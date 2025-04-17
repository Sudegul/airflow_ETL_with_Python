# Dockerized Microservices ETL Pipeline  

**Sude Gül** 


---

## 📦 Project Overview

This project is an extension of the Airflow ETL Pipeline assignment.  
It implements the system using **Docker containers** and **microservices**,
each running in isolated environments and communicating over a Docker network.

---

## 🧱 Project Structure

```
.
├── backend/               # Flask API service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Static HTML served via Nginx
│   ├── index.html
│   └── Dockerfile
├── database/              # PostgreSQL init SQL
│   └── init.sql
├── docker-compose.yml     # All services orchestrated here
└── README.md              # This file
```

---

## 🚀 How to Run the Project

### 🔧 1. Build and Start All Containers

```bash
docker-compose up --build
```

### 🛑 To Stop All Services

```bash
docker-compose down
```

---

## 🌐 Services Overview

| Service   | URL                              | Description                   |
|-----------|----------------------------------|-------------------------------|
| Frontend  | http://localhost:8080            | Static webpage via Nginx     |
| Backend   | http://localhost:5001/api/data   | Flask API returning DB data  |
| Database  | localhost:5433                   | PostgreSQL (container only)  |

---

## 🗄️ Database Info

- Image: `postgres:13`
- Port: `5433` (host) → `5432` (container)
- DB Name: `airflowdb`
- User: `airflowuser`
- Password: `airflowpass`

### 🧪 Initial Table

Upon startup, the following table is created via `init.sql`:

```sql
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
```

And 3 example rows are inserted:
- Sude
- Airflow
- Docker

---

## 📌 Notes

- All services run in an isolated Docker network (`app-network`)
- Backend uses `psycopg2` to connect to PostgreSQL
- All configs and environment variables are managed via `docker-compose.yml`

---

## ✅ Tested On

- macOS (M1/M2)
- Docker Desktop
- Docker Compose v2.20+
- Python 3.10 (Flask backend)

---

---

## 🚀 Optional: Scaling and Load Balancing

This system can be scaled horizontally using Docker Compose or Docker Swarm.

### ➕ Scaling with Docker Compose
You can run multiple instances of the backend service using the `--scale` option:

```bash
docker-compose up --build --scale backend=3
```

This command runs 3 backend containers. A load balancer such as **Nginx** or **Traefik** can be used to distribute requests among them.

### ➕ Load Balancing Concept
In a production environment, a **reverse proxy** would be placed in front of the backend services to handle incoming traffic and distribute it across multiple instances to improve availability and performance.

Tools commonly used:
- Nginx (with round-robin configuration)
- HAProxy
- Docker Swarm Ingress
- Kubernetes Ingress Controller

> This feature was not implemented in this project, but the architecture supports it.


---

## 🛠️ Airflow Integration (ETL)

Airflow UI is accessible at: [http://localhost:8081](http://localhost:8081)

A DAG named `sde_gul_etl` performs the following steps:

1. **extract_csv**: Loads data from `in_store_sales.csv` into PostgreSQL  
2. **extract_postgres**: Extracts data from `online_sales` table  
3. **transform**: Aggregates total quantities per product  
4. **load**: Inserts final results into `aggregated_sales` table  

📁 DAG file location: `airflow/dags/etl_hw1_dag.py`  
All DAGs can be triggered manually from the Airflow web UI.

---

## ⚠️ Challenges Faced

- Port conflicts with PostgreSQL (5432, 5433)
- Airflow services failed to start before running `airflow db init`
- DAG did not appear initially due to folder visibility in IDE
- psycopg2 failed due to `numpy.int64` → resolved by converting to `int()`
- CSV file was missing required columns (like `sale_date`)
- Confusion between Airflow’s DB and application DB
- Docker volume sync issues on macOS when editing files outside container

