from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import ValidationError

from ..schema import TaxReturn


def parse_tax_returns_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Try to parse each row into a TaxReturn.
    - Returns a DataFrame of parsed records (as dicts)
    - And a Series of error messages (or None) per row.
    """
    parsed_records: List[Dict[str, Any]] = []
    errors: List[Optional[str]] = []

    for _, row in df.iterrows():
        raw = row.to_dict()
        try:
            model = TaxReturn.model_validate(raw)
            parsed_records.append(model.model_dump())
            errors.append(None)
        except ValidationError as e:
            # Soft failure: keep raw row, but record the error message
            parsed_records.append(raw)
            errors.append(str(e))

    parsed_df = pd.DataFrame(parsed_records)
    error_series = pd.Series(errors, name="pydantic_error")

    return parsed_df, error_series
