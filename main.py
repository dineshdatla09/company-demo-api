from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from enum import Enum

app = FastAPI(
    title="API to Create Company",
    description="API to manage company, mirrors the UI form",
    version="1.0.0",
)

# --- Dropdowns (mirrors UI dropdown options) ---
class ClientStatus(str, Enum):
    deployed = "Deployed"
    pending = "Pending"
    inactive = "Inactive"

class CompanyType(str, Enum):
    co_sourced = "Co-Sourced"
    fully_outsourced = "Fully Outsourced"
    self_managed = "Self Managed"

# --- Company Model (mirrors the UI form exactly) ---
class Company(BaseModel):
    # Required fields (marked with * on the UI)
    company_name: str
    ticker_symbol: str
    file_ticker: str
    sales_force_account_id: str

    # Optional fields
    client_status: Optional[ClientStatus] = ClientStatus.deployed
    company_type: Optional[CompanyType] = CompanyType.co_sourced
    company_logo_file_name: Optional[str] = None
    drop_box_url: Optional[str] = None

    # Products checkboxes (False = unchecked, True = checked)
    stock_plan_administration_software: Optional[bool] = False
    employee_services: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corp",
                "ticker_symbol": "ACME",
                "file_ticker": "ACME_FILE",
                "sales_force_account_id": "SF-001234",
                "client_status": "Deployed",
                "company_type": "Co-Sourced",
                "company_logo_file_name": "acme_logo.png",
                "drop_box_url": "https://dropbox.com/acme",
                "stock_plan_administration_software": True,
                "employee_services": False
            }
        }

# --- In-memory store ---
companies: dict[int, Company] = {}
next_id = 1

# --- Health Check ---
@app.get("/", tags=["Health"])
def root():
    """Check if the API is running."""
    return {"status": "ok", "message": "Welcome to Company API!"}

# --- CREATE Company (mirrors clicking the Create button on UI) ---
@app.post("/company", status_code=201, tags=["Companies"])
def create_company(company: Company):
    """
    Create a new company.
    Fill in the fields below just like you would on the UI form.
    Required fields: company_name, ticker_symbol, file_ticker, sales_force_account_id.
    """
    global next_id

    # Check for duplicate company name
    for c in companies.values():
        if c.company_name.lower() == company.company_name.lower():
            raise HTTPException(status_code=400, detail="Company name already exists")

    companies[next_id] = company
    next_id += 1
    return {
        "message": "Company created successfully",
        "id": next_id - 1,
        "company": company
    }

# --- GET All Companies ---
@app.get("/company", tags=["Companies"])
def list_companies():
    """Fetch all companies."""
    return {"total": len(companies), "companies": companies}

# --- GET One Company ---
@app.get("/company/{company_id}", tags=["Companies"])
def get_company(company_id: int):
    """Fetch a single company by ID."""
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies[company_id]