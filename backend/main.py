from fastapi import FastAPI
import requests

app = FastAPI()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Backend is running with FastAPI + FakeAPI"}

# Employees (fetch from FakeAPI)
@app.get("/employees")
def get_employees():
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    return response.json()

# Departments (derive from FakeAPI employees)
@app.get("/departments")
def get_departments():
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    employees = response.json()
    departments = list({emp["company"]["name"] for emp in employees})
    return departments

# Attendance (fake logs from FakeAPI posts)
@app.get("/attendance")
def get_attendance():
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    posts = response.json()
    # Just return first 10 as fake attendance logs
    return posts[:10]
