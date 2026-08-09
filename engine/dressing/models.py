from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DressingPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wrapper_id: str
    authored: bool = False
    drinks: tuple[str, ...] = Field(default_factory=tuple)
    stage_name_templates: tuple[str, ...] = Field(default_factory=tuple)


class DressingCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    declared_wrapper_ids: tuple[str, ...] = Field(default_factory=tuple)
    wrappers: dict[str, DressingPack]

    @model_validator(mode="after")
    def validate_catalog(self) -> "DressingCatalog":
        declared = self.declared_wrapper_ids
        if len(declared) != len(set(declared)):
            msg = "declared_wrapper_ids must be unique"
            raise ValueError(msg)
        undeclared = sorted(set(self.wrappers) - set(declared))
        if undeclared:
            msg = f"wrappers contain undeclared wrapper ids: {', '.join(undeclared)}"
            raise ValueError(msg)
        for wrapper_id, pack in self.wrappers.items():
            if pack.wrapper_id != wrapper_id:
                msg = f"wrapper key {wrapper_id!r} must match wrapper_id"
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
