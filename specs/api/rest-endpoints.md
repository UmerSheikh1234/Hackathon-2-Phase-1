# REST API Endpoints

## Base URL
Development: http://localhost:8000
Production: https://api.example.com

## Authentication
All endpoints require JWT token in header:
Authorization: Bearer <token>

## Endpoints
### GET /api/tasks
List all tasks for authenticated user.
Query Parameters:
- status: "all" | "pending" | "completed"
- sort: "created" | "title" | "due_date"
Response: Array of Task objects

### POST /api/tasks
Create a new task.
Request Body:
- title: string (required)
- description: string (optional)
Response: Created Task object