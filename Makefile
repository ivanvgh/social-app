# ---- Config ----
ENV ?= ./.env
COMPOSE := docker compose --env-file $(ENV) -f docker-compose.yml -f docker-compose.dev.yml
SERVICES := gateway auth profiles posts comments notifications media
ACTIVE_SERVICES := $(filter-out $(EXCLUDE),$(SERVICES))

# Helper: read KEY from $(ENV)
define GET_ENV
$(strip $(shell awk -F= '/^$(1)=/{print $$2}' $(ENV) 2>/dev/null))
endef

# Ports from .env with sane defaults
GATEWAY_PORT  := $(or $(call GET_ENV,GATEWAY_PORT),8080)
AUTH_PORT     := $(or $(call GET_ENV,AUTH_PORT),8001)
PROFILES_PORT := $(or $(call GET_ENV,PROFILES_PORT),8002)
POSTS_PORT    := $(or $(call GET_ENV,POSTS_PORT),8003)
COMMENTS_PORT := $(or $(call GET_ENV,COMMENTS_PORT),8004)
NOTIFS_PORT   := $(or $(call GET_ENV,NOTIFICATIONS_PORT),8005)
MEDIA_PORT    := $(or $(call GET_ENV,MEDIA_PORT),8006)

.PHONY: help env build up up-d down ps logs tail restart re sh \
        health health-live health-ready ping pg mongo redis clean prune

help:
	@echo 'Usage:'
	@echo '  make env            - Create .env from .env.example if missing'
	@echo '  make up             - Build & start all services (daemonized)'
	@echo '  make down           - Stop & remove containers'
	@echo '  make build          - Build all images'
	@echo '  make ps             - Show compose status'
	@echo '  make logs           - Show last logs for all services'
	@echo '  make tail SERVICE=auth     - Follow logs for a single service'
	@echo '  make restart SERVICE=auth  - Restart a single service'
	@echo '  make re SERVICE=auth       - Rebuild+restart a single service'
	@echo '  make sh SERVICE=auth       - Shell into a service container'
	@echo '  make health         - Check /health/live and /health/ready'
	@echo '  make ping           - Ping Postgres, Mongo, Redis'
	@echo '  make clean|prune    - Cleanup (careful)'

env:
	@test -f $(ENV) || (cp .env.example $(ENV) && echo 'Created $(ENV) from .env.example')

build:
	$(COMPOSE) build

up up-d:
	$(COMPOSE) up --build -d
	@$(MAKE) ps

up-ex:
	$(COMPOSE) up -d $(filter-out $(EXCLUDE),$(SERVICES))

down:
	$(COMPOSE) down

stop:
	$(COMPOSE) stop

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs --tail=100

tail:
	@test -n "$(SERVICE)" || (echo 'Set SERVICE=<name>'; exit 1)
	$(COMPOSE) logs -f --tail=200 $(SERVICE)

restart:
	@test -n "$(SERVICE)" || (echo 'Set SERVICE=<name>'; exit 1)
	$(COMPOSE) up -d $(SERVICE)

re:
	@test -n "$(SERVICE)" || (echo 'Set SERVICE=<name>'; exit 1)
	$(COMPOSE) up --build -d $(SERVICE)

sh:
	@test -n "$(SERVICE)" || (echo 'Set SERVICE=<name>'; exit 1)
	$(COMPOSE) exec $(SERVICE) /bin/sh || $(COMPOSE) exec $(SERVICE) /bin/bash

# ---- Health checks ----
health: health-live health-ready

health-live:
	@set -e; set -a; . $(ENV); set +a; \
	for name in $(ACTIVE_SERVICES); do \
	  case $$name in \
	    gateway) port=$$GATEWAY_PORT ;; \
	    auth) port=$$AUTH_PORT ;; \
	    profiles) port=$$PROFILES_PORT ;; \
	    posts) port=$$POSTS_PORT ;; \
	    comments) port=$$COMMENTS_PORT ;; \
	    notifications) port=$$NOTIFICATIONS_PORT ;; \
	    media) port=$$MEDIA_PORT ;; \
	  esac; \
	  url="http://localhost:$$port/health/live"; \
	  out=$$(curl -sS "$$url" || true); \
	  if echo "$$out" | grep -q '"status":"ok"'; then \
	    printf '✓ %s /live -> %s\n' "$$name" "$$out"; \
	  else \
	    printf '✗ %s /live -> %s\n' "$$name" "$$out"; exit 1; \
	  fi; \
	done

health-ready:
	@set -e; set -a; . $(ENV); set +a; \
	for name in $(ACTIVE_SERVICES); do \
	  case $$name in \
	    gateway) port=$$GATEWAY_PORT ;; \
	    auth) port=$$AUTH_PORT ;; \
	    profiles) port=$$PROFILES_PORT ;; \
	    posts) port=$$POSTS_PORT ;; \
	    comments) port=$$COMMENTS_PORT ;; \
	    notifications) port=$$NOTIFICATIONS_PORT ;; \
	    media) port=$$MEDIA_PORT ;; \
	  esac; \
	  url="http://localhost:$$port/health/ready"; \
	  out=$$(curl -sS "$$url" || true); \
	  if echo "$$out" | grep -q '"status":"ready"\|"status":"ok"'; then \
	    printf '✓ %s /ready -> %s\n' "$$name" "$$out"; \
	  else \
	    printf '✗ %s /ready -> %s\n' "$$name" "$$out"; exit 1; \
	  fi; \
	done

# ---- Dependency pings ----
ping: pg mongo redis

pg:
	$(COMPOSE) exec -T postgres pg_isready -U social -d social_auth -h localhost

mongo:
	$(COMPOSE) exec -T mongo mongosh -u social -p socialpass --quiet --eval 'db.runCommand({ ping: 1 })'

redis:
	$(COMPOSE) exec -T redis redis-cli ping

# ---- Cleanup (dangerous) ----
clean:
	$(COMPOSE) down -v --remove-orphans

prune:
	@echo 'Pruning unused images/volumes (system-wide)...'
	docker system prune -f
	docker volume prune -f
