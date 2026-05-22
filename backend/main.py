from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI()

FAKE_API_URL = "https://jsonplaceholder.typicode.com/users"


class Employee(BaseModel):
    id: int
    name: str
    email: str
    company: str


local_employees: list[dict] = []


@app.get("/employees", response_model=List[Employee])
def get_employees():
    response = requests.get(FAKE_API_URL)
    api_employees = response.json()

    normalized = [
        {
            "id": emp["id"],
            "name": emp["name"],
            "email": emp["email"],
            "company": emp["company"]["name"],
        }
        for emp in api_employees
    ]

    return normalized + local_employees


@app.post("/employees", response_model=Employee)
def add_employee(emp: Employee):
    local_employees.append(emp.dict())
    return emp


@app.put("/employees/{id}", response_model=Employee)
def update_employee(id: int, emp: Employee):
    for i, e in enumerate(local_employees):
        if e["id"] == id:
            local_employees[i] = emp.dict()
            return emp
    raise HTTPException(status_code=404, detail="Employee not found")


@app.delete("/employees/{id}")
def delete_employee(id: int):
    global local_employees
    local_employees = [e for e in local_employees if e["id"] != id]
    return {"message": "Employee deleted"}
