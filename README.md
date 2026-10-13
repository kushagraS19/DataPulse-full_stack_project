# DataPulse — Data Analytics Platform

**Turn raw CSV data into meaningful insights.**

DataPulse is a full-stack data analytics platform designed to simplify dataset processing and exploration. It allows users to upload datasets, clean and analyze data, visualize patterns through charts, and generate insights through an interactive interface.

## Key Features

- **Dataset Processing:** Upload and process CSV datasets.
- **Data Cleaning:** Prepare raw data for analysis using Python data-processing libraries.
- **Interactive Visualizations:** Explore data through charts and graphical representations.
- **Data Analytics:** Analyze datasets to identify patterns, distributions, and relationships.
- **Automated Insights:** Generate useful insights from processed data.
- **Dashboards:** Present analytical results in an organized visual interface.
- **Authentication:** Secure user authentication and account management.
- **Workspaces and Projects:** Organize analytical work across projects and workspaces.
- **Backend API:** Handle authentication, datasets, analytics, dashboards, charts, and insights through a structured API.

## Tech Stack

| Layer                        | Technologies             |
| ---------------------------- | ------------------------ |
| Frontend                     | React, Vite, JavaScript  |
| Backend                      | Python, FastAPI          |
| Database                     | PostgreSQL               |
| Data Processing              | Pandas, NumPy            |
| ORM                          | SQLAlchemy               |
| Database Migrations          | Alembic                  |
| Validation and Configuration | Pydantic                 |
| Authentication               | JWT-based authentication |
| Testing                      | Pytest                   |

## Architecture

DataPulse follows a frontend–backend architecture.

1. **Frontend:** React provides the user interface for managing datasets and exploring analytical results.
2. **Backend:** FastAPI exposes APIs for authentication, data processing, analytics, and application features.
3. **Processing Layer:** Pandas and NumPy handle data manipulation and numerical operations.
4. **Database:** PostgreSQL stores application data, while SQLAlchemy manages database interactions.
5. **Visualization:** Processed analytical results are presented through charts and dashboards.

## Project Structure

The project is organized into separate frontend and backend applications.

```text
DataPulse/
├── frontend/       # React + Vite application
├── backend/        # FastAPI application
├── README.md
└── .gitignore
```

_Note: Adjust the directory names above if your actual repository structure differs._

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.10+
- PostgreSQL

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DataPulse
```

### 2. Configure the Backend

Navigate to the backend directory and install the dependencies:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using the configuration required by your backend:

```env
DATABASE_URL=your_postgresql_connection_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OTP_SECRET=your_otp_secret
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=your_verified_sender
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
```

Replace the example values with your local configuration. Never commit real credentials or API keys.

Run database migrations using the project's configured Alembic setup, then start the FastAPI server using your application's actual entry-point module.

### 3. Configure the Frontend

Open a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

> The directory names, environment values, migration command, and FastAPI entry point should be checked against the actual repository before using these instructions.

## Testing

The backend test suite has previously passed **12 tests**.

Run the test suite from the backend environment:

```bash
pytest
```

## Why DataPulse?

DataPulse brings data preparation, analysis, visualization, and insight generation into one application. Its modular backend and separate frontend make it a practical demonstration of full-stack development, API design, database integration, and Python-based data processing.

## Current Status

DataPulse is developed and run locally. It is not presented as a publicly deployed service.

## Author

**Kushagra Saini**

Full-Stack Developer | Python | React | FastAPI | PostgreSQL
