# Job Board MCP Server

A production-ready FastMCP server with a web dashboard for managing job listings. Built with FastAPI, SQLAlchemy, and modern Python tooling.

**Made and maintained by [The A-Tech Corporation PTY LTD](https://theatechcorporation.com)**


## Features

- **MCP Server**: Full Model Context Protocol server with job search, applications, and management tools
- **Web Dashboard**: Clean, responsive web interface for managing jobs and applications
- **AI Assistant**: Ollama-powered chat interface for natural language job queries
- **Database**: SQLite by default, PostgreSQL supported for production
- **RESTful API**: Full CRUD API for programmatic access
- **Extensible**: Easy to customize and extend with your own data

## Project Structure

```
job-board-mcp/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management (Pydantic Settings)
│   ├── database.py            # Database connection and session management
│   ├── dependencies.py        # Shared FastAPI dependencies
│   ├── models.py              # SQLAlchemy models (Job, JobApplication)
│   ├── mcp_server.py          # MCP server implementation
│   ├── web_server.py          # FastAPI web server entry point
│   ├── cli.py                 # CLI commands (init_db, reset_db, seed)
│   ├── routers/
│   │   ├── __init__.py        # Router exports
│   │   ├── pages.py           # HTML page routes
│   │   ├── jobs.py            # Job API routes
│   │   ├── applications.py    # Application API routes
│   │   └── ai.py              # AI assistant routes
│   └── services/
│       ├── __init__.py
│       ├── crud.py            # Database CRUD operations
│       ├── ai_assistant.py    # Ollama AI integration
│       ├── mcp_executor.py    # MCP tool execution for AI
│       └── seed.py            # Sample data for development
├── static/
│   └── css/
│       └── styles.css         # Dashboard styles
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── job_form.html
│   ├── job_detail.html
│   ├── applications.html
│   ├── application_detail.html
│   ├── statistics.html
│   └── ai_assistant.html
├── examples/                   # Example scripts
│   ├── create_job_via_mcp.py
│   ├── import_jobs_csv.py
│   ├── rest_api_example.py
│   └── test_mcp_client.py
├── pyproject.toml              # Project dependencies
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image
└── README.md
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd job-board-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database

```bash
job-board-init
# Or: python -m app.cli init_db
```

### 4. Run Servers

Run the web dashboard:
```bash
job-board-web
# Or: python -m app.web_server
```

Run the MCP server:
```bash
job-board-mcp
# Or: python -m app.mcp_server
```

### 5. Access Dashboard

Open http://localhost:8000 in your browser.

## CLI Commands

| Command | Description |
|---------|-------------|
| `job-board-init` | Initialize database with tables and seed data |
| `job-board-init init_db` | Initialize database only |
| `job-board-init reset_db` | Reset database (deletes all data) |
| `job-board-init seed` | Seed database with sample data |
| `job-board-web` | Start the web dashboard server |
| `job-board-mcp` | Start the MCP server |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./job_board.db` | Database connection string |
| `WEB_HOST` | `0.0.0.0` | Web server host |
| `WEB_PORT` | `8000` | Web server port |
| `MCP_SERVER_NAME` | `Mackay Job Board MCP` | MCP server display name |
| `DEBUG` | `true` | Enable debug mode |
| `ENABLE_AUTH` | `false` | Enable dashboard authentication |
| `ADMIN_USERNAME` | `admin` | Admin username (if auth enabled) |
| `ADMIN_PASSWORD` | `changeme` | Admin password (if auth enabled) |
| `SECRET_KEY` | *(auto-generated)* | JWT secret key |
| `DEFAULT_LOCATION` | `Mackay` | Default job location |
| `ENABLE_SEED_DATA` | `true` | Load sample data on init |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API host |
| `OLLAMA_MODEL` | `qwen3.5:4b` | Ollama model for AI assistant |

## MCP Tools

The MCP server provides these tools:

### Job Search & Discovery
- `get_jobs` - Get jobs with filters (location, industry, type, remote)
- `search_jobs` - Keyword search across title, company, description
- `get_job_details` - Get full job details by ID
- `get_job_categories` - List available industries, types, levels
- `get_job_stats` - Job board statistics

### Applications
- `apply_for_job` - Submit a job application
- `get_application_status` - Check application status

### Admin Tools
- `create_job_listing` - Create a new job
- `update_job_listing` - Update an existing job
- `delete_job_listing` - Delete a job

## Web Dashboard

### Pages
- **Dashboard** (`/`) - Overview with stats and recent activity
- **Jobs** (`/jobs`) - List, search, and filter jobs
- **Job Detail** (`/jobs/{id}`) - View job details and applications
- **New Job** (`/jobs/new`) - Create a new job listing
- **Edit Job** (`/jobs/{id}/edit`) - Modify an existing job
- **Applications** (`/applications`) - View all applications
- **Application Detail** (`/applications/{id}`) - View application details
- **Statistics** (`/statistics`) - Job market statistics
- **AI Assistant** (`/ai-assistant`) - Chat interface for job queries

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Create a new job |
| POST | `/api/jobs/{id}/update` | Update a job |
| POST | `/api/jobs/{id}/delete` | Delete a job |
| POST | `/api/jobs/{id}/toggle` | Toggle job active status |
| POST | `/api/applications/{id}/status` | Update application status |
| POST | `/api/ai/chat` | Chat with AI assistant |
| POST | `/api/ai/clear` | Clear conversation history |
| GET | `/api/ai/health` | Check AI service health |

## Database Schema

### Job
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| title | String | Job title |
| company | String | Company name |
| location | String | Job location |
| job_type | String | Full-time, Part-time, Contract, Casual |
| salary_range | String | Salary information |
| description | Text | Full job description |
| requirements | JSON | List of requirements |
| benefits | JSON | List of benefits |
| posted_date | DateTime | When posted |
| expiry_date | DateTime | Application deadline |
| industry | String | Industry category |
| experience_level | String | Entry, Mid, Senior, Executive |
| remote_friendly | Boolean | Remote work option |
| applications_count | Integer | Number of applications |
| is_active | Boolean | Job is accepting applications |

### JobApplication
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| job_id | UUID | Reference to job |
| applicant_name | String | Applicant's name |
| applicant_email | String | Applicant's email |
| applicant_phone | String | Phone number |
| cover_letter | Text | Cover letter text |
| resume_link | String | URL to resume |
| applied_date | DateTime | When applied |
| status | String | pending, reviewing, interviewing, offered, rejected |
| notes | Text | Internal notes |

## AI Assistant

The dashboard includes an AI assistant powered by Ollama that can:
- Search and filter jobs using natural language
- Get job recommendations
- Create job listings through conversation
- Answer questions about the job board

### Setup Ollama

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull qwen3.5:4b`
3. Set environment variables:
   ```bash
   export OLLAMA_HOST=http://localhost:11434
   export OLLAMA_MODEL=qwen3.5:4b
   ```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black app/
ruff check app/
```

## Deployment

### Using Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using PostgreSQL

1. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/job_board
   ```
2. Install PostgreSQL driver:
   ```bash
   pip install -e ".[postgres]"
   ```

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `ENABLE_AUTH=true` and configure credentials
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=false`
- [ ] Configure HTTPS/reverse proxy
- [ ] Set up database backups
- [ ] Configure `OLLAMA_HOST` if using AI assistant

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

Made with care by [The A-Tech Corporation PTY LTD](https://theatechcorporation.com)