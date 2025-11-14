import re
from datetime import date
from typing import Optional


def validate_nric(nric: Optional[str], pattern: str) -> bool:
    if not nric:
        return False
    return re.match(pattern, str(nric)) is not None


def validate_postal(postal: Optional[str], pattern: str) -> bool:
    if not postal:
        return False
    return re.match(pattern, str(postal)) is not None


def validate_filing_date(
    filing_date: Optional[date],
    assessment_year: Optional[int],
    require_gte: bool = True,
) -> bool:
    if filing_date is None or assessment_year is None:
        return False
    year = filing_date.year
    return year >= assessment_year if require_gte else True


def validate_chargeable(
    annual_income: Optional[float],
    reliefs: Optional[float],
    chargeable: Optional[float],
    allow_negative: bool = False,
) -> bool:
    if annual_income is None or reliefs is None or chargeable is None:
        return False
    expected = annual_income - reliefs
    if not allow_negative and expected < 0:
        expected = 0.0
    return abs(chargeable - expected) < 1e-2


def validate_cpf_residency(
    cpf_contrib: Optional[float],
    residency_status: Optional[str],
    cpf_only_for_residents: bool = True,
) -> bool:
    if not cpf_only_for_residents:
        return True
    cpf = float(cpf_contrib or 0.0)
    if cpf == 0:
        return True
    return (residency_status or "").lower() == "resident"
