# Event Management System - Django + DRF

## Overview
This project provides a RESTful API for event management with:
- Events (create, list, retrieve, update, delete)
- RSVP (Going / Maybe / Not Going)
- Reviews (rating + comment)
- JWT authentication (SimpleJWT)
- Pagination, search and filtering
- Custom permissions: only organizer can edit/delete; private events accessible only to invited users

## Quick setup (local)
1. Create virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Run server:
   ```bash
   python manage.py runserver
   ```
4. API endpoints:
   - `POST /api/auth/token/` -> get JWT tokens (access & refresh)
   - `GET /api/events/` -> list events (public + invited)
   - `POST /api/events/` -> create event (authenticated)
   - `POST /api/events/{id}/rsvp/` -> RSVP (authenticated)
   - `PATCH /api/events/{event_id}/rsvp/{user_id}/` -> update RSVP
   - `POST /api/events/{event_id}/reviews/` -> add review
   - `GET /api/events/{id}/reviews/` -> list reviews

## Notes
- Settings use SQLite and console email backend for development.
- To use media uploads, set MEDIA_ROOT and serve media in development (already configured).
- For production, set DEBUG=False and configure SECRET_KEY, allowed hosts, database, and email properly.

## Git
Initialize git, commit and push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - Event Management API"
# create repo on GitHub and push
git remote add origin <your_repo_url>
git push -u origin main
```
