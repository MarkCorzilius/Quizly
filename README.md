# 📦 Quizly Backend API

## 📌 Description

Quizly is an AI-powered quiz generator that turns YouTube videos into interactive quizzes. Using the Gemini API, Quizly analyzes video content and automatically generates a quiz with 10 questions.

## ⚙️ Tech Stack

* Python 3.14.0
* Django 6.0.6
* Django REST Framework 3.17.1
* SQLite 3.51.0
* Google Gemini API

## 🚀 Quickstart Instructions

Clone the repository
```bash
git clone <your-repo-url>
```

Create a virtual environment
```bash
python -m venv venv
```

Activate Virtual Environment

Windows:
```bash
venv\Scripts\activate
```

Mac:
```bash
source venv/bin/activate
```

Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔑 Environment Variables
Quizly uses the Google Gemini API to generate quizzes. Create a .env file in the project root and add your Gemini API key:
```env
GEMINI_API_KEY=your-gemini-api-key
```

Run Database Migrations
```bash
python manage.py migrate
```

Create Superuser
```bash
python manage.py createsuperuser
```

Run Server
```bash
python manage.py runserver
```

## 📡 API Overview

🔐 Authentication (JWT)

Method	Endpoint	Description
POST	/api/register/	Register a new user
POST	/api/login/	Log in a user
POST	/api/logout/	Log out the current user
POST	/api/token/refresh/	Refresh the access token

📊 Quizzes Management

Method	Endpoint	Description
GET	/api/quizzes/	Get all quizzes
POST	/api/quizzes/	Generate a new quiz from a YouTube video
GET	/api/quizzes/{id}/	Get a specific quiz
PATCH	/api/quizzes/{id}/	Update a quiz
DELETE	/api/quizzes/{id}/	Delete a quiz

🤖 AI Quiz Generation

Quizly uses the Google Gemini API to analyze YouTube video content and generate 10 quiz questions automatically.

Simply provide a YouTube video URL and Quizly creates an interactive quiz based on the video’s content.

🔒 Authentication

The API uses JWT authentication with HTTP-only cookies for secure token storage.

Access tokens are used to authenticate API requests, while refresh tokens can be used to obtain new access tokens.

## 🧪 Testing

Run the test suite with:
```bash
python manage.py test
```
