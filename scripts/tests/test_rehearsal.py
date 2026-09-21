"""Contract tests for the rehearsal stack launcher.

`scripts/rehearsal.py` boots the local stack, so most of it needs Docker, a
database and a tunnel. The pure parts below are the ones that decide whether a
rehearsal starts at all, or starts pointing at the wrong place, so they are the
parts worth pinning.
"""

import json
import socket
import urllib.parse

import pytest

from scripts import rehearsal


@pytest.fixture(autouse=True)
def _isolate_repo_paths(monkeypatch, tmp_path):
    """Keep every test off the real .env, .env.example and routing table."""
    monkeypatch.setattr(rehearsal, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(rehearsal, "SHARED_ENV_FILE", tmp_path / "shared" / ".env")
    monkeypatch.setattr(rehearsal, "ENV_EXAMPLE", tmp_path / ".env.example")
    monkeypatch.setattr(rehearsal, "ROUTING_TABLE", tmp_path / "routing_table.json")
    monkeypatch.setattr(rehearsal, "children", [])


def write_routing_table(path, table):
    path.write_text(json.dumps(table), encoding="utf-8")


def complete_env_text(**overrides):
    values = {key: "set" for key in rehearsal.REQUIRED_KEYS}
    values.update(overrides)
    return "\n".join(f"{key}={value}" for key, value in values.items())


class TestRequiredProviderKeys:
    """Rule 8: provider names live in the routing table, not in this script."""

    def test_derives_one_key_per_provider_in_the_routing_table(self):
        write_routing_table(
            rehearsal.ROUTING_TABLE,
            {
                "generation": {"premium": "vendorb/big-model", "cheap": "vendora/x"},
                "classification": {"cheap": "vendora/y"},
            },
        )
        assert rehearsal.required_provider_keys() == [
            "VENDORA_API_KEY",
            "VENDORB_API_KEY",
        ]

    def test_a_new_provider_in_the_table_becomes_a_new_required_key(self):
        """The reason this function exists: adding a provider must not need an
        edit here. If someone hardcodes the provider list, this goes red."""
        write_routing_table(
            rehearsal.ROUTING_TABLE, {"generation": {"cheap": "vendora/x"}}
        )
        before = rehearsal.required_provider_keys()
        write_routing_table(
            rehearsal.ROUTING_TABLE,
            {"generation": {"cheap": "vendora/x", "premium": "newcomer/z"}},
        )
        after = rehearsal.required_provider_keys()
        assert set(after) - set(before) == {"NEWCOMER_API_KEY"}

    def test_ignores_bare_model_names_that_carry_no_provider(self):
        write_routing_table(
            rehearsal.ROUTING_TABLE,
            {"generation": {"cheap": "no-slash-here", "premium": "vendora/x"}},
        )
        assert rehearsal.required_provider_keys() == ["VENDORA_API_KEY"]

    def test_absent_routing_table_requires_no_provider_keys(self):
        assert not rehearsal.ROUTING_TABLE.exists()
        assert rehearsal.required_provider_keys() == []


class TestReadEnv:
    def test_blank_required_key_stops_the_rehearsal(self):
        """A blank value is the failure mode this catches: the key is present,
        so a naive membership check would pass and the stack would boot broken."""
        write_routing_table(rehearsal.ROUTING_TABLE, {})
        rehearsal.ENV_FILE.write_text(
            complete_env_text(FIREBASE_WEB_API_KEY=""), encoding="utf-8"
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal.read_env()
        assert exc.value.code == 1

    def test_missing_provider_key_stops_the_rehearsal(self, capsys):
        write_routing_table(
            rehearsal.ROUTING_TABLE, {"generation": {"cheap": "vendora/x"}}
        )
        rehearsal.ENV_FILE.write_text(complete_env_text(), encoding="utf-8")
        with pytest.raises(SystemExit):
            rehearsal.read_env()
        assert "VENDORA_API_KEY" in capsys.readouterr().err

    def test_complete_env_parses_and_returns_values(self):
        write_routing_table(rehearsal.ROUTING_TABLE, {})
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

    def test_seeds_env_from_example_when_absent(self):
        write_routing_table(rehearsal.ROUTING_TABLE, {})
        rehearsal.ENV_EXAMPLE.write_text(complete_env_text(), encoding="utf-8")
        assert not rehearsal.ENV_FILE.exists()
        env = rehearsal.read_env()
        assert rehearsal.ENV_FILE.exists()
        assert env["POSTGRES_DB"] == "set"

    def test_prefers_the_shared_env_over_the_example(self):
        write_routing_table(rehearsal.ROUTING_TABLE, {})
        rehearsal.SHARED_ENV_FILE.parent.mkdir(parents=True)
        rehearsal.SHARED_ENV_FILE.write_text(
            complete_env_text(POSTGRES_DB="from-shared"), encoding="utf-8"
        )
        rehearsal.ENV_EXAMPLE.write_text(
            complete_env_text(POSTGRES_DB="from-example"), encoding="utf-8"
        )
        assert rehearsal.read_env()["POSTGRES_DB"] == "from-shared"

    def test_no_env_and_no_example_fails(self):
        write_routing_table(rehearsal.ROUTING_TABLE, {})
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
