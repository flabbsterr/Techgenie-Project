APP_NAME = "IT Support Portal"
VERSION = "1.0.0"
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

DEFAULT_USERS = [
    {"username": "staff", "password": "password123"},
    {"username": "it", "password": "itadmin123"}
]

SAMPLE_TICKETS = [
    {"name": "John Doe", "issue": "Computer won't start", "status": "Open", "priority": "High"},
    {"name": "Jane Smith", "issue": "Email not working", "status": "In Progress", "priority": "Medium"},
    {"name": "Bob Johnson", "issue": "Printer offline", "status": "Closed", "priority": "Low"}
]