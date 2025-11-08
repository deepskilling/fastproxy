# ============================================================================
# FastProxy Docker Makefile
# ============================================================================
# Convenient commands for Docker operations
# ============================================================================

.PHONY: help build up down logs ps restart clean demo prod

# Default target
.DEFAULT_GOAL := help

# Docker Compose command (use v2 if available)
DOCKER_COMPOSE := $(shell if docker compose version > /dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

# Files
DEMO_FILE := docker-compose.demo.yml
PROD_FILE := docker-compose.yml

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "FastProxy Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^## .*:' $(MAKEFILE_LIST) | sed 's/## /  /' | column -t -s ':'

## demo: Start demo stack
demo:
	@echo "$(GREEN)Starting demo stack...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) up -d
	@echo "$(GREEN)✓ Demo stack started$(NC)"
	@echo "Access at: http://localhost:8000"

## prod: Start production stack
prod:
	@echo "$(GREEN)Starting production stack...$(NC)"
	$(DOCKER_COMPOSE) -f $(PROD_FILE) up -d
	@echo "$(GREEN)✓ Production stack started$(NC)"

## build: Build all images
build:
	@echo "$(BLUE)Building images...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) build

## build-prod: Build production images
build-prod:
	@echo "$(BLUE)Building production images...$(NC)"
	$(DOCKER_COMPOSE) -f $(PROD_FILE) build

## build-nc: Build without cache
build-nc:
	@echo "$(BLUE)Building images (no cache)...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) build --no-cache

## up: Start services (demo)
up: demo

## down: Stop and remove containers
down:
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

## down-prod: Stop production services
down-prod:
	@echo "$(YELLOW)Stopping production services...$(NC)"
	$(DOCKER_COMPOSE) -f $(PROD_FILE) down
	@echo "$(GREEN)✓ Production services stopped$(NC)"

## down-v: Stop and remove volumes (⚠️  deletes data)
down-v:
	@echo "$(RED)⚠️  This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) -f $(DEMO_FILE) down -v; \
		echo "$(GREEN)✓ Services and volumes removed$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

## logs: View logs (all services)
logs:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) logs -f

## logs-fastproxy: View FastProxy logs
logs-fastproxy:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) logs -f fastproxy

## logs-backend: View backend logs
logs-backend:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) logs -f backend

## logs-frontend: View frontend logs
logs-frontend:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) logs -f frontend

## ps: List running containers
ps:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) ps

## restart: Restart all services
restart:
	@echo "$(YELLOW)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

## restart-fastproxy: Restart FastProxy only
restart-fastproxy:
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) restart fastproxy

## shell-fastproxy: Open shell in FastProxy container
shell-fastproxy:
	docker exec -it fastproxy /bin/sh

## shell-backend: Open shell in backend container
shell-backend:
	docker exec -it fastproxy-backend /bin/sh

## shell-frontend: Open shell in frontend container
shell-frontend:
	docker exec -it fastproxy-frontend /bin/sh

## health: Check health status
health:
	@echo "Service Health Status:"
	@docker ps --filter "name=fastproxy" --format "table {{.Names}}\t{{.Status}}"

## stats: Show resource usage
stats:
	docker stats --no-stream fastproxy fastproxy-backend fastproxy-frontend 2>/dev/null || docker stats --no-stream

## clean: Remove stopped containers and unused images
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker container prune -f
	docker image prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

## clean-all: Remove everything (⚠️  including volumes)
clean-all:
	@echo "$(RED)⚠️  This will remove all containers, images, and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) -f $(DEMO_FILE) down -v; \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ All Docker resources removed$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

## backup: Backup volumes
backup:
	@echo "$(BLUE)Backing up volumes...$(NC)"
	@mkdir -p backups
	@docker run --rm -v fastproxy-audit:/data -v $(PWD)/backups:/backup \
		alpine tar czf /backup/fastproxy-audit-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "$(GREEN)✓ Backup complete$(NC)"

## restore: Restore volumes (requires BACKUP_FILE variable)
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Error: BACKUP_FILE not specified$(NC)"; \
		echo "Usage: make restore BACKUP_FILE=backups/fastproxy-audit-YYYYMMDD-HHMMSS.tar.gz"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring from $(BACKUP_FILE)...$(NC)"
	@docker run --rm -v fastproxy-audit:/data -v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$$(basename $(BACKUP_FILE)) -C /
	@echo "$(GREEN)✓ Restore complete$(NC)"

## test: Test the demo stack
test:
	@echo "$(BLUE)Testing services...$(NC)"
	@echo -n "FastProxy: "
	@curl -sf http://localhost:8000/health > /dev/null && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "Backend: "
	@curl -sf http://localhost:8001/api/health > /dev/null && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "Frontend: "
	@curl -sf http://localhost:3000 > /dev/null && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"

## config: Validate docker-compose configuration
config:
	@echo "$(BLUE)Validating demo configuration...$(NC)"
	$(DOCKER_COMPOSE) -f $(DEMO_FILE) config

## pull: Pull latest base images
pull:
	@echo "$(BLUE)Pulling latest base images...$(NC)"
	docker pull python:3.11-slim
	docker pull node:18-alpine
	@echo "$(GREEN)✓ Pull complete$(NC)"

## update: Update and rebuild all services
update: pull build-nc down demo
	@echo "$(GREEN)✓ Update complete$(NC)"

