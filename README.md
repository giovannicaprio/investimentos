# FastAPI Web Application

This is a simple web application built with FastAPI and modern frontend technologies.

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the project root directory and your virtual environment is activated.

2. Run the application:
```bash
cd app
uvicorn main:app --reload
```

3. Open your browser and navigate to:
```
http://localhost:8000
```

## Features

- FastAPI backend with automatic API documentation
- Modern frontend with Tailwind CSS
- API endpoint example at `/api/hello`
- Interactive web interface

## API Documentation

Once the application is running, you can access the automatic API documentation at:
```
http://localhost:8000/docs
``` 