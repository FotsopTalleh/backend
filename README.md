# Personalized Timetable Generator - Backend

Flask backend for generating personalized timetables from faculty timetable and Form B PDFs.

## Features

- PDF parsing using pdfplumber
- Timetable generation in JSON format
- HTML rendering of timetables
- PDF export functionality
- CORS enabled for frontend integration

## Deployment on Render

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add environment variables if needed

## API Endpoints

- `POST /upload` - Upload faculty timetable and Form B PDFs
- `GET /timetable` - View timetable as HTML
- `POST /download` - Download timetable as PDF

## Development

```bash
pip install -r requirements.txt
python app.py