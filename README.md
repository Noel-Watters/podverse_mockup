# Podverse Mockup

A comprehensive podcast management platform with admin dashboard, RSS feed management, and analytics capabilities.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Docker Usage](#docker-usage)
4. [Application Architecture](#application-architecture)
5. [Quick Start Guide](#quick-start-guide)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [API Documentation](#api-documentation)

## System Requirements

### Required Software Versions

| Component | Version | Notes |
|-----------|---------|-------|
| **Docker** | 20.10+ | Docker Compose included |
| **Node.js** | 18.0+ | For local development |
| **Python** | 3.12+ | For local development |
| **PostgreSQL** | 15+ | Via Docker or local install |
| **Redis** | 7.0+ | Via Docker or local install |

## Environment Setup

### Environment Files
```
podverse_mockup/
├── .env                    # Main environment variables
├── .env.example           # Main environment template
├── backend/
│   ├── .env               # Backend-specific environment variables
│   └── .env.example       # Backend environment template
└── frontend/
    ├── .env.local         # Frontend environment variables
    └── env.local.example  # Frontend environment template
```

### Quick Setup
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/env.local.example frontend/.env.local
```

### Step 4: Environment-Specific Overrides

### Environment Overrides
| Environment | Key Changes |
|-------------|-------------|
| **Staging** | `FLASK_ENV=staging`, `CORS_ORIGINS=https://staging.yourdomain.com`, `AUTH0_COOKIE_SECURE=true` |
| **Production** | `FLASK_ENV=production`, `CORS_ORIGINS=https://yourdomain.com`, `AUTH0_COOKIE_SECURE=true` |

### Security Notes
- Never commit `.env` files to version control
- Use different secrets for each environment
- Rotate secrets regularly
- Store production secrets in secure vaults

## Docker Usage

### Services Overview
| Service | Dockerfile | Base Image | Port | Purpose |
|---------|------------|------------|------|---------|
| **Backend** | `Dockerfile.backend` | `python:3.12-bookworm` | 8000 | Flask API server |
| **Frontend** | `Dockerfile.frontend` | `node:18-alpine` | 3000 | Next.js application |
| **Database** | `Dockerfile.database` | `postgres:15-alpine3.20` | 5432 | PostgreSQL database |
| **Parse Service** | `Dockerfile.perse_service` | `node:18-alpine` | 3001 | RSS parsing service |

### Common Commands
| Action | Command |
|--------|---------|
| Start all services | `docker-compose up -d` |
| Start specific services | `docker-compose up -d database redis backend` |
| View logs | `docker-compose logs -f backend` |
| Production deployment | `docker-compose --env-file .env.production up -d` |
| Scale services | `docker-compose up -d --scale celery=3` |

### Database Operations
| Operation | Command |
|-----------|---------|
| Run migrations | `docker-compose exec backend flask db upgrade` |
| Create migration | `docker-compose exec backend flask db migrate -m "Add new table"` |
| Seed data | `docker-compose exec backend python scripts/seed_all.py` |
| Backup database | `docker-compose exec database pg_dump -U podverse_admin podverse > backup.sql` |
| Restore database | `docker-compose exec -T database psql -U podverse_admin podverse < backup.sql` |

### Volumes
| Volume | Purpose | Location |
|--------|---------|----------|
| **Database data** | PostgreSQL data directory | Docker volume `pgdata` |
| **Application exports** | Export files | `./backend/exports/` |
| **Application logs** | Application logs | `./logs/` |

## Application Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Parse Service │
│   (Next.js)     │◄──►│   (Flask)       │◄──►│   (Node.js)     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 3001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth0         │    │   PostgreSQL    │    │     Redis       │
│   (External)    │    │   Port: 5432    │    │   Port: 6380    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Architecture

| Service | Technology | Purpose | Key Features |
|---------|------------|---------|--------------|
| **Frontend** | Next.js 15+ | Admin dashboard | Dashboard, RSS management, analytics |
| **Backend** | Flask + SQLAlchemy | REST API | CRUD operations, background tasks, security |
| **Database** | PostgreSQL 15 | Data storage | ACID compliance, JSON support, full-text search |
| **Redis** | Redis Stack | Caching & queue | Session storage, Celery broker, rate limiting |
| **Celery** | Celery + Redis | Background tasks | RSS parsing, data export, scheduled tasks |
| **Parse Service** | Node.js | RSS parsing | Feed validation, content extraction |

### Data Flow

#### Authentication Flow
```
1. User → Frontend Login Page
2. Frontend → Auth0 Authorization
3. Auth0 → User Consent
4. Auth0 → Frontend (JWT Token)
5. Frontend → Backend API (with JWT)
6. Backend → Auth0 (Token Validation)
7. Backend → Database (Authenticated Request)
```

#### RSS Feed Processing Flow
```
1. User → Frontend (Add RSS Feed)
2. Frontend → Backend API
3. Backend → Parse Service
4. Parse Service → RSS Feed URL
5. Parse Service → Backend (Parsed Data)
6. Backend → Database (Store Data)
7. Backend → Celery (Background Processing)
8. Celery → Database (Update Statistics)
```

### Security Architecture

| Security Layer | Implementation | Features |
|----------------|----------------|----------|
| **Authentication** | Auth0 Integration | JWT tokens, role-based access, session management |
| **API Security** | Rate limiting, CORS | Per-user limits, cross-origin protection, input validation |
| **Data Protection** | Encryption, audit logging | Data at rest/transit, security events, access controls |

## Quick Start Guide

### Prerequisites Check
```bash
docker --version
docker-compose --version
node --version  # Should be 18+
python3 --version  # Should be 3.12+
```

### Setup & Start
| Action | Command |
|--------|---------|
| Clone repository | `git clone 'https://github.com/Noel-Watters/podverse_mockup.git' && cd podverse_mockup` |
| Copy environment files | `cp .env.example .env && cp backend/.env.example backend/.env && cp frontend/env.local.example frontend/.env.local` |
| Edit environment files | `nano .env && nano backend/.env && nano frontend/.env.local` |
| Start services | `docker-compose up --build -d` |
| Check status | `docker-compose ps` |

### Verify Installation
```bash
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:3001
docker-compose exec database psql -U podverse_admin -d podverse -c "SELECT version();"
```

### Access Applications
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/admin/docs
- **Database**: localhost:5432
- **Redis**: localhost:6380

## Development Workflow

### Local Development
| Service | Setup | Command |
|---------|-------|---------|
| **Backend** | `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` | `export FLASK_APP=main.py && export FLASK_ENV=development && flask run --host=0.0.0.0 --port=8000` |
| **Frontend** | `cd frontend && npm install` | `npm run dev` |

### Database Operations
| Action | Command |
|--------|---------|
| Connect to database | `docker-compose exec database psql -U podverse_admin -d podverse` |
| Run migrations | `docker-compose exec backend flask db upgrade` |
| Seed data | `docker-compose exec backend python scripts/seed_all.py` |
| Reset database | `docker-compose down -v && docker-compose up -d database && docker-compose exec backend python scripts/seed_all.py` |

## Testing

### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── app/
│   │   ├── blueprints/      # API endpoint tests
│   │   ├── services/        # Business logic tests
│   │   └── utils/           # Utility function tests
├── integration/             # Integration tests
│   ├── blueprints/          # API integration tests
│   └── services/            # Service integration tests
└── fixtures/                # Test data and fixtures
```

### Test Commands
| Test Type | Command |
|-----------|---------|
| All tests | `docker-compose exec backend pytest` |
| Specific file | `docker-compose exec backend pytest tests/unit/app/blueprints/channel/test_channel_routes.py` |
| With coverage | `docker-compose exec backend pytest --cov=app tests/` |
| Frontend tests | `docker-compose exec frontend npm test` |
| Reset test database | `docker-compose exec backend pytest --setup-show` |
| Load test fixtures | `docker-compose exec backend python scripts/seed_all.py` |

## Deployment

### Production Checklist
| Category | Tasks |
|----------|-------|
| **Environment** | Set `FLASK_ENV=production`, configure production database, set up Auth0 production app, configure SSL certificates, set up monitoring |
| **Security** | Update all secrets and API keys, configure CORS for production domains, enable HTTPS enforcement, set up firewall rules, configure backup strategy |
| **Performance** | Configure database connection pooling, set up Redis clustering, configure Celery worker scaling, enable CDN for static assets, set up load balancing |

### Deployment Commands
| Action | Command |
|--------|---------|
| Production deployment | `docker-compose --env-file .env.production up -d` |
| Blue-green deployment | `docker-compose -f docker-compose.prod.yml up -d` |
| Rolling updates | `docker-compose pull && docker-compose up -d --no-deps backend` |

## Troubleshooting

### Common Issues
| Issue | Diagnostic Commands | Solution |
|-------|-------------------|----------|
| **Database Connection** | `docker-compose ps database`, `docker-compose logs database` | Check database status and logs |
| **Redis Connection** | `docker-compose ps redis`, `docker-compose exec backend python -c "import redis; r = redis.Redis.from_url('redis://redis:6379'); print(r.ping())"` | Verify Redis connectivity |
| **Auth0 Configuration** | `docker-compose exec backend env | grep AUTH0` | Check Auth0 environment variables |
| **Frontend Build** | `docker-compose build --no-cache frontend`, `docker-compose logs frontend` | Rebuild frontend and check logs |

### Log Locations
| Log Type | Command |
|----------|---------|
| Backend logs | `docker-compose logs -f backend` |
| Frontend logs | `docker-compose logs -f frontend` |
| Celery logs | `docker-compose logs -f celery` |
| Database logs | `docker-compose logs -f database` |
| Security audit logs | `./backend/logs/security_audit.log` |
| Application logs | `./backend/logs/app.log` |
| Export logs | `./backend/logs/export.log` |

### Performance Monitoring
| Action | Command |
|--------|---------|
| Resource usage | `docker stats` |
| Database performance | `docker-compose exec database psql -U podverse_admin -d podverse -c "SELECT * FROM pg_stat_activity;"` |
| Redis memory | `docker-compose exec redis redis-cli info memory` |

## API Documentation

### API Endpoints
| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Health check | None |
| `/admin` | GET | Admin health check | None |
| `/admin/channels` | GET | Channel management | JWT |
| `/admin/channels/export` | GET | Export channels | JWT |
| `/admin/channels/<id>` | GET | Get specific channel | JWT |
| `/admin/channels/by-feed` | GET | Get channels by feed | JWT |
| `/admin/feeds` | GET | RSS feed operations | JWT |
| `/admin/feeds/<id>` | GET | Get specific feed | JWT |
| `/admin/feeds/<id>/reparse` | POST | Reparse feed | JWT |
| `/admin/feeds/<id>/export` | GET | Export feed | JWT |
| `/admin/feeds/<id>/logs` | GET | Get feed logs | JWT |
| `/admin/feeds/export` | GET | Export all feeds | JWT |
| `/admin/feeds/bulk-update` | POST | Bulk update feeds | JWT |
| `/admin/feeds/bulk-reparse` | POST | Bulk reparse feeds | JWT |
| `/admin/feeds/auto-reparse-status` | GET | Auto reparse status | JWT |
| `/admin/items` | GET | Episode management | JWT |
| `/admin/items/<id>` | GET | Get specific item | JWT |
| `/admin/stats/channels` | GET | Channel statistics | JWT |
| `/admin/stats/channels/<id>` | GET | Specific channel stats | JWT |
| `/admin/stats/items` | GET | Item statistics | JWT |
| `/admin/stats/items/<id>` | GET | Specific item stats | JWT |
| `/admin/export_logs` | GET | Export logs | JWT |
| `/admin/export_logs/<id>` | GET | Get specific export log | JWT |
| `/admin/export_logs/<id>/download` | GET | Download export | JWT |
| `/admin/docs` | GET | API documentation | None |

### Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Rate Limiting
- **Default**: 1000 requests per hour per user
- **Custom**: Configurable via `DEFAULT_RATE_LIMIT` environment variable
- **Headers**: Rate limit information included in response headers

### Error Handling
| Status Code | Description |
|-------------|-------------|
| **400** | Bad Request (validation errors) |
| **401** | Unauthorized (invalid/missing token) |
| **403** | Forbidden (insufficient permissions) |
| **404** | Not Found (resource not found) |
| **429** | Too Many Requests (rate limit exceeded) |
| **500** | Internal Server Error (server errors) |

## Additional Resources

### Documentation
- [Application Flow Documentation](NOTES.md)
- [Database Schema](podverse_db/database_schema.md)
- [Backend API Documentation](backend/openapi/)

### External Services
- [Auth0 Documentation](https://auth0.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.org/)

### Support
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Report security issues privately

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Note**: This documentation is maintained alongside the codebase. For the most up-to-date information, always refer to the latest version in the repository.
