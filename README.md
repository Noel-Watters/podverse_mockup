# Podverse Mockup - Docker Setup & Usage

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your machine (Windows, macOS, WSL2, or a real-deal Linux box).
* Docker Compose is included with Docker Desktop.

> Linux users: May the flags be ever in your favor. Install Docker & Compose manually and enable the daemon.

---

## Cloning the Repo

```bash
git clone https://github.com/Cramessar/podverse_mockup.git
cd podverse_mockup
```

---

## Build Docker Images

You should have `Dockerfile`s for backend, frontend, and the database setup in place.

To build and start all services (backend, frontend, Postgres, Redis, Celery, and Celery-Beat):

```bash
docker compose up --build
```

Once built, containers should appear in Docker Desktop, humming along nicely.

---

## ▶ Running the Containers

You've got options:

* **Option 1**: Click the "play" button in Docker Desktop. Easy.
* **Option 2**: Real devs use terminals. (Or masochists. Hard to tell.)

```bash
docker compose up
```

This will start all services as defined in `docker-compose.yml`:
- **Backend**: Flask API server with task queue integration
- **Frontend**: Next.js application  
- **Database**: PostgreSQL database
- **Redis**: In-memory store for caching and task queue
- **Celery**: Background task worker
- **Celery-Beat**: Scheduled task scheduler

---

## Database Setup & Initialization

Schema and seeding are handled automatically by the backend container using scripts like `init_database.sql` or individual seed scripts.

For details on how it works or to re-run seeders, see:

```
/podverse_db/README.md
```

---

## Access the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Postgres (DB)**: `localhost:5432` (connect via pgAdmin or DBeaver)
- **Redis**: `localhost:6379` (for caching and task queue)

> Postgres creds are usually defined in `.env` or `docker-compose.yml`. Use those if you need to connect manually.

### Background Services

- **Celery Worker**: Handles background tasks (feed parsing, data processing)
- **Celery Beat**: Scheduled task runner (auto-reparse feeds every hour)


### 📂 Environment Variables (`.env`)

This project uses environment variables to keep configuration clean and secure across services. Create a `.env` file at the root of the project using the `.env.example` as a guide.

Here are a few key variables you’ll need:

```env
copy the example
```

> ⚠️ **Important:**  
> This `.env` file is used by **multiple services** in the Docker Compose setup — such as the backend, AI container, and both databases. Docker Compose will automatically inject these values via `env_file`.

🔍 You don’t need to memorize these — just peek at `.env.example` and fill in the blanks. It’ll make sense, eventually. Promise. ✨



## Stopping Containers

To gracefully stop all running services:

```bash
docker compose down
```

---

## Cleanup & Troubleshooting

If Docker starts acting like a gremlin got into your volumes, try the following to clean things up:

### 📼 Remove stopped containers, dangling images, and unused networks:

```bash
docker system prune -a
```

> Warning: This deletes *all* unused data. Use wisely.

###  Remove all unused volumes (especially useful for DB issues):

```bash
docker volume prune
```

###  Nuke and rebuild everything (if all else fails):

I cannot stress this enough. Too many problems will be caused by old build caches, volumes, etc. Just run these commands every few days and rebuild. 

```bash
docker compose down -v --remove-orphans
docker system prune -a
docker volume rm $(docker volume ls -q)
docker compose up --build
```

---

##  Helpful Commands


Just use docker desktop. It simplifies all of these tips.

### View logs for a container:

```bash
docker logs <container-name>
```

### List all containers (running or not):

```bash
docker ps -a
```

### Restart a single container:

```bash
docker restart <container-name>
```

### Check container health status (if healthchecks are defined):

```bash
docker inspect --format='{{json .State.Health}}' <container-name>
```

---

## Notes

* Make sure your line endings for `entrypoint.sh` or seed scripts use **LF**, not **CRLF**, especially if editing on Windows.
* Port conflicts? Double-check nothing else is running on 3000/5000/5432.
