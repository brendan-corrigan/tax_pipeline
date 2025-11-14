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
    postal_code_regex: str = r"^[0-9]{6}$"
    filing_date_after_ay: bool = True
    cpf_only_for_residents: bool = True
    allow_negative_chargeable_income: bool = False


class DQWeights(BaseModel):
    nric_valid: float = 0.2
    postal_valid: float = 0.1
    filing_date_valid: float = 0.2
    chargeable_calc_valid: float = 0.3
    cpf_residency_valid: float = 0.2


class PathSettings(BaseModel):
    input: str = "test_data/individual_tax_returns.csv"
    output: str = "artifacts"
    logging_config: str = "configs/logging.yaml"
    curated_dir: str = "artifacts/curated"
    dq_dir: str = "artifacts"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
    )

    env: Environment = Field(default=Environment.local)
    assessment_year: int = 2023

    validation: ValidationSettings = Field(default_factory=ValidationSettings)

    paths: PathSettings = Field(default_factory=PathSettings)

    dq_weights: DQWeights = Field(default_factory=DQWeights)

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
