from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    local = "local"
    dev = "dev"
    prod = "prod"


class ValidationSettings(BaseModel):
    nric_regex: str = r"^[STFG]\d{7}[A-Z]$"
    postal_code_regex: str = r"^\d{6}$"


class PathSettings(BaseModel):
    input: str = "test_data/individual_tax_returns.csv"
    logging_config: str = "configs/logging.yaml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
    )

    env: Environment = Field(default=Environment.local)
    assessment_year: int = 2023

    validation: ValidationSettings = Field(default_factory=ValidationSettings)

    paths: PathSettings = Field(default_factory=PathSettings)

    @classmethod
    def load(cls, yaml_path: str | Path = "configs/config.yaml") -> "Settings":
        """
        Loads settings from YAML file, overridden by env vars
        Example:
            - Env var override yaml for NRIC regex
            export VALIDATION__NRIC=[abc]123[abc]
        """
        yaml_path = Path(yaml_path)
        if yaml_path.exists():
            with yaml_path.open("r") as f:
                yaml_data = yaml.safe_load(f) or {}
        else:
            yaml_data = {}

        return cls(**yaml_data)


def load_settings(config_path: str = "configs/config.yaml") -> Settings:
    return Settings.load(config_path)


settings = load_settings()
