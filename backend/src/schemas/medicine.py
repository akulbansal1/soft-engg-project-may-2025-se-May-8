from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class MedicineBase(BaseModel):
    name: str = Field(..., example="Paracetamol", description="Name of the medicine")
    dosage: str = Field(..., example="500mg", description="Dosage information")
    frequency: str = Field(..., example="Once a day after dinner", description="Frequency of intake")
    start_date: date = Field(..., example="2025-06-25", description="Start date of the medicine course")
    end_date: Optional[date] = Field(None, example="2025-07-05", description="End date of the medicine course")
    notes: Optional[str] = Field(None, example="Take with food", description="Additional notes or instructions")

class MedicineCreate(MedicineBase):
    user_id: int = Field(..., example=1, description="ID of the user taking the medicine")

class MedicineUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Paracetamol")
    dosage: Optional[str] = Field(None, example="500mg")
    frequency: Optional[str] = Field(None, example="Once a day after dinner")
    start_date: Optional[date] = Field(None, example="2025-06-25")
    end_date: Optional[date] = Field(None, example="2025-07-05")
    notes: Optional[str] = Field(None, example="Take with food")

class MedicineResponse(MedicineBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)

    class Config:
        from_attributes = True
