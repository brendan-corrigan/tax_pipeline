import pandas as pd
import re
from datetime import datetime
import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "dq_rules.yaml"
DATA_PATH = BASE_DIR / "test_data" / "grant_applications.csv"


def parse_ddmmyyyy(date_str: str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except Exception:
        return None


def parse_yyyymmdd(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df


def rule_application_id_not_null(row: pd.Series) -> bool:
    return pd.notnull(row["application_id"])


def rule_citizen_nric_not_null(row: pd.Series) -> bool:
    return pd.notnull(row["citizen_nric"])


def rule_grant_scheme_name_not_null(row: pd.Series) -> bool:
    return pd.notnull(row["grant_scheme_name"])


def rule_household_income_not_null(row: pd.Series) -> bool:
    return pd.notnull(row["household_income"])


def rule_application_id_unique(df: pd.DataFrame) -> pd.Series:
    return ~df["application_id"].duplicated(keep=False)


def rule_citizen_nric_format(row: pd.Series) -> bool:
    value = row["citizen_nric"]
    if pd.isnull(value):
        return False
    return bool(re.match(r"^[STFG]\d{7}[A-Z]$", str(value)))


def rule_household_income_non_negative(row: pd.Series) -> bool:
    value = row["household_income"]
    if pd.isnull(value):
        return False
    return value >= 0


def rule_household_size_positive(row: pd.Series) -> bool:
    value = row["household_size"]
    if pd.isnull(value):
        return False
    try:
        return int(value) >= 1
    except Exception:
        return False


def rule_requested_amount_non_negative(row: pd.Series) -> bool:
    value = row["requested_amount"]
    if pd.isnull(value):
        return False
    return value >= 0


def rule_approved_amount_non_negative_or_null(row: pd.Series) -> bool:
    value = row["approved_amount"]
    if pd.isnull(value):
        return True
    return value >= 0


def rule_application_date_not_in_future(row: pd.Series) -> bool:
    value = row["application_date"]
    parsed = parse_ddmmyyyy(str(value))
    if parsed is None:
        return False
    return parsed <= datetime.now()


def rule_application_status_allowed_values(row: pd.Series) -> bool:
    allowed = {"Pending", "Approved", "Rejected"}
    value = row["application_status"]
    if pd.isnull(value):
        return False
    return str(value) in allowed


def rule_application_date_format_ddmmyyyy(row: pd.Series) -> bool:
    value = row["application_date"]
    return parse_ddmmyyyy(str(value)) is not None


def rule_decision_date_format_yyyymmdd(row: pd.Series) -> bool:
    value = row["decision_date"]
    if pd.isnull(value):
        return False
    return parse_yyyymmdd(str(value)) is not None


def rule_decision_date_not_before_application_date(row: pd.Series) -> bool:
    app_raw = row["application_date"]
    dec_raw = row["decision_date"]
    app = parse_ddmmyyyy(str(app_raw))
    dec = parse_yyyymmdd(str(dec_raw))
    if app is None or dec is None:
        return False
    return dec >= app


def rule_approved_amount_null_status_mapping(row: pd.Series) -> bool:
    status = row["application_status"]
    approved = row["approved_amount"]
    if status == "Approved":
        return pd.notnull(approved)
    if status in {"Pending", "Rejected"}:
        return pd.isnull(approved)
    return False


def rule_decision_date_within_6_months(row: pd.Series) -> bool:
    app_raw = row["application_date"]
    dec_raw = row["decision_date"]
    app = parse_ddmmyyyy(str(app_raw))
    dec = parse_yyyymmdd(str(dec_raw))
    if app is None or dec is None:
        return False
    delta = dec - app
    return 0 <= delta.days <= 183


def rule_decision_date_not_in_future(row: pd.Series) -> bool:
    value = row["decision_date"]
    parsed = parse_yyyymmdd(str(value))
    if parsed is None:
        return False
    return parsed <= datetime.now()


RULE_FUNCTIONS_ROW = {
    "application_id_not_null": rule_application_id_not_null,
    "citizen_nric_not_null": rule_citizen_nric_not_null,
    "grant_scheme_name_not_null": rule_grant_scheme_name_not_null,
    "household_income_not_null": rule_household_income_not_null,
    "citizen_nric_format": rule_citizen_nric_format,
    "household_income_non_negative": rule_household_income_non_negative,
    "household_size_positive": rule_household_size_positive,
    "requested_amount_non_negative": rule_requested_amount_non_negative,
    "approved_amount_non_negative_or_null": rule_approved_amount_non_negative_or_null,
    "application_date_not_in_future": rule_application_date_not_in_future,
    "application_status_allowed_values": rule_application_status_allowed_values,
    "application_date_format_ddmmyyyy": rule_application_date_format_ddmmyyyy,
    "decision_date_format_yyyymmdd": rule_decision_date_format_yyyymmdd,
    "decision_date_not_before_application_date": rule_decision_date_not_before_application_date,
    "approved_amount_null_status_mapping": rule_approved_amount_null_status_mapping,
    "decision_date_within_6_months": rule_decision_date_within_6_months,
    "decision_date_not_in_future": rule_decision_date_not_in_future,
}


def run_rules(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    total_rows = len(df)
    rule_results = {}

    for rule in config["rules"]:
        rule_id = rule["id"]
        level = rule["level"]
        if level == "row":
            func = RULE_FUNCTIONS_ROW[rule_id]
            mask = df.apply(func, axis=1)
        elif level == "dataset":
            if rule_id == "application_id_unique":
                unique_mask = rule_application_id_unique(df)
                mask = unique_mask
            else:
                raise ValueError(f"Unsupported dataset-level rule: {rule_id}")
        else:
            raise ValueError(f"Unknown rule level: {level}")

        rule_results[rule_id] = mask

    rule_results_df = pd.DataFrame(rule_results)
    rule_results_df.index = df.index

    return rule_results_df, total_rows


def compute_dimension_scores(rule_results_df: pd.DataFrame, config: dict, total_rows: int) -> pd.DataFrame:
    rule_to_dimension = {r["id"]: r["dimension"] for r in config["rules"]}
    dimension_rule_ids = {}
    for rule_id, dimension in rule_to_dimension.items():
        dimension_rule_ids.setdefault(dimension, []).append(rule_id)

    records = []
    for dimension, rule_ids in dimension_rule_ids.items():
        subset = rule_results_df[rule_ids]
        if subset.empty:
            passed_rows = 0
        else:
            per_row_pass_all = subset.all(axis=1)
            passed_rows = int(per_row_pass_all.sum())
        failed_rows = total_rows - passed_rows
        score = (passed_rows / total_rows * 100) if total_rows > 0 else 0.0
        records.append(
            {
                "dimension_name": dimension,
                "score": round(score, 2),
                "passed_rows": passed_rows,
                "failed_rows": failed_rows,
                "total_rows": total_rows,
            }
        )

    return pd.DataFrame(records).sort_values("dimension_name").reset_index(drop=True)


def main():
    config = load_config()
    df = load_data()
    rule_results_df, total_rows = run_rules(df, config)
    scores_df = compute_dimension_scores(rule_results_df, config, total_rows)
    print(scores_df)
    output_path = BASE_DIR / "dq_dimension_scores.csv"
    scores_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
