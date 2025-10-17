# Tournament Browser - Tournament Management System

**Tournament Browser** is a modern web application for creating, managing, and participating in tournaments. It combines tournament management features, invitation system, and social networking, allowing users to organize their own tournaments and join tournaments with friends.

## ℹ️ Note

When using the application in development version, the first access may require Supabase configuration. The application can run in development mode without a database, but some features will be limited.

I recommend first configuring Supabase or running the application in development mode, then familiarizing yourself with the application's feature documentation and Tournament Browser capabilities.

## Technologies and Stack

### Frontend (HTML/CSS)
- **Framework**: Jinja2 Templates
- **Styling**: Custom CSS (Bootstrap-style)
- **Interactivity**: Server-side rendering with forms

### Backend (FastAPI)
- **Framework**: FastAPI (Python 3.8+)
- **Deployment**: Local development
- **API**: RESTful endpoints + HTML rendering

### Database (Supabase)
- **Engine**: PostgreSQL
- **Storage**: Supabase Storage
- **Authorization**: Supabase Auth
- **Real-time**: Real-time change handling

## Permission System

Tournament Browser uses the following permission system:

### User Levels

**Guests (not logged in):**
- No access to application features
- Ability to register or log in

**Logged-in users:**
- Creating own tournaments
- Managing own tournaments
- Joining public tournaments
- Accepting tournament invitations
- Inviting friends to tournaments
- Browsing own tournaments
- Searching users
- Sending friend invitations

### Tournament Permissions

**Tournament creator:**
- Editing and deleting tournament
- Managing participants
- Inviting players
- Setting tournament as public/private

**Tournament participants:**
- Viewing tournament details
- Viewing participant list
- Browsing matches

**Other users:**
- No access to private tournaments
- Ability to join public tournaments

### Social Relationships
- Sending and accepting friend invitations
- Ability to remove friends
- Inviting friends to tournaments
- Invitation notification system

## Features

- **Tournament Management** - Creating, editing, deleting tournaments
- **Invitation System** - Inviting players and friends to tournaments
- **Joining Tournaments** - Browsing and joining public tournaments
- **User Dashboard** - Overview of all user tournaments
- **Tournament Details** - Complete tournament information, participants, and matches
- **Friends System** - Adding friends and managing relationships
- **Responsive Interface** - Works on all devices
- **REST API** - Complete API for frontend integration

## Installation and Setup

### Requirements
- Python 3.8+
- pip (Python Package Manager)
- Supabase account (optional for development mode)

### Local Setup

**Backend**

Create Python virtual environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure `.env` file in `backend/` directory (optional):
```env
SUPABASE_URL=Your_Supabase_URL
SUPABASE_KEY=Your_Supabase_anon_key
ENV=development
```

Run server:
```bash
uvicorn main:app --reload
```

**Development Mode (without Supabase)**
```bash
cd backend
uvicorn main:app --reload
```

The application will be available at: `http://localhost:8000`

## Deployment

### Backend (Local)
- Run `uvicorn main:app --reload` in backend directory
- Application available at `http://localhost:8000`

### Supabase Configuration (Production)
1. Create project in Supabase
2. Configure tables according to database schema
3. Add SUPABASE_URL and SUPABASE_KEY environment variables
4. Run application with full functionality

## Project Structure

```
tournament_browser/
├── README.md
└── backend/
    ├── main.py                 # Main FastAPI application file
    ├── requirements.txt        # Python dependencies
    ├── config/
    │   ├── __init__.py
    │   └── config.py          # Application configuration and settings
    ├── db/
    │   ├── __init__.py
    │   └── supabase.py        # Database connections
    ├── endpoints/
    │   ├── __init__.py
    │   ├── menu.py            # Main menu endpoints
    │   ├── tournament.py      # Tournament management endpoints
    │   ├── tournament_list.py # Tournament listing endpoints
    │   └── user_auth.py       # Authentication endpoints
    ├── entities/
    │   ├── __init__.py
    │   └── users.py           # User data models
    ├── repositories/
    │   ├── __init__.py
    │   ├── friend_repository.py    # Friend data operations
    │   ├── tournament_repository.py # Tournament data operations
    │   └── user_repository.py      # User data operations
    ├── schemas/
    │   ├── __init__.py
    │   ├── friend.py          # Friend Pydantic schemas
    │   ├── login_form.py      # Authentication schemas
    │   ├── tournaments.py     # Tournament schemas
    │   └── user.py            # User schemas
    ├── services/
    │   ├── __init__.py
    │   ├── friend_service.py   # Friend business logic
    │   ├── tournament.py      # Tournament business logic
    │   └── user_service.py    # User business logic
    ├── templates/
    │   ├── edit_tourn.html    # Tournament editing template
    │   ├── edit.html          # General editing template
    │   ├── error.html         # Error template
    │   ├── login.html         # Login template
    │   ├── menu.html          # Main menu template
    │   ├── my_tournaments.html # My tournaments template
    │   ├── register.html      # Registration template
    │   ├── tournament_details.html # Tournament details template
    │   ├── tournament_join.html # Tournament joining template
    │   └── your_tourn.html    # Created tournaments template
    ├── styles/
    │   ├── auth.css           # Authentication styles
    │   ├── main.css           # Main application styles
    │   ├── menu.css           # Menu styles
    │   └── tournament.css     # Tournament styles
    └── utils/
        ├── __init__.py
        └── auth.py            # Authentication utility functions
```

## API Documentation

### HTML Endpoints
- `GET /` - API homepage
- `GET /tournament_list/` - Tournament joining page
- `GET /tournament_list/my-tournaments` - My tournaments
- `GET /tournament/{id}/details` - Tournament details

### REST API Endpoints
- `GET /tournament_list/api/available` - Available tournaments and invitations
- `POST /tournament_list/api/{id}/join` - Join tournament
- `POST /tournament_list/api/{id}/respond` - Respond to invitation
- `GET /tournament_list/api/my-tournaments` - My tournaments (API)
- `GET /tournament/api/{id}/details` - Tournament details (API)

## Author

**Dariusz Marecik**
- Email: marecik.dariusz@gmail.com
