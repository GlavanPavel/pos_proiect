# Event Management Platform

## Description
This project is a full-stack platform designed to manage artistic events and track ticket sales. The system is built using a Service-Oriented Architecture (SOA), featuring a React frontend that communicates with three backend services:

* **Frontend:** A web application built with React to handle user interfaces for clients, event managers, and administrators.
* **Event WebService:** A backend service that manages events, event packages, and tickets (FastAPI + MariaDB).
* **Client WebService:** A backend service that manages client profiles and purchased tickets (FastAPI + MongoDB).
* **Auth Service:** An Identity Management (IDM) service for managing users and roles (gRPC + SQL).

<img width="800" alt="Diagrama Arhitectura" src="https://github.com/user-attachments/assets/2edd3895-966b-4cf0-8ec1-89ae46f146c5" />

## Project Details
* **Containerization:** All backend services and databases are containerized using Docker. The React frontend is run locally outside of Docker.
* **Architecture:** The backend services communicate with each other using HTTP (REST) and gRPC protocols.

## Running and Initializing the Application

### 1. Start the Backend Services
Spin up the backend containers using Docker Compose:

```bash
docker-compose up -d
```

### 2. Initialize the Databases
Although the database initialization process could have been automated within the docker-compose file, it was left manual.

```bash
# Create tables for the events service
docker exec -it evenimente-service python fastapi_app/create_tables.py

# Initialize databases and populate initial data
docker exec -it clienti-service python -m user_management.init_mongo
docker exec -it evenimente-service python -m fastapi_app.events_init
docker exec -it idm-service python -m auth_service.init_idm
```

### 3. Start the React Frontend
```bash
cd frontend
npm install
npm start
```

## API Documentation
After initialization, the interactive Swagger documentation for the backend APIs can be accessed locally at their default routes (e.g., `http://localhost:8000/docs`).
