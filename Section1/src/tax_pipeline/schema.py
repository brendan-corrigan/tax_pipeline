from datetime import date
from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FilingStatus(StrEnum):
    single = "Single"
    married = "Married"


class TaxReturn(BaseModel):
    taxpayer_id: int = Field()  # REQUIRED

    nric: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)

    filing_status: Optional[Literal["single", "married"]] = Field(default=None)

    assessment_year: Optional[int] = Field(default=None)
    filing_date: Optional[date] = Field(default=None)

    annual_income_sgd: Optional[float] = Field(default=None)
    chargeable_income_sgd: Optional[float] = Field(default=None)
    tax_payable_sgd: Optional[float] = Field(default=None)
    tax_paid_sgd: Optional[float] = Field(default=None)
    total_reliefs_sgd: Optional[float] = Field(default=None)

    number_of_dependents: Optional[int] = Field(default=None)

    occupation: Optional[str] = Field(default=None)
    residential_status: Optional[str] = Field(default=None)

    postal_code: Optional[str] = Field(default=None)
    housing_type: Optional[str] = Field(default=None)

    cpf_contributions_sgd: Optional[float] = Field(default=None)
    foreign_income_sgd: Optional[float] = Field(default=None)
