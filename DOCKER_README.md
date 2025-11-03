# Abhirang - Docker Setup

## Prerequisites
- Docker
- Docker Compose

## Quick Start

### 1. Clone and Setup Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (optional)
nano .env
```

### 2. Build and Run with Docker
```bash
# Build and start containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Run Migrations
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files (if needed)
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Access the Application
- Website: http://localhost:8000
- Admin: http://localhost:8000/admin

## Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Stop Containers
```bash
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Containers
```bash
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Execute Commands
```bash
# Django shell
docker-compose exec web python manage.py shell

# Create app
docker-compose exec web python manage.py startapp appname

# Run tests
docker-compose exec web python manage.py test
```

### Database Access
```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d abhirang_db
```

## Development Workflow

The project directory is mounted as a volume, so changes to your code will be reflected immediately without rebuilding.

If you modify `requirements.txt`, rebuild the web service:
```bash
docker-compose up -d --build web
```

## Switching Between SQLite and PostgreSQL

### Use SQLite (Default for local development)
Don't set `DB_ENGINE` in `.env` or comment it out:
```bash
# DB_ENGINE=django.db.backends.postgresql
```

### Use PostgreSQL (For Docker)
Set in `.env`:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=abhirang_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

## Troubleshooting

### Database Connection Issues
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Permission Issues
```bash
# Fix media/static permissions
docker-compose exec web chmod -R 755 /app/media
docker-compose exec web chmod -R 755 /app/staticfiles
```

### Clean Start
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild everything
docker-compose up --build
```

## Production Notes

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Generate a new `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use a production-grade WSGI server (Gunicorn is included)
5. Set up reverse proxy (Nginx/Apache)
6. Use secure passwords for database
7. Set up SSL certificates
