# Social Media Platform — Full Specification & Implementation Plan (Monorepo)

**Date:** 2025-08-20

> This document combines a complete **Software Requirements Specification (SRS)** and a full **Implementation Plan** for a simplified Facebook‑like social platform, designed for a team of 5 developers using a **monorepo**, **FastAPI** microservices, **React** SPA, **PostgreSQL + MongoDB** (polyglot), **Redis** (Streams + cache + rate limits), and **Docker Compose** for local orchestration.  
> **No implementation code** is included—only contracts, structures, and plans.

---


## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Goals and Non-Goals](#2-goals-and-non-goals)
- [3. Scope](#3-scope)
- [4. Architecture Overview](#4-architecture-overview)
  - [4.1 Monorepo Strategy](#41-monorepo-strategy)
  - [4.2 Services and Data Ownership](#42-services-and-data-ownership)
  - [4.3 Technology Stack](#43-technology-stack)
- [5. Functional Requirements](#5-functional-requirements)
  - [5.1 Authentication & Profiles](#51-authentication--profiles)
  - [5.2 Posts](#52-posts)
  - [5.3 Comments & 1‑Level Replies](#53-comments--1level-replies)
  - [5.4 Likes](#54-likes)
  - [5.5 Notifications (Real‑Time)](#55-notifications-realtime)
  - [5.6 Feeds](#56-feeds)
  - [5.7 Media](#57-media)
- [6. Non‑Functional Requirements](#6-nonfunctional-requirements)
- [7. Security Requirements](#7-security-requirements)
- [8. Data Model](#8-data-model)
  - [8.1 PostgreSQL Schema](#81-postgresql-schema)
  - [8.2 MongoDB Collections](#82-mongodb-collections)
- [9. Events & Real‑Time Design](#9-events---realtime-design)
  - [9.1 Redis Streams](#91-redis-streams)
  - [9.2 Event Contracts](#92-event-contracts)
  - [9.3 Idempotency & Error Handling](#93-idempotency--error-handling)
- [10. API Contracts (High‑Level)](#10-api-contracts-highlevel)
  - [10.1 Auth Service](#101-auth-service)
  - [10.2 Profile Reads](#102-profile-reads)
  - [10.3 Posts Service](#103-posts-service)
  - [10.4 Comments Service](#104-comments-service)
  - [10.5 Notifications Service](#105-notifications-service)
  - [10.6 Gateway](#106-gateway)
- [11. WebSocket Contract](#11-websocket-contract)
- [12. Caching & Rate Limiting](#12-caching--rate-limiting)
- [13. Observability](#13-observability)
- [14. Deployment & Environments](#14-deployment--environments)
- [15. Risks & Mitigations](#15-risks--mitigations)
- [16. Acceptance Criteria (MVP)](#16-acceptance-criteria-mvp)
- [17. Implementation Plan](#17-implementation-plan)
  - [17.1 Phases & Milestones](#171-phases--milestones)
  - [17.2 Team Roles & RACI](#172-team-roles--raci)
  - [17.3 Branching, CI/CD, and Versioning](#173-branching-cicd-and-versioning)
  - [17.4 QA & Testing Strategy](#174-qa--testing-strategy)
  - [17.5 Release & Go‑Live Checklist](#175-release--golive-checklist)
  - [17.6 Documentation Artifacts](#176-documentation-artifacts)
  - [17.7 Issue Templates](#177-issue-templates)

---

## 1. Executive Summary

We will build a modern, microservice‑based social platform where users can create posts (**title, description, single image**), interact via **likes**, **comments**, and **1‑level replies**, and receive **real‑time notifications** for **post likes** and **post comments**. The system uses **polyglot persistence**: **PostgreSQL** for identity and security‑sensitive relational data; **MongoDB** for social content (posts, comments, notifications) with denormalized counters. **Redis Streams** deliver reliable at‑least‑once events, and a **WebSocket** channel provides real‑time delivery. The solution is developed in a **monorepo** with Docker Compose for local orchestration and shared contracts.

---

## 2. Goals and Non-Goals

**Goals**
- Production‑grade foundations: authentication, session security, and consistent API contracts.
- Polyglot storage aligned to data shapes and throughput patterns.
- Real‑time notifications for post likes and comments.
- Clean service boundaries, observable system, and staged delivery plan for a 5‑dev team.
- Monorepo for speed, atomic changes, and shared tooling.

**Non‑Goals (MVP)**
- Social graph (follow/friends), DMs, groups, advanced search, or recommendations.
- Video uploads/transcoding; content moderation at scale.
- Federated identity (OAuth social login) — can be added later.

---

## 3. Scope

**In Scope**
- Users (auth & profile), posts with image preview, comments and 1‑level replies, likes, real‑time notifications, feeds (global & profile), minimal media flow (URL or presigned upload), rate limits, and observability.

**Out of Scope (for MVP)**
- Notifications for comment likes or replies (only post likes and post comments).
- Multi‑tenant sharding, regionalization, and multi‑cloud DR.

---

## 4. Architecture Overview

### 4.1 Monorepo Strategy

**Why monorepo (team of 5 + Docker Compose):**
- Atomic contract and multi‑service changes in one PR.
- Single `compose up` for full environment.
- Shared standards (linters, type checking, pre‑commit) and generated API clients.

**Suggested layout** (no implementation code shown):
```
/social-app/
  /gateway/              # API gateway (FastAPI)
  /auth/                 # Auth & sessions (FastAPI + Postgres)
  /profiles/             # Profile reads/writes (FastAPI + Postgres)
  /posts/                # Posts & post likes (FastAPI + MongoDB)
  /comments/             # Comments, 1-level replies, likes (FastAPI + MongoDB)
  /notifications/        # Notifications + WS + Redis Streams (FastAPI + MongoDB + Redis)
  /media/                # (optional) presigned uploads service (FastAPI + S3/MinIO)
  /web/                  # React SPA
  /libs/
    /contracts/          # OpenAPI specs, generated clients (TS & Python)
    /py-common/          # shared py utils (auth headers, tracing, error model)
  /deploy/
    docker-compose.yml
    docker-compose.dev.yml
    docker-compose.prod.yml
  /ops/
    /migrations/         # Alembic for Postgres
    /k8s/                # future
  /docs/                 # ADRs, diagrams, RFCs
  /.github/workflows/    # CI pipelines
```

**Engineering conventions**
- Python: PEP8, ruff, mypy, pytest; functions under ~20 lines where practical; SOLID & dependency injection.
- JS/TS: Airbnb ESLint, Prettier; prefer functions; simple objects over deep inheritance.
- Shared contracts: OpenAPI first; generated clients used between services and in React.

### 4.2 Services and Data Ownership

| Service | Primary DB | Secondary | Responsibilities |
|---|---|---|---|
| Auth | PostgreSQL | Redis (rate limit) | Registration, login, JWT access tokens, rotating refresh cookies, sessions/devices, email verify, password reset, optional TOTP |
| Profiles | PostgreSQL | — | Profile reads/writes, privacy flags (future) |
| Posts | MongoDB | Redis (hot counts) | Post CRUD, like/unlike posts, feed & profile listings, counters |
| Comments | MongoDB | Redis (hot counts) | Comments, 1‑level replies, likes on comments/replies (optional later) |
| Notifications | MongoDB | Redis Streams, WebSockets | Persist notifications; consume events; push real‑time messages |
| Gateway | — | — | Entry point; JWT validation; routing; CORS; rate limits; request IDs |
| Media (opt.) | — | S3/MinIO | Presigned uploads & validations |

### 4.3 Technology Stack

- Backend: FastAPI (Python 3.12), Pydantic v2
- Frontend: React (TypeScript), React Query (or RTK Query), Zustand/Redux
- Databases: PostgreSQL 15+ (auth), MongoDB 6+ (content)
- Infra: Redis 7 (Streams + cache + rate limits), WebSockets
- Orchestration: Docker + Docker Compose (dev); K8s (future)
- Auth: JWT (RS256/EdDSA), rotating refresh cookies, Argon2id/bcrypt
- Observability: JSON logs, metrics, request IDs; optional OpenTelemetry

---

## 5. Functional Requirements

### 5.1 Authentication & Profiles
- Register, login, logout (single/all devices), silent refresh.
- JWT access (short‑lived) + rotating refresh cookie (long‑lived).
- Device sessions tracked; email verification and password reset.
- Profile: username, avatar, bio, created date; view profile by username.

### 5.2 Posts
- Create, read, update, delete (owner only).
- Fields: title (≤ 120), description (≤ 5000), image_url (optional), owner_id.
- Feed preview: image (16:9, center‑crop), title single‑line ellipsis, description 2–3 lines with “See more”.
- Counters: likes_count, comments_count.

### 5.3 Comments & 1‑Level Replies
- Comment on post; reply to a top‑level comment only.
- Enforce single nesting level; reject reply‑to‑reply attempts.
- Paginated top‑level comments; expandable replies.

### 5.4 Likes
- Like/unlike posts (MVP).
- (Optional later) Like/unlike comments/replies.
- Idempotent toggles and atomic counter updates.

### 5.5 Notifications (Real‑Time)
- Triggered on post liked and post commented.
- Store unread notifications and deliver over WebSocket if online.
- Mark‑as‑read endpoint and unread count.

### 5.6 Feeds
- Global feed: reverse chronological posts.
- Profile feed: posts filtered by owner_id.
- Pagination defaults: posts 20 (max 50); comments 10; replies 5.

### 5.7 Media
- MVP: accept a verified external image_url.
- Optional: presigned uploads via Media service; store public URL in post.

---

## 6. Non‑Functional Requirements

- Performance: p95 < 700 ms for feed with warm cache; WS latency < 200 ms intra‑region.
- Reliability: Redis Streams for at‑least‑once events; idempotent consumers.
- Scalability: Horizontally scalable stateless services.
- Security: strong hashing, JWT signing, refresh rotation, CSRF for refresh, rate limits.
- Maintainability: strict service boundaries; generated clients; small shared libs.
- Portability: local dev with Docker Compose; prod‑ready container images.

---

## 7. Security Requirements

- Password hashing: Argon2id (preferred) or bcrypt.
- JWT: RS256/EdDSA, short TTL (10–15 min), key rotation support.
- Refresh: HttpOnly, Secure, SameSite=Strict cookies; rotation on each refresh; revoke on anomaly.
- CSRF: double‑submit token for refresh endpoint.
- Authorization: object ownership checks on write operations.
- Rate limits: login/register, posts, comments, likes via Redis.
- Input validation & sanitization; MIME allow‑list for images.
- Audit trail for auth events in Postgres.

---

## 8. Data Model

### 8.1 PostgreSQL Schema

users: id (UUID, PK), username (unique), email (unique), password_hash, avatar_url?, bio?, email_verified_at?, created_at, updated_at  
Indexes: (username), (email)

user_security: user_id (PK), mfa_enabled (bool), totp_secret?, last_password_rotated_at

sessions: id (UUID, PK), user_id (FK), device_id (UUID), user_agent, ip (INET), refresh_token_hash, expires_at, revoked_at?, created_at  
Indexes: (user_id, device_id), (expires_at)

privacy_settings (future): user_id (PK), profile_visibility ENUM('public','followers','private')

audit_log (optional): id (UUID), user_id?, action, meta (JSONB), created_at

### 8.2 MongoDB Collections

posts: _id, post_id(ULID/UUID), owner_id(UUID string), title, description, image_url?, likes_count, comments_count, created_at, updated_at  
Indexes: {{created_at:-1}}, {{owner_id:1, created_at:-1}}

post_likes: _id, post_id, user_id, created_at  
Unique Index: {{post_id:1, user_id:1}}

comments: _id, comment_id, post_id, author_id, parent_comment_id?, content, likes_count, created_at, updated_at  
Indexes: {{post_id:1, created_at:-1}}, {{parent_comment_id:1, created_at:1}}

comment_likes (optional): _id, comment_id, user_id, created_at  
Unique Index: {{comment_id:1, user_id:1}}

notifications: _id, notification_id, recipient_id, actor_id, type('post_liked'|'post_commented'), post_id, comment_id?, is_read, created_at  
Indexes: {{recipient_id:1, created_at:-1}}, {{recipient_id:1, is_read:1}}

---

## 9. Events & Real‑Time Design

### 9.1 Redis Streams
- Streams: events:post.liked, events:comment.created
- Producers: Posts (likes), Comments (creation)
- Consumer Groups: Notifications service (at‑least‑once)

### 9.2 Event Contracts

post.liked: event, post_id, post_owner_id, actor_id, created_at(ISO), dedupe_key  
comment.created: event, post_id, post_owner_id, comment_id, actor_id, is_reply(bool), created_at(ISO), dedupe_key

### 9.3 Idempotency & Error Handling
- Producers: Publish once per state change; include dedupe_key (e.g., hash of fields).
- Consumers: Upsert notifications using (event_type, actor_id, target_id, time_bucket) or dedupe_key.
- Retries: Use consumer group pending list; DLQ for poison events; alert on DLQ growth.

---

## 10. API Contracts (High‑Level)

All endpoints are behind Gateway and require Authorization unless noted.

### 10.1 Auth Service
- POST /auth/register
- POST /auth/login
- POST /auth/refresh (CSRF)
- POST /auth/logout
- POST /auth/logout-all
- POST /auth/request-password-reset, POST /auth/reset-password
- POST /auth/verify-email

### 10.2 Profile Reads
- GET /profiles/:username
- PATCH /profiles/me (avatar_url, bio)

### 10.3 Posts Service
- POST /posts
- GET /posts/:post_id
- PATCH /posts/:post_id (owner)
- DELETE /posts/:post_id (owner)
- GET /feed?page&limit
- GET /profiles/:username/posts?page&limit
- POST /posts/:post_id/like
- DELETE /posts/:post_id/like

### 10.4 Comments Service
- POST /posts/:post_id/comments
- GET /posts/:post_id/comments?page&limit
- POST /comments/:comment_id/replies
- GET /comments/:comment_id/replies?page&limit
- (Optional) POST/DELETE /comments/:comment_id/like

### 10.5 Notifications Service
- GET /notifications?is_read=false&page&limit
- POST /notifications/:notification_id/read
- WS /ws/notifications?access_token=...

### 10.6 Gateway
- JWT verification, CORS, rate limits, request ID propagation.

---

## 11. WebSocket Contract

Connect: GET /ws/notifications?access_token=...

Server → Client messages:
- type: post_commented — fields: notification_id, actor {{id, username, avatar_url}}, post {{id, title}}, comment {{id, excerpt}}, created_at
- type: post_liked — fields: notification_id, actor {{...}}, post {{id, title}}, created_at
- type: keepalive — fields: ts

Client acks optional; read/unread via REST.

---

## 12. Caching & Rate Limiting

Caching:
- Post detail & counts: Redis TTL ≈ 60s.
- Unread notification count: Redis hash by user_id; reconcile from Mongo on login.

Rate limits (Redis):
- Login: 5/min/IP + 10/min/account.
- Posts: 10/min/user.
- Comments: 30/min/user.
- Likes: 10/sec burst, 60/min.

---

## 13. Observability

- Logs: JSON (service, route, status, user_id, request_id, duration).
- Metrics: latency p50/p95/p99, error rate, Redis stream lag, DB ops, WS connections.
- Health: /health/live (process), /health/ready (deps).
- Tracing (optional): OpenTelemetry across gateway → services.

---

## 14. Deployment & Environments

- Local dev: Docker Compose for Postgres, MongoDB, Redis, services, and web.
- Staging/Prod: Container images built from monorepo; env‑only configuration; secrets in secret manager.
- Versioning: monorepo tag vX.Y.Z; per‑service images tagged service:vX.Y.Z.

---

## 15. Risks & Mitigations

- Counter drift: atomic increments + nightly reconciliation job.
- WS scale: shard by user hash; backpressure; notify rate limits.
- Cross‑DB consistency: opaque UUID references; avoid cross‑DB transactions.
- Monorepo sprawl: path‑filtered CI; codeowners; minimal shared libs.

---

## 16. Acceptance Criteria (MVP)

1) Auth works end‑to‑end (register/login/refresh/logout); sessions rotate correctly.  
2) Posts render with image preview card; feeds paginate.  
3) Comments and one‑level replies work; deeper nesting rejected.  
4) Likes are idempotent and counters remain correct.  
5) Real‑time notifications for post likes and post comments are pushed over WS and persisted.  
6) Profile page lists the user’s posts with pagination.

---


# Social Media Platform — Implementation Plan (Monorepo)

**Date:** 2025-08-20

## 17. Implementation Plan

### 17.1 Phases & Milestones

Phase 0 — Foundations  
- Repos/dirs, Compose, health endpoints, pre‑commit hooks, lint/type/test.  
- Alembic baseline; Mongo index bootstrap; .env examples.  
**Exit:** compose up is green; all /health endpoints return 200.

Phase 1 — Identity & Sessions (Postgres)  
- Register, login, refresh (CSRF), logout, sessions, Argon2id.  
- Gateway JWT verification; CORS; rate limits.  
- Web: minimal login/register storing access token in memory.  
**Exit:** E2E auth; invalid tokens rejected.

Phase 2 — Posts (Mongo)  
- Post CRUD; global & profile feeds; counters; preview card UX.  
**Exit:** Auth user can create/edit/delete own posts and see feeds.

Phase 3 — Comments & 1‑Level Replies (Mongo)  
- Endpoints for comments and replies; enforce one‑level; pagination.  
- Update post comments_count atomically.  
**Exit:** Comments & replies functional; counts correct.

Phase 4 — Likes + Events (Redis Streams)  
- Post like/unlike; unique post_likes; atomic likes_count.  
- Produce events:post.liked.  
**Exit:** Idempotent likes; events produced; consumer test passes.

Phase 5 — Notifications + WebSockets  
- Consume events:post.liked & events:comment.created; persist notifications.  
- WS endpoint; unread/read REST; web bell & badge.  
**Exit:** Real‑time notifications delivered when online; persisted when offline.

Phase 6 — Security Hardening & Ops  
- Email verification, password reset, optional TOTP.  
- Rate limits tuned; ownership checks audited; input validation tightened.  
- Dashboards; backups; restore rehearsal.  
**Exit:** Security checklist passes; ops dashboards live.

Phase 7 — Polish & Deferred Items  
- UX polish, accessibility; empty states; optional comment/reply likes; media presigned uploads.  
**Exit:** MVP feature‑complete and user‑friendly.

### 17.2 Team Roles & RACI

| Area | Owner | Support | Accountable | Consulted | Informed |
|---|---|---|---|---|---|
| Auth + Sessions | Backend Dev A | Dev B | Tech Lead | Frontend | Team |
| Posts Service | Backend Dev B | Dev C | Tech Lead | Frontend | Team |
| Comments Service | Backend Dev C | Dev B | Tech Lead | Frontend | Team |
| Notifications + WS | Backend Dev D | Dev A | Tech Lead | Frontend | Team |
| Gateway + DevEx | Tech Lead | Dev D | PM/Lead | All | Team |
| Frontend (web) | Frontend Dev | Backend A-D | Tech Lead | PM/Lead | Team |
| CI/CD & Compose | DevOps‑minded Dev | Tech Lead | PM/Lead | All | Team |

### 17.3 Branching, CI/CD, and Versioning

- Branching: trunk‑based; short feature branches; PR reviews; codeowners per folder.
- CI: path‑filtered builds/tests per service; contract generation/check; compose smoke E2E.
- Artifacts: per‑service Docker images; layer caching; optional SBOM scans.
- Versioning: tag monorepo (vX.Y.Z); publish images `service:vX.Y.Z`.

### 17.4 QA & Testing Strategy

- Unit tests: validation, ownership, counters.
- Component tests: service endpoints with test containers.
- Contract tests: Gateway ↔ services; generated clients validated.
- E2E tests: login → create post → comment → like → notification.
- Load tests: like/comment bursts; WS fan‑out sanity.
- Seed data: minimal fixtures for dev and CI.

### 17.5 Release & Go‑Live Checklist

- Secrets configured; keys rotated; dual‑key window for JWT.
- DB migrations applied; indexes verified.
- Health/ready checks green; dashboards baseline healthy.
- Rollback plan (image pinning) documented.
- Post‑release smoke passes (auth, post, like, comment, notification).

### 17.6 Documentation Artifacts

- ADRs: monorepo choice, polyglot persistence, JWT+refresh, Redis Streams vs Pub/Sub.
- Architecture diagram: services, data, events.
- ERDs/logical diagrams: Postgres & Mongo.
- API reference (OpenAPI) published in /libs/contracts and gateway /docs.

### 17.7 Issue Templates

- Feature: background, acceptance criteria, API changes, telemetry, rollout.
- Bug: env, steps, expected/actual, logs/IDs, severity.
- Task/Chore: scope, owner, estimate, dependencies.

---

**End of Document**