Kanban Board API
A RESTful Kanban board application built with Django and Django REST Framework. This backend API provides a complete task management system with team collaboration features.

Key Features>>>>>>
Board Management: Create, update, and delete project boards
Task System: Full CRUD operations for tasks within boards
Team Collaboration: Add users to boards with assigned roles
User Assignment: Assign tasks to specific team members
Comment System: Discuss tasks with threaded comments
User Authentication: Secure login and registration system
Role-based Access: Control permissions through board membership
Technical Stack>>>>>>>
Backend: Django 4.x + Django REST Framework
Database: PostgreSQL/SQLite
Authentication: Token-based authentication
API Design: RESTful architecture with ViewSets and Routers



API Endpoints>>>>>>>
POST /api/login/ - User authentication
POST /api/registration/ - User registration
GET/POST /api/boards/ - List and create boards
GET/PUT/DELETE /api/boards/{id}/ - Board detail operations
GET/POST /api/tasks/ - Task management
GET /api/tasks/assigned-to-me/ - Tasks assigned to current user
GET /api/tasks/reviewing/ - Tasks where user is reviewer
POST /api/board-users/ - Add users to boards

Project Structure>>>>>>>>>
The application follows a modular design with separate views for:
Board operations (ViewSets)
Task management with custom endpoints
User authentication and registration
Comment system for tasks
Board user membership management
Perfect for team-based project management with clean, RESTful API design and scalable architecture.