import logging
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError

from .schema import TaxReturn
from .settings import Settings

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        # self.outdir = Path(outdir)

    def run(self) -> None:
        input_path = self.settings.paths.input
        logger.info(
            "Starting pipeline run", extra={"input_path": str(input_path)}
        )

        df_raw = pd.read_csv(input_path)
        logger.info("Loaded raw data", extra={"rows": len(df_raw)})

        df_parsed, parsing_errors = self.parse_df(df_raw, schema=TaxReturn)
        df_parsed["parsing_errors"] = parsing_errors
        df_parsed.to_csv("parsed.csv")

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
