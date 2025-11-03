# Makefile for Docker commands

.PHONY: help build up down restart logs shell migrate superuser test clean

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker containers"
	@echo "  make up          - Start containers"
	@echo "  make down        - Stop containers"
	@echo "  make restart     - Restart containers"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Open Django shell"
	@echo "  make migrate     - Run migrations"
	@echo "  make superuser   - Create superuser"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

superuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f
