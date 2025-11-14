import pandas as pd


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "postal_code" in out.columns:
        out["postal_code"] = (
            out["postal_code"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(6)
        )

    # Coerce numeric columns if present
    for col in [
        "annual_income_sgd",
        "chargeable_income_sgd",
        "tax_payable_sgd",
        "tax_paid_sgd",
        "total_reliefs_sgd",
        "cpf_contributions_sgd",
        "foreign_income_sgd",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Coerce dates
    if "filing_date" in out.columns:
        out["filing_date"] = pd.to_datetime(out["filing_date"], errors="coerce")

    return out


def build_dims_and_fact(df: pd.DataFrame) -> tuple[pd.DataFrame, ...]:
    # Taxpayer dim
    taxpayer_cols = [
        "taxpayer_id",
        "nric",
        "full_name",
        "filing_status",
        "residential_status",
        "number_of_dependents",
    ]
    dim_taxpayer = df[taxpayer_cols].drop_duplicates().reset_index(drop=True)
    dim_taxpayer["taxpayer_sk"] = dim_taxpayer.index + 1

    # Time dim
    dim_time = (
        df[["filing_date", "assessment_year"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_time["date"] = dim_time["filing_date"]
    dim_time["year"] = dim_time["date"].dt.year
    dim_time["quarter"] = dim_time["date"].dt.quarter
    dim_time["month"] = dim_time["date"].dt.month
    dim_time["day"] = dim_time["date"].dt.day
    dim_time["date_key"] = (
        dim_time["date"].dt.strftime("%Y%m%d").astype("Int64")
    )
    dim_time["is_filing_date"] = True
    dim_time["time_sk"] = dim_time.index + 1

    # Location dim
    loc_cols = ["postal_code", "housing_type"]
    dim_location = df[loc_cols].drop_duplicates().reset_index(drop=True)
    dim_location["location_sk"] = dim_location.index + 1

    # Occupation dim
    occ_cols = ["occupation"]
    dim_occupation = df[occ_cols].drop_duplicates().reset_index(drop=True)
    dim_occupation["occupation_sk"] = dim_occupation.index + 1

    # Build fact
    fact = (
        df.merge(dim_taxpayer, on=taxpayer_cols, how="left")
        .merge(
            dim_time,
            left_on=["filing_date", "assessment_year"],
            right_on=["date", "assessment_year"],
            how="left",
        )
        .merge(dim_location, on=loc_cols, how="left")
        .merge(dim_occupation, on=occ_cols, how="left")
    )

    fact_out = fact[
        [
            "taxpayer_sk",
            "time_sk",
            "location_sk",
            "occupation_sk",
            "assessment_year",
            "annual_income_sgd",
            "total_reliefs_sgd",
            "chargeable_income_sgd",
            "tax_payable_sgd",
            "tax_paid_sgd",
            "cpf_contributions_sgd",
            "foreign_income_sgd",
            "dq_score",
        ]
    ].copy()

    fact_out = fact_out.reset_index().rename(columns={"index": "fact_id"})
    fact_out["fact_id"] = fact_out["fact_id"] + 1

    return dim_taxpayer, dim_time, dim_location, dim_occupation, fact_out
