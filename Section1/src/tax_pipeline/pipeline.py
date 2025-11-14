import json
import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError

from . import transforms as T
from .data_quality import dq_score
from .io.utils import ensure_dir, write_csv, write_parquet
from .schema import TaxReturn
from .settings import Settings
from .validators import (
    validate_chargeable,
    validate_cpf_residency,
    validate_filing_date,
    validate_nric,
    validate_postal,
)

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings

    def run(self) -> None:
        input_path = self.settings.paths.input
        logger.info(
            "Starting pipeline run", extra={"input_path": str(input_path)}
        )

        df_raw = pd.read_csv(input_path)
        logger.info("Loaded raw data", extra={"rows": len(df_raw)})

        df_parsed, parsing_errors = self.parse_df(df_raw, schema=TaxReturn)
        df_parsed["parsing_errors"] = parsing_errors

        df = T.standardize(df_raw)
        logger.info("Standardized data frame")

        self._ensure_dirs()

        df_with_dq = self._apply_dq(df)
        self._write_dq_artifacts(df_with_dq)

        dims = T.build_dims_and_fact(df_with_dq)
        self._write_curated(*dims)

    def _ensure_dirs(self) -> None:
        ensure_dir(self.settings.paths.landing_dir)
        ensure_dir(self.settings.paths.curated_dir)
        ensure_dir(self.settings.paths.dq_dir)

    def parse_df(
        self, df: pd.DataFrame, schema: type[BaseModel]
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Try to parse each row into a pydantic schema.
        - Returns a DataFrame of parsed records (as dicts)
        - And a Series of error messages (or None) per row.
        """
        parsed_records: list[dict[str, Any]] = []
        errors: list[Optional[str]] = []

        # Ensure we have dict-like rows
        for _, row in df.iterrows():
            raw = row.to_dict()
            try:
                model = schema.model_validate(raw)
                parsed_records.append(model.model_dump())
                errors.append(None)
            except ValidationError as e:
                parsed_records.append(raw)
                errors.append(str(e))

        parsed_df = pd.DataFrame(parsed_records)
        error_series = pd.Series(errors, name="pydantic_error")

        return parsed_df, error_series

    def _apply_dq(self, df: pd.DataFrame) -> pd.DataFrame:
        s = self.settings
        v = s.validation
        w = s.dq_weights.model_dump()

        flags = pd.DataFrame(
            {
                "nric_valid": df.get("nric", pd.Series([None] * len(df))).apply(
                    lambda x: validate_nric(x, v.nric_regex)
                ),
                "postal_valid": df.get(
                    "postal_code", pd.Series([None] * len(df))
                ).apply(lambda x: validate_postal(x, v.postal_code_regex)),
                "filing_date_valid": df.apply(
                    lambda r: validate_filing_date(
                        r.get("filing_date"),
                        r.get("assessment_year", s.assessment_year),
                        v.filing_date_after_ay,
                    ),
                    axis=1,
                ),
                "chargeable_calc_valid": df.apply(
                    lambda r: validate_chargeable(
                        r.get("annual_income_sgd"),
                        r.get("total_reliefs_sgd"),
                        r.get("chargeable_income_sgd"),
                        v.allow_negative_chargeable_income,
                    ),
                    axis=1,
                ),
                "cpf_residency_valid": df.apply(
                    lambda r: validate_cpf_residency(
                        r.get("cpf_contributions_sgd"),
                        r.get("residential_status"),
                        v.cpf_only_for_residents,
                    ),
                    axis=1,
                ),
            }
        )

        df_out = df.copy()
        df_out["dq_score"] = flags.apply(
            lambda row: dq_score(row.to_dict(), w),
            axis=1,
        )

        for col in flags.columns:
            df_out[col] = flags[col]

        return df_out

    def _write_dq_artifacts(self, df: pd.DataFrame) -> None:
        dq_dir = Path(self.settings.paths.dq_dir)
        report_path = dq_dir / "dq_report.csv"
        summary_path = dq_dir / "dq_summary.json"

        dq_report_cols = [
            col
            for col in [
                "taxpayer_id",
                "nric",
                "assessment_year",
                "dq_score",
                "nric_valid",
                "postal_valid",
                "filing_date_valid",
                "chargeable_calc_valid",
                "cpf_residency_valid",
            ]
            if col in df.columns
        ]

        write_csv(df[dq_report_cols], report_path)

        summary = {
            "records": int(len(df)),
            "avg_dq": float(
                df["dq_score"].mean() if "dq_score" in df.columns else 0.0
            ),
            "pct_valid_nric": float(df["nric_valid"].mean()),
            "pct_valid_postal": float(df["postal_valid"].mean()),
            "pct_valid_filing_date": float(df["filing_date_valid"].mean()),
            "pct_valid_chargeable": float(df["chargeable_calc_valid"].mean()),
            "pct_valid_cpf_residency": float(df["cpf_residency_valid"].mean()),
        }

        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2))

    def _write_curated(
        self,
        dim_taxpayer: pd.DataFrame,
        dim_time: pd.DataFrame,
        dim_location: pd.DataFrame,
        dim_occupation: pd.DataFrame,
        fact: pd.DataFrame,
    ) -> None:
        curated_dir = Path(self.settings.paths.curated_dir)
        write_parquet(dim_taxpayer, curated_dir / "dim_taxpayer.parquet")
        write_parquet(dim_time, curated_dir / "dim_time.parquet")
        write_parquet(dim_location, curated_dir / "dim_location.parquet")
        write_parquet(dim_occupation, curated_dir / "dim_occupation.parquet")
        write_parquet(fact, curated_dir / "fact_tax_returns.parquet")
