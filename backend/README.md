# SBOM Analyzer - Backend Foundation

This is the backend service foundation for the **AI-Powered Software Supply Chain Risk Intelligence Platform**. It is constructed using the Flask Application Factory Pattern, SQLAlchemy ORM, and MySQL.

## Project Structure

```text
backend/
├── app/
│   ├── config/          # Configurations mapping per environment
│   ├── database/        # Database adapter and bindings
│   ├── models/          # Declarative SQLAlchemy models
│   ├── repositories/    # Generic and concrete data retrieval layer
│   ├── services/        # Service logic skeletons (no business rules yet)
│   ├── schemas/         # Pydantic input validation DTOs
│   ├── routes/          # API route blueprints
│   ├── middlewares/     # Auth checks & global error handling
│   └── utils/           # Shared helper modules (JWT, crypto, uploads)
├── logs/                # Rotating files logs directory
├── uploads/             # File uploads temporary folder
├── wsgi.py              # WSGI server entrypoint
├── requirements.txt     # Backend python dependencies
└── README.md            # This instruction file
```

## Running the Application

### 1. Environment Setup
Clone the repository, verify the folder path, and create a python virtual environment:
```bash
python -m venv venv
# On Windows powershell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Dependencies Installation
```bash
pip install -r requirements.txt
```

### 3. Local Environment variables
Copy the template file `.env.example` to `.env` and fill out your specific configuration parameters (e.g. database credentials):
```bash
cp .env.example .env
```

### 4. Running the Dev Server
Start the application locally using the entrypoint script:
```bash
python wsgi.py
```
The server will boot by default on [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Database Migrations

This platform uses **Flask-Migrate** (built on top of **Alembic**) for executing declarative database migrations.

### Initialize Migrations
If migrating for the first time, execute the initialization:
```bash
flask db init
```

### Generating new Migrations
Whenever SQLAlchemy models are updated, generate a new version schema:
```bash
flask db migrate -m "Description of model changes"
```

### Applying Migrations
Apply version scripts directly to the target MySQL instance:
```bash
flask db upgrade
```

## Coding Standards
- **Clean Separation**: Routes call Services; Services call Repositories and Agents; Repositories query database Models directly.
- **Transactions**: Never write inline MySQL query parameters inside router code. Always route data queries via repository decorators and context sessions.
- **Errors**: Raise custom exceptions from `app.middlewares.error_middleware` to return standardized JSON responses automatically.
- **Observability**: Avoid python print statements. Use `current_app.logger` or specific loggers (`app`, `security`, `error`, `ai`) created inside `app/utils/logger.py`.
