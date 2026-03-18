This repository contains a complete AI-powered career guidance web application built with Python, Flask, SQLAlchemy, and Gemini AI. The app lets users register, complete a detailed career assessment, and receive a personalized career report with recommended roles, strengths, skill gaps, and a learning roadmap.

Project Structure
-----------------
career-guidance-ai/
  app.py               # Flask app entry point, routes, configuration
  database.py          # SQLAlchemy models and database helper functions
  ai_service.py        # AI integration (Gemini + fallback), prompt building, parsing
  config.py            # Optional configuration module (if present)
  requirements.txt     # Python dependencies
  Procfile             # Process definition for production (Gunicorn)
  .env.example         # Example environment config (no secrets)
  .gitignore           # Git ignore rules
  instance/            # Local database folder (SQLite)
    career_guidance.db # SQLite database (created locally, not committed)
  templates/           # Jinja2 templates
    index.html         # Landing page
    login.html         # Login page
    register.html      # Registration page
    dashboard.html     # User dashboard
    profile.html       # Profile page (if used)
    questions.html     # Career assessment form
    loading.html       # “Analyzing your assessment” loading screen
    results.html       # Career report / results page
  static/
    css/
      style.css        # Global styles and results page design
    js/
      main.js          # Global JS (if used)
      questions.js     # Assessment form logic (steps, validation, UX)
      results.js       # Renders AI results into cards, lists, and timeline

Main Features
-------------
- User registration, login, logout (Flask-Login)
- Dashboard showing user assessments and actions to start/continue
- 15-question multi-step career assessment:
  - Interests and preferred work environment
  - Skills (technical, communication, analytical, creative, leadership, detail)
  - Academic strengths and education level
  - Underutilized skills and personal definition of success
  - Motivations, values, and work-life balance
  - Career aspirations and transition timeline
- AI-powered analysis using Gemini (via server-side API):
  - Builds a structured prompt from all assessment answers
  - Sends prompt to Gemini and expects a JSON-only response
  - Parses and validates JSON before saving to the database
- Fallback analysis when AI is unavailable:
  - Predefined JSON structure with:
    - career_matches
    - top_strengths
    - skill_gaps
    - learning_roadmap
    - next_steps
    - personalized_advice
- Loading screen during processing with step-by-step animation
- Detailed results page:
  - Top career matches (title, match %, description, why it fits, salary, growth, skills)
  - Key strengths section
  - Skill gaps with priority and development suggestions
  - Multi-phase learning roadmap (phases, actions, resources)
  - Immediate next steps checklist
  - Personalized advice block
- Responsive layout and print-friendly report for PDF export
- Ready for deployment with Gunicorn and environment-based configuration

Data Model Overview (database.py)
---------------------------------
User model:
- id (Integer, primary key)
- email (String, unique, indexed)
- username (String, unique)
- password_hash (String, hashed password)
- created_at (DateTime)
- last_login (DateTime)
- Relationship to Assessment (one-to-many)

Assessment model:
- id (Integer, primary key)
- user_id (ForeignKey to users.id)
- status (String: in_progress, completed, error)
- progress (Integer 0–100)
- Question fields:
  - q1_interests (Text)
  - q2_environment (String)
  - q3_technical_skill (Integer)
  - q3_communication_skill (Integer)
  - q3_math_skill (Integer)
  - q3_creative_skill (Integer)
  - q3_leadership_skill (Integer)
  - q3_detail_skill (Integer)
  - q4_academic_subjects (String)
  - q5_underutilized_skills (Text)
  - q6_success_definition (String)
  - q7_motivation (String)
  - q8_handle_setbacks (String)
  - q9_priorities (Text)
  - q10_work_life_balance (Integer)
  - q11_mentorship (String)
  - q12_education_level (String)
  - q13_additional_education (String)
  - q14_career_aspirations (Text)
  - q15_transition_timeline (String)
- AI results fields:
  - results (Text, stores full JSON from AI)
  - ai_response (Text, optional raw AI content)
  - career_matches (Text, optional JSON subset)
  - skill_roadmap (Text, optional JSON subset)
  - recommended_courses (Text, optional JSON subset)
- Timestamps:
  - started_at (DateTime)
  - completed_at (DateTime)
  - last_updated (DateTime, auto-updated)

ChatHistory model (optional):
- id (Integer, primary key)
- assessment_id (ForeignKey to assessments.id)
- user_message (Text)
- ai_response (Text)
- created_at (DateTime)

AI Service Overview (ai_service.py)
-----------------------------------
- Loads environment variables to determine AI provider
- Supports:
  - Gemini via the new google-genai SDK (Client-based)
  - Fallback mode for offline/demo usage

Key functions:
- analyze_career_assessment(assessment_data: Dict) -> Dict
  - Builds a structured prompt from the assessment data
  - Routes to Gemini or fallback depending on AI_PROVIDER
  - Returns a Python dictionary with the expected structure

- build_assessment_prompt(data: Dict) -> str
  - Creates a detailed career-profile prompt:
    - Interests and environment
    - Skills ratings
    - Academic background
    - Values and motivations
    - Priorities and timeline
    - Aspirations and constraints
  - Instructs the AI to respond with JSON only

- get_gemini_response(prompt: str) -> str
  - Uses google-genai Client to call:
    - client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
  - Returns response.text for parsing

- parse_ai_response(response: str) -> Dict
  - Handles responses wrapped in `````` fences
  - Extracts the JSON portion if necessary
  - Uses json.loads to convert to a dict
  - Validates required fields:
    - career_matches
    - top_strengths
    - skill_gaps
    - learning_roadmap
    - next_steps
  - If parsing or validation fails, falls back to generate_fallback_response

- generate_fallback_response() -> Dict
  - Returns a complete, static report:
    - Three generic but realistic career options
    - List of strengths
    - Skill gaps with priorities
    - Three-phase learning roadmap
    - Immediate next steps
    - A long-form advice paragraph

Application Flow
----------------
1) User registration and login
   - User creates an account, logs in, and is redirected to the dashboard.

2) Start or continue an assessment
   - The app creates or retrieves an Assessment row in status "in_progress".
   - User fills the multi-step form in questions.html.

3) Submit assessment
   - Answers are saved to the Assessment record.
   - Status is updated to "processing".
   - User is redirected to /assessment/<id>/processing.

4) Processing route
   - Reads the assessment data from the database.
   - Calls analyze_career_assessment with a dict of all question values.
   - Receives dict results from AI or fallback.
   - Serializes to JSON and stores in assessment.results.
   - Sets status to "completed" and updates completed_at.
   - Renders loading.html while work happens, then the user can open results.

5) Results page
   - /assessment/<id>/results loads the Assessment and parses assessment.results.
   - results.html embeds the results object in a script tag.
   - results.js reads this data and:
     - Renders career cards with match %, salary, growth, skills.
     - Displays strengths, skill gaps, and roadmap phases.
     - Lists immediate next steps and advice.
   - Includes print-ready styling for exporting as PDF.

Environment and Configuration
-----------------------------
The app is configured through environment variables:

- SECRET_KEY
  - Flask secret key for sessions.

- DATABASE_URI
  - SQLAlchemy database URL.
  - Example for SQLite:
    - sqlite:///career_guidance.db

- AI_PROVIDER
  - Controls the AI backend.
  - Allowed values:
    - gemini
    - fallback

- GEMINI_API_KEY
  - API key for Gemini when AI_PROVIDER=gemini.

A .env.example file documents the expected keys. Actual secrets are provided using a .env file locally or environment configuration on the hosting platform.

Running Locally
---------------
1) Create and activate a virtual environment:

   python -m venv venv
   venv\Scripts\activate        # Windows
   # or
   source venv/bin/activate     # macOS/Linux

2) Install dependencies:

   pip install -r requirements.txt

3) Create a .env file in the project root using .env.example as a guide, and set real values for SECRET_KEY, DATABASE_URI, AI_PROVIDER, and GEMINI_API_KEY (if using Gemini).

4) Start the application:

   python app.py

5) Open the app in a browser:

   http://127.0.0.1:5000

Deployment Notes
----------------
- The app is set up to run with Gunicorn in production using:

  gunicorn app:app

- A Procfile is included for platforms that use process types (for example, Render).
- requirements.txt includes all necessary packages, including gunicorn and google-genai.
- Environment variables must be configured on the host instead of relying on a local .env file.
- The database can be:
  - SQLite for simple/local usage.
  - PostgreSQL (or another SQLAlchemy-supported backend) by updating DATABASE_URI.

Summary
-------
This project is a full-stack AI career guidance application:
- Flask handles routing, authentication, and templating.
- SQLAlchemy manages persistent user and assessment data.
- Gemini (via the new google-genai client) generates personalized career recommendations.
- Fallback behavior guarantees that the app continues to produce meaningful results even if the AI provider is unavailable.
- The UI presents results in a modern, structured, and print-ready format suitable for demos, portfolios, or real users.
