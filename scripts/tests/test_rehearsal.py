"""Contract tests for the rehearsal stack launcher.

`scripts/rehearsal.py` boots the local stack, so most of it needs Docker, a
database and a tunnel. The pure parts below are the ones that decide whether a
rehearsal starts at all, or starts pointing at the wrong place, so they are the
parts worth pinning.
"""

import builtins
import re
import socket
import sys
import types
import urllib.parse
from pathlib import Path

import pytest

from scripts import rehearsal

REPO_ROOT = Path(__file__).resolve().parents[2]
# No trailing \b: the leak to catch is `ANTHROPIC_API_KEY`, and `_` is a word
# character, so a closing boundary would step straight over it.
PROVIDER_NAME = re.compile(
    r"\b(?:anthropic|groq|openai|cohere|mistral|bedrock|vertex)", re.IGNORECASE
)

# What the routing layer reports for the committed routing table. Stubbed in
# most tests so they exercise rehearsal.py's own handling rather than the
# router, and so they do not pay the LLM SDK import.
CREDENTIALS = [
    ("ANTHROPIC_API_KEY", "PRIMARY_LLM_API_KEY"),
    ("GROQ_API_KEY", "SECONDARY_LLM_API_KEY"),
]


@pytest.fixture(autouse=True)
def _isolate_repo_paths(monkeypatch, tmp_path):
    """Keep every test off the real .env and .env.example."""
    monkeypatch.setattr(rehearsal, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(rehearsal, "SHARED_ENV_FILE", tmp_path / "shared" / ".env")
    monkeypatch.setattr(rehearsal, "ENV_EXAMPLE", tmp_path / ".env.example")
    monkeypatch.setattr(rehearsal, "children", [])


@pytest.fixture
def credentials(monkeypatch):
    """Stand in for the routing layer with the real committed requirements."""
    monkeypatch.setattr(
        rehearsal, "required_credential_env_vars", lambda: list(CREDENTIALS)
    )


def complete_env_text(**overrides):
    values = {key: "set" for key in rehearsal.REQUIRED_KEYS}
    values.update({name: "set" for name, _ in CREDENTIALS})
    values.update(overrides)
    return "\n".join(f"{key}={value}" for key, value in values.items() if value)


class TestRequiredCredentialEnvVars:
    """Rule 8: this script holds no provider names and derives nothing. It asks
    the routing layer, which owns the one mapping."""

    def test_returns_what_the_routing_layer_reports(self, monkeypatch):
        monkeypatch.setattr(
            rehearsal.sys, "path", [str(REPO_ROOT), *rehearsal.sys.path]
        )
        assert rehearsal.required_credential_env_vars() == [
            ("ANTHROPIC_API_KEY", "PRIMARY_LLM_API_KEY"),
            ("GROQ_API_KEY", "SECONDARY_LLM_API_KEY"),
        ]

    def test_this_script_names_no_provider(self):
        """The check `scripts/checks/provider_leak_check.py` does not scan
        scripts/, so nothing else stops a provider name reappearing here."""
        source = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(encoding="utf-8")
        assert not PROVIDER_NAME.search(source), PROVIDER_NAME.search(source)

    def test_an_unmapped_provider_points_at_the_file_to_edit(self, monkeypatch, capsys):
        def raise_unmapped():
            raise ValueError(
                "routing table uses provider 'newcomer', which has no "
                "credential entry in router.py"
            )

        monkeypatch.setitem(
            sys.modules,
            "engine.routing.router",
            types.SimpleNamespace(required_credential_env_vars=raise_unmapped),
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal.required_credential_env_vars()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "newcomer" in err
        assert "engine/routing/router.py" in err

    def test_an_unimportable_routing_layer_fails_with_an_install_hint(
        self, monkeypatch, capsys
    ):
        """The rehearsal must not die on a bare ImportError traceback when the
        dependencies are simply not installed yet."""
        real_import = builtins.__import__

        def refuse(name, *args, **kwargs):
            if name == "engine.routing.router":
                raise ModuleNotFoundError("No module named 'litellm'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setitem(sys.modules, "engine.routing.router", None)
        monkeypatch.delitem(sys.modules, "engine.routing.router")
        monkeypatch.setattr(builtins, "__import__", refuse)
        with pytest.raises(SystemExit) as exc:
            rehearsal.required_credential_env_vars()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "litellm" in err
        assert "pip install -r requirements.txt" in err


class TestReadEnv:
    def test_blank_required_key_stops_the_rehearsal(self, credentials):
        """A blank value is the failure mode this catches: the key is present,
        so a naive membership check would pass and the stack would boot broken."""
        rehearsal.ENV_FILE.write_text(
            complete_env_text(FIREBASE_WEB_API_KEY=""), encoding="utf-8"
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal.read_env()
        assert exc.value.code == 1

    def test_a_blank_llm_credential_stops_the_rehearsal(self, credentials, capsys):
        rehearsal.ENV_FILE.write_text(
            complete_env_text(ANTHROPIC_API_KEY=""), encoding="utf-8"
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal.read_env()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "ANTHROPIC_API_KEY or PRIMARY_LLM_API_KEY" in err
        assert "GROQ_API_KEY" not in err

    def test_the_neutral_deploy_slot_satisfies_a_provider_credential(self, credentials):
        """Deploy binds PRIMARY_LLM_API_KEY / SECONDARY_LLM_API_KEY and the
        router hydrates the provider vars from them at runtime. A .env written
        that way must boot locally too, or the cloud runbook's setup is
        rejected by the local preflight."""
        values = {key: "set" for key in rehearsal.REQUIRED_KEYS}
        values["PRIMARY_LLM_API_KEY"] = "primary-secret"
        values["SECONDARY_LLM_API_KEY"] = "secondary-secret"
        rehearsal.ENV_FILE.write_text(
            "\n".join(f"{k}={v}" for k, v in values.items()), encoding="utf-8"
        )
        env = rehearsal.read_env()
        assert env["PRIMARY_LLM_API_KEY"] == "primary-secret"
        assert "ANTHROPIC_API_KEY" not in env

    def test_neither_the_provider_var_nor_its_slot_fails(self, credentials, capsys):
        values = {key: "set" for key in rehearsal.REQUIRED_KEYS}
        rehearsal.ENV_FILE.write_text(
            "\n".join(f"{k}={v}" for k, v in values.items()), encoding="utf-8"
        )
        with pytest.raises(SystemExit):
            rehearsal.read_env()
        err = capsys.readouterr().err
        assert "ANTHROPIC_API_KEY or PRIMARY_LLM_API_KEY" in err
        assert "GROQ_API_KEY or SECONDARY_LLM_API_KEY" in err

    def test_infrastructure_keys_are_checked_before_the_routing_layer_loads(
        self, monkeypatch, capsys
    ):
        """Loading the router costs seconds. A missing Postgres password is the
        common failure and must still report immediately."""
        loaded = []

        def record_and_return():
            loaded.append(True)
            return list(CREDENTIALS)

        monkeypatch.setattr(
            rehearsal, "required_credential_env_vars", record_and_return
        )
        rehearsal.ENV_FILE.write_text(
            complete_env_text(POSTGRES_PASSWORD=""), encoding="utf-8"
        )
        with pytest.raises(SystemExit):
            rehearsal.read_env()
        assert "POSTGRES_PASSWORD" in capsys.readouterr().err
        assert loaded == [], "routing layer was loaded before the cheap checks failed"

    def test_complete_env_parses_and_returns_values(self, credentials):
        rehearsal.ENV_FILE.write_text(
            "# a comment\n"
            "\n"
            "not_a_pair_line\n"
            "PASSWORD_WITH_EQUALS=a=b=c\n"
            "  SPACED_KEY =  spaced-value  \n" + complete_env_text(),
            encoding="utf-8",
        )
        env = rehearsal.read_env()
        assert env["PASSWORD_WITH_EQUALS"] == "a=b=c"
        assert env["SPACED_KEY"] == "spaced-value"
        assert "not_a_pair_line" not in env
        assert "# a comment" not in env

    def test_seeds_env_from_example_when_absent(self, credentials):
        rehearsal.ENV_EXAMPLE.write_text(complete_env_text(), encoding="utf-8")
        assert not rehearsal.ENV_FILE.exists()
        env = rehearsal.read_env()
        assert rehearsal.ENV_FILE.exists()
        assert env["POSTGRES_DB"] == "set"

    def test_prefers_the_shared_env_over_the_example(self, credentials):
        rehearsal.SHARED_ENV_FILE.parent.mkdir(parents=True)
        rehearsal.SHARED_ENV_FILE.write_text(
            complete_env_text(POSTGRES_DB="from-shared"), encoding="utf-8"
        )
        rehearsal.ENV_EXAMPLE.write_text(
            complete_env_text(POSTGRES_DB="from-example"), encoding="utf-8"
        )
        assert rehearsal.read_env()["POSTGRES_DB"] == "from-shared"

    def test_no_env_and_no_example_fails(self, credentials):
        with pytest.raises(SystemExit):
            rehearsal.read_env()


class TestBuildDisplayUrl:
    def test_host_token_stays_in_the_fragment(self):
        """The fragment is never sent to a server. If the host token migrates
        into the query string it leaks to the dashboard origin's access logs."""
        url = rehearsal.build_display_url(
            session_id="sess-1",
            host_token="secret-host-token",
            tunnel_url="https://demo.trycloudflare.com",
        )
        assert "#" in url, f"host token is not in a fragment at all: {url}"
        query = url.split("?", 1)[1].split("#", 1)[0]
        fragment = url.split("#", 1)[1]
        assert "secret-host-token" not in query, f"host token leaked to query: {query}"
        assert "secret-host-token" in fragment

    def test_join_base_url_is_encoded_into_the_query(self):
        url = rehearsal.build_display_url(
            session_id="sess-1",
            host_token="t",
            tunnel_url="https://demo.trycloudflare.com",
        )
        query = urllib.parse.parse_qs(url.split("?", 1)[1].split("#", 1)[0])
        assert query["join_base_url"] == ["https://demo.trycloudflare.com"]
        assert url.startswith(f"http://127.0.0.1:{rehearsal.WEB_PORT}/display/sess-1?")


class TestEnsurePortAvailable:
    def test_fails_when_the_port_is_already_taken(self, capsys):
        """Without this guard the rehearsal boots a second API against a port
        it does not own, and the display talks to the stale process."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as holder:
            holder.bind(("0.0.0.0", 0))
            holder.listen()
            port = holder.getsockname()[1]
            with pytest.raises(SystemExit) as exc:
                rehearsal.ensure_port_available("API", port)
        assert exc.value.code == 1
        assert f"port {port} is already in use" in capsys.readouterr().err

    def test_passes_on_a_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("0.0.0.0", 0))
            port = probe.getsockname()[1]
        rehearsal.ensure_port_available("API", port)


class FakeStdout:
    def __init__(self, lines):
        self._lines = list(lines)

    def readline(self):
        return self._lines.pop(0) if self._lines else ""


class FakeProcess:
    def __init__(self, lines):
        self.stdout = FakeStdout(lines)


class TestWaitForTunnelUrl:
    def test_picks_the_tunnel_url_out_of_noisy_cloudflared_output(self):
        proc = FakeProcess(
            [
                "INF Thank you for trying Cloudflare Tunnel.\n",
                "INF +-------------------------------------+\n",
                "INF | https://odd-pine-1234.trycloudflare.com |\n",
                "INF +-------------------------------------+\n",
            ]
        )
        assert (
            rehearsal.wait_for_tunnel_url(proc)
            == "https://odd-pine-1234.trycloudflare.com"
        )

    def test_ignores_non_tunnel_urls(self):
        proc = FakeProcess(
            [
                "INF connecting to https://api.cloudflare.com/client/v4\n",
                "INF url=https://real-one-99.trycloudflare.com\n",
            ]
        )
        assert (
            rehearsal.wait_for_tunnel_url(proc)
            == "https://real-one-99.trycloudflare.com"
        )


class DummyChild:
    def __init__(self, alive=True):
        self._alive = alive
        self.terminated = False
        self.returncode = None

    def poll(self):
        return None if self._alive else 0

    def terminate(self):
        self.terminated = True
        self._alive = False

    def wait(self, timeout=None):
        return 0

    def kill(self):
        pass


class TestTeardown:
    def test_terminates_every_live_child(self, monkeypatch):
        live, already_gone = DummyChild(), DummyChild(alive=False)
        monkeypatch.setattr(rehearsal, "children", [live, already_gone])
        rehearsal.teardown()
        assert live.terminated
        assert not already_gone.terminated
