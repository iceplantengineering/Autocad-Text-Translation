# AutoCAD DWG Chinese to Japanese Translator

A web-based application that automatically extracts Chinese text from AutoCAD DWG files, translates it to Japanese, and re-inserts the translated text back into the DWG file while preserving original formatting.

## Features

- DWG file upload and processing (AutoCAD 2012+)
- Chinese to Japanese text translation
- Text extraction and re-insertion with formatting preservation
- Web-based interface with progress tracking
- Deployment ready for Netlify

## Project Structure

```
├── backend/          # Python Flask/FastAPI backend
├── frontend/         # React frontend application
└── README.md         # This file
```

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Tech Stack

- **Backend**: Python, Flask/FastAPI, Autodesk APS
- **Frontend**: React, Material-UI
- **Translation**: DeepL/Google Cloud Translation API
- **Deployment**: Netlify (frontend), Cloud services (backend)