# CODE REPOSITORY & STRUCTURE

## Repository Information

**Main Repository:** [GitHub URL - Podverse Mockup]
- **Project Type:** Full-stack podcast management platform
- **Technology Stack:** Next.js 15 + Flask + PostgreSQL + Redis
- **Branch Strategy:** 
  - `main` - Production-ready code
  - `develop` - Feature development and integration
  - `feature/*` - Individual feature branches
  - `hotfix/*` - Critical production fixes
- **Access:** 
  - **Admin:** Full repository access, deployment rights
  - **Developers:** Read/write access to assigned modules
  - **Reviewers:** Pull request review and approval rights

## Project Structure

```
podverse_mockup/
├── README.md                           # Main project documentation
├── .env.example                        # Environment variables template
├── docker-compose-admin.yml            # Docker services configuration
├── Dockerfile.admin_api                # Backend API container
├── Dockerfile.admin_database           # PostgreSQL database container
├── Dockerfile.admin_parse_service      # RSS parsing service container
├── Dockerfile.admin_web                # Frontend web container
│
├── backend/                            # Flask API Backend
│   ├── main.py                         # Application entry point
│   ├── config.py                       # Configuration management
│   ├── requirements.txt                # Python dependencies
│   ├── make_celery.py                  # Celery task configuration
│   ├── entrypoint.sh                   # Container startup script
│   │
│   ├── app/                            # Main application package
│   │   ├── __init__.py                 # Flask app factory
│   │   ├── extensions.py               # Flask extensions setup
│   │   │
│   │   ├── blueprints/                 # API route modules
│   │   │   ├── __init__.py             # Blueprint registration
│   │   │   ├── health/                 # Health check endpoints
│   │   │   ├── channel/                # Channel management API
│   │   │   ├── feed/                   # RSS feed management API
│   │   │   ├── item/                   # Episode management API
│   │   │   ├── stats/                  # Analytics API
│   │   │   ├── export_logs/            # Export tracking API
│   │   │   ├── report_builder/         # Custom reports API
│   │   │   └── docs/                   # API documentation
│   │   │
│   │   ├── models/                     # Database models
│   │   │   ├── __init__.py             # Model imports
│   │   │   ├── base.py                 # Base model class
│   │   │   ├── feed.py                 # RSS feed model
│   │   │   └── ...
│   │   │
│   │   ├── services/                   # Business logic services
│   │   │   └── data_export.py          # Export functionality
│   │   │
│   │   ├── tasks/                      # Background tasks
│   │   │   ├── __init__.py
│   │   │   └── export_task.py          # Export processing tasks
│   │   │
│   │   └── utils/                      # Utility modules
│   │       ├── auth.py                 # Authentication utilities
│   │       ├── redis_lock.py           # Distributed locking
│   │       └── ...
│   │
│   ├── openapi/                        # API documentation
│   │   ├── openapi.yaml                # OpenAPI specification
│   │   ├── bundled.yaml                # Bundled documentation
│   │   ├── components/                 # Reusable components
│   │   ├──paths/                      # API endpoint definitions
│   │   └── ...
│   │
│   ├── scripts/                        # Database seeding scripts
│   │   ├── seed_all.py                 # Complete database seeding
│   │   ├── seed_feed.py                # Feed data seeding
│   │   └── ...
│   │
│   ├── tests/                          # Test suite
│   │   ├── conftest.py                 # Test configuration
│   │   ├── pytest.ini                  # Pytest configuration
│   │   ├── fixtures/                   # Test fixtures
│   │   ├── unit/                       # Unit tests
│   │   └── integration/                # Integration tests
│   │
│   ├── exports/                        # Export file storage
│   └── logs/                           # Application logs
│
├── frontend/                           # Next.js Frontend
│   ├── package.json                    # Node.js dependencies
│   ├── next.config.js                  # Next.js configuration
│   ├── tailwind.config.js              # Tailwind CSS config
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── .env.local.example              # Frontend environment template
│   │
│   ├── app/                            # Next.js App Router
│   │   ├── layout.tsx                  # Root layout component
│   │   ├── page.tsx                    # Home page
│   │   ├── login.tsx                   # Authentication page
│   │   ├── not-found.tsx               # 404 error page
│   │   ├── ClientProviders.tsx         # Redux provider wrapper
│   │   │
│   │   ├── dashboard/                  # Admin dashboard
│   │   │   └── page.tsx                # Dashboard main page
│   │   │
│   │   ├── channels/                   # Channel management
│   │   │   └── [id]/                   # Dynamic channel pages
│   │   │       └── page.tsx
│   │   │
│   │   ├── rssfeed/                    # RSS feed management
│   │   │   ├── page.tsx                # Feed list page
│   │   │   └── FeedPageCont.tsx        # Feed page controller
│   │   │
│   │   ├── statistics/                 # Analytics dashboard
│   │   │   ├── page.tsx                # Stats main page
│   │   │   ├── ChannelSelector.tsx     # Channel selection
│   │   │   ├── StatsChart.tsx          # Chart components
│   │   │   └── ChannelStatsChart.tsx   # Channel-specific charts
│   │   │
│   │   ├── reports/                    # Report generation
│   │   │   └── page.tsx                # Reports page
│   │   │
│   │   └── api/                        # API route handlers
│   │       ├── health/                 # Health check API
│   │       ├── feeds/                  # Feed management API
│   │       ├── channels/               # Channel management API
│   │       ├── items/                  # Item management API
│   │       ├── stats/                  # Statistics API
│   │       └── ...
│   │
│   ├── components/                     # React components
│   │   ├── Sidebar.tsx                 # Navigation sidebar
│   │   ├── TopBar.tsx                  # Top navigation bar
│   │   ├── SearchFeed.tsx              # Feed search component
│   │   ├── AddRssFeedModal.tsx         # Add feed modal
│   │   │
│   │   ├── dashboard/                  # Dashboard components
│   │   │   ├── DashboardLayout.tsx     # Dashboard layout
│   │   │   ├── DashboardHeaderSection.tsx
│   │   │   ├── DashboardFeedSection.tsx
│   │   │   └── DashboardStatsSection.tsx
│   │   │
│   │   ├── channel/                    # Channel components
│   │   │   ├── ChannelLayout.tsx       # Channel page layout
│   │   │   ├── ChannelHeader.tsx       # Channel header
│   │   │   ├── ChannelStats.tsx        # Channel statistics
│   │   │   ├── EpisodeList.tsx         # Episode listing
│   │   │   └── EpisodeLogSection.tsx   # Episode logs
│   │   │
│   │   ├── rssfeed/                    # RSS feed components
│   │   │   ├── FeedTable.tsx           # Feed data table
│   │   │   ├── FeedTableRow.tsx        # Individual feed row
│   │   │   ├── FeedStatusBadge.tsx     # Status indicators
│   │   │   ├── FeedToolbar.tsx         # Feed actions toolbar
│   │   │   └── FeedExpandedRow.tsx     # Expanded feed details
│   │   │
│   │   └── reparsefeed/                # Reparse components
│   │       ├── ReparseFeed.tsx         # Reparse functionality
│   │       ├── ReparseButton.tsx       # Reparse action button
│   │       └── ReparseNotify.tsx       # Reparse notifications
│   │
│   ├── redux/                          # State management
│   │   ├── store.ts                    # Redux store configuration
│   │   ├── feedSlice.ts                # Feed state management
│   │   ├── channelslice.ts             # Channel state management
│   │   ├── batchChannelSlice.ts        # Batch channel operations
│   │   └── reparseSlice.ts             # Reparse state management
│   │
│   ├── types/                          # TypeScript type definitions
│   │   ├── types.ts                    # Common types
│   │   ├── feed.ts                     # Feed-related types
│   │   ├── channel.ts                  # Channel-related types
│   │   ├── item.ts                     # Item-related types
│   │   └── stats.ts                    # Statistics types
│   │
│   ├── hooks/                          # Custom React hooks
│   │   └── useDebounce.ts              # Debounce utility hook
│   │
│   ├── utils/                          # Utility functions
│   │   ├── cn.ts                       # Class name utilities
│   │   └── datetime.ts                 # Date/time utilities
│   │
│   ├── styles/                         # Styling
│   │   └── globals.css                 # Global CSS styles
│   │
│   ├── public/                         # Static assets
│   │   ├── data/                       # Static data files
│   │   │   ├── podcasts.json           # Sample podcast data
│   │   │   ├── genres.json             # Genre definitions
│   │   │   └── trending_podcasts.json  # Trending podcasts
│   │   ├── Podverse/                   # Brand assets
│   │   │   ├── Dark_Podverse_Logo.svg
│   │   │   ├── Light_Podverse_Logo.svg
│   │   │   └── Blue_Podverse_Logo.svg
│   │   └── icons/                      # UI icons
│   │
│   ├── middleware.js                   # Next.js middleware
│   └── jest.config.js                  # Testing configuration
│
├── podverse_db/                        # Database management
│   ├── database_schema.md              # Database schema documentation
│   ├── init_db.sql                     # Database initialization
│   └── migrations/                     # Database migrations
│       ├── migration_add_channel_columns.sql
│       ├── migration_add_export_logs.sql
│       ├── migration_add_feed_flag_status_errors.sql
│       ├── migration_add_item_columns.sql
│       └── migration_remove_podcast_index_id.sql
│
└── podverse-parse-service/             # RSS parsing service
    ├── index.js                        # Parse service entry point
    ├── package.json                    # Node.js dependencies
    └── package-lock.json               # Dependency lock file
```

## Key Files & Their Purpose

### **Configuration Files**
- **`docker-compose-admin.yml`**: Orchestrates all services (backend, frontend, database, Redis, parse service)
- **`backend/config.py`**: Flask application configuration for different environments
- **`frontend/next.config.js`**: Next.js framework configuration
- **`frontend/tailwind.config.js`**: CSS framework configuration
- **`.env.example`**: Environment variables template for all services

### **Application Entry Points**
- **`backend/main.py`**: Flask application startup and database initialization
- **`frontend/app/layout.tsx`**: Next.js root layout and global providers
- **`podverse-parse-service/index.js`**: RSS parsing service HTTP server

### **Core Backend Files**
- **`backend/app/__init__.py`**: Flask app factory and extension initialization
- **`backend/app/extensions.py`**: Database, serialization, and rate limiting setup
- **`backend/make_celery.py`**: Background task configuration and scheduling
- **`backend/app/blueprints/__init__.py`**: API route organization and registration

### **Database & Models**
- **`backend/app/models/`**: SQLAlchemy models for all database entities
- **`podverse_db/database_schema.md`**: Complete database schema documentation
- **`podverse_db/migrations/`**: Database schema evolution scripts

### **Frontend Core Files**
- **`frontend/app/ClientProviders.tsx`**: Redux store provider setup
- **`frontend/redux/store.ts`**: Redux store configuration and middleware
- **`frontend/redux/feedSlice.ts`**: Feed state management with RTK patterns
- **`frontend/types/`**: TypeScript type definitions for API contracts

### **API & Communication**
- **`frontend/app/api/`**: Next.js API route handlers for backend communication
- **`backend/app/blueprints/feed/routes.py`**: RSS feed management API endpoints
- **`backend/app/utils/auth.py`**: Auth0 JWT authentication and authorization
- **`backend/openapi/`**: API documentation and OpenAPI specifications

### **Background Processing**
- **`backend/app/tasks/export_task.py`**: Data export background tasks
- **`backend/app/services/data_export.py`**: Export business logic
- **`backend/app/utils/export_utils.py`**: Export file generation utilities

### **Testing & Quality**
- **`backend/tests/`**: Comprehensive test suite (unit, integration, fixtures)
- **`frontend/jest.config.js`**: Frontend testing configuration
- **`backend/pytest.ini`**: Backend testing configuration

### **Documentation & Scripts**
- **`README.md`**: Complete project documentation and setup guide
- **`backend/scripts/seed_all.py`**: Database seeding for development
- **`backend/openapi/README.md`**: API documentation guide

### **Security & Monitoring**
- **`backend/app/utils/security_headers.py`**: Security header configuration
- **`backend/app/utils/request_logger.py`**: Request logging and monitoring
- **`backend/app/utils/audit_decorators.py`**: Administrative action auditing
- **`backend/app/utils/limiter_utils.py`**: Rate limiting implementation
