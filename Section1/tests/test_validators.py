from datetime import date

from tax_pipeline.validators import (
    validate_chargeable,
    validate_cpf_residency,
    validate_filing_date,
    validate_nric,
    validate_postal,
)


def test_validate_nric():
    assert validate_nric("S1234567D", r"^[STFG][0-9]{7}[A-Z]$")
    assert not validate_nric("X1234567D", r"^[STFG][0-9]{7}[A-Z]$")


def test_validate_postal():
    assert validate_postal("123456", r"^[0-9]{6}$")
    assert not validate_postal("12A456", r"^[0-9]{6}$")


def test_validate_filing_date():
    assert validate_filing_date(date(2023, 4, 1), 2023)
    assert not validate_filing_date(date(2022, 12, 31), 2023)


def test_validate_chargeable():
    assert validate_chargeable(100000, 8000, 92000)
    assert validate_chargeable(100000, 120000, 0)
    assert not validate_chargeable(100000, 8000, 93000)


def test_validate_cpf_residency():
    assert validate_cpf_residency(0, "Non-Resident")
    assert validate_cpf_residency(500, "Resident")
    assert not validate_cpf_residency(500, "Non-Resident")
