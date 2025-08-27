# Kanban Board API

A RESTful Kanban board application built with Django and Django REST Framework. This backend API provides a complete task management system with team collaboration features.

## Key Features
- **Board Management**: Create, update, and delete project boards
- **Task System**: Full CRUD operations for tasks within boards
- **Team Collaboration**: Add users to boards with assigned roles
- **User Assignment**: Assign tasks to specific team members
- **Comment System**: Discuss tasks with threaded comments
- **User Authentication**: Secure login and registration system
- **Role-based Access**: Control permissions through board membership

## Technical Stack
- **Backend**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL/SQLite
- **Authentication**: Token-based authentication
- **API Design**: RESTful architecture with ViewSets and Routers

## Setup Guide

### Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git
- PostgreSQL (optional, SQLite is used by default)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd kanban-board-api
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   Create a `.env` file in the project root:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   # For PostgreSQL:
   # DATABASE_URL=postgresql://username:password@localhost:5432/kanban_db
   ```

5. **Database Setup**
   ```bash
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate

   # Create a superuser (optional)
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   # If you have fixtures/sample data
   python manage.py loaddata sample_data.json
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at: `http://localhost:8000/`

### Quick Test
Test if the setup worked:
```bash
# Test the API endpoint
curl http://localhost:8000/api/boards/

# Or visit in browser
http://localhost:8000/admin/  # Django admin interface
```

### Database Configuration

#### Using SQLite (Default)
No additional setup required. The database file will be created automatically.

#### Using PostgreSQL
1. Install PostgreSQL and create a database:
   ```sql
   CREATE DATABASE kanban_db;
   CREATE USER kanban_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE kanban_db TO kanban_user;
   ```

2. Update your `.env` file:
   ```env
   DATABASE_URL=postgresql://kanban_user:your_password@localhost:5432/kanban_db
   ```

3. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

### Development Tools

#### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

#### Code Formatting
```bash
# Install development dependencies
pip install black flake8

# Format code
black .

# Check code style
flake8 .
```

## API Endpoints

### Authentication
- `POST /api/login/` - User authentication
- `POST /api/registration/` - User registration

### Boards
- `GET/POST /api/boards/` - List and create boards
- `GET/PUT/DELETE /api/boards/{id}/` - Board detail operations

### Tasks
- `GET/POST /api/tasks/` - Task management
- `GET /api/tasks/assigned-to-me/` - Tasks assigned to current user
- `GET /api/tasks/reviewing/` - Tasks where user is reviewer

### Board Users
- `POST /api/board-users/` - Add users to boards

### API Documentation
Visit `http://localhost:8000/api/docs/` for interactive API documentation (if configured).

## Project Structure

```
kanban-board-api/
├── kanban_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── boards/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── tasks/
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── users/
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── requirements.txt
├── manage.py
└── README.md
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   python manage.py runserver 8001  # Use different port
   ```

2. **Database connection errors**
   - Check your DATABASE_URL in .env
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - Verify database credentials

3. **Module not found errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows

   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Migration issues**
   ```bash
   # Reset migrations (development only!)
   python