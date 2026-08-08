from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WrapperContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wrapper_id: str
    option_lists: dict[str, tuple[str, ...]] = Field(default_factory=dict)


class DressingCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    declared_wrapper_ids: tuple[str, ...] = Field(default_factory=tuple)
    authored_packs: dict[str, WrapperContent] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_catalog(self) -> "DressingCatalog":
        declared = self.declared_wrapper_ids
        if len(declared) != len(set(declared)):
            msg = "declared_wrapper_ids must be unique"
            raise ValueError(msg)
        undeclared = sorted(set(self.authored_packs) - set(declared))
        if undeclared:
            msg = f"authored_packs contain undeclared wrapper ids: {', '.join(undeclared)}"
            raise ValueError(msg)
        for wrapper_id, content in self.authored_packs.items():
            if content.wrapper_id != wrapper_id:
                msg = f"authored pack key {wrapper_id!r} must match wrapper_id"
                raise ValueError(msg)
        return self


class DressingRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arc_id_prefix: str
    pack_path: str


class DressingRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registrations: tuple[DressingRegistration, ...]

    @model_validator(mode="after")
    def validate_registry(self) -> "DressingRegistry":
        if not self.registrations:
            msg = "registrations must not be empty"
            raise ValueError(msg)
        return self
