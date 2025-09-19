from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import tempfile
from typing import List, Optional
import asyncio
from datetime import datetime
from dwg_processor import DWGProcessor
from debug_translation_service import DebugTranslationService
from text_cleaner import TextCleaner

app = FastAPI(title="AutoCAD DWG Translator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://68cd66c628bbf420fb0c3b07--autocad-text-translation.netlify.app",
        "https://autocad-text-translation.netlify.app",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

dwg_processor = DWGProcessor()
translation_service = DebugTranslationService()

class TranslationJob:
    def __init__(self, job_id: str, filename: str, file_path: str):
        self.job_id = job_id
        self.filename = filename
        self.file_path = file_path
        self.status = "uploaded"
        self.progress = 0
        self.error_message = None
        self.created_at = datetime.now()
        self.completed_at = None
        self.translated_file_path = None
        self.extracted_texts = []
        self.translations = {}

jobs = {}

@app.get("/")
async def root():
    return {"message": "AutoCAD DWG Translator API"}

async def process_translation(job_id: str):
    """Background task to process the translation"""
    job = jobs.get(job_id)
    if not job:
        return

    try:
        job.status = "extracting"
        job.progress = 10

        # Extract text entities
        text_entities = dwg_processor.extract_text_entities(job.file_path)
        job.extracted_texts = text_entities

        # Filter Chinese texts
        chinese_texts = translation_service.filter_chinese_texts([entity.text for entity in text_entities])

        if not chinese_texts:
            job.status = "completed"
            job.progress = 100
            job.completed_at = datetime.now()
            job.translated_file_path = job.file_path  # No translation needed
            return

        job.status = "translating"
        job.progress = 30

        # Get glossary
        glossary = translation_service.create_technical_glossary()

        # Translate texts
        translation_results = await translation_service.translate(chinese_texts, glossary)

        # Create translation mapping
        text_to_translation = {}
        for i, result in enumerate(translation_results):
            text_to_translation[chinese_texts[i]] = result['translated_text']

        job.status = "replacing"
        job.progress = 70

        # Replace text in DWG file
        # Create handle-to-text mapping
        handle_to_translation = {}
        for entity in text_entities:
            if entity.text in text_to_translation:
                handle_to_translation[entity.handle] = text_to_translation[entity.text]

        # Replace texts
        translated_file_path = dwg_processor.replace_text_entities(job.file_path, handle_to_translation)

        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.now()
        job.translated_file_path = translated_file_path
        job.translations = text_to_translation

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not (file.filename.lower().endswith('.dwg') or file.filename.lower().endswith('.dxf')):
        raise HTTPException(status_code=400, detail="Only DWG and DXF files are supported")

    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        jobs[job_id] = TranslationJob(job_id, file.filename, file_path)

        # Start background processing
        if background_tasks:
            background_tasks.add_task(process_translation, job_id)

        return {
            "job_id": job_id,
            "filename": file.filename,
            "message": "File uploaded successfully",
            "status": "processing_started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        "job_id": job.job_id,
        "filename": job.filename,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "extracted_count": len(job.extracted_texts),
        "translations_count": len(job.translations)
    }

@app.get("/download/{job_id}")
async def download_file(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    if not job.translated_file_path or not os.path.exists(job.translated_file_path):
        raise HTTPException(status_code=404, detail="Translated file not found")

    return FileResponse(
        path=job.translated_file_path,
        filename=f"translated_{job.filename}",
        media_type='application/octet-stream'
    )

@app.get("/jobs")
async def list_jobs():
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            }
            for job in jobs.values()
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)