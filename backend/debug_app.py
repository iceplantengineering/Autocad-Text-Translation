from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import tempfile
from typing import List, Optional
import asyncio
from datetime import datetime
from enhanced_dwg_processor import EnhancedDWGProcessor
from debug_translation_service import DebugTranslationService

app = FastAPI(title="AutoCAD DWG Translator API (Debug Version)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

dwg_processor = EnhancedDWGProcessor()
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
        self.debug_info = {}

jobs = {}

async def process_translation(job_id: str):
    """バックグラウンドで翻訳処理を実行"""
    job = jobs.get(job_id)
    if not job:
        return

    try:
        job.status = "extracting"
        job.progress = 10
        job.debug_info["extraction_started"] = datetime.now().isoformat()

        # テキストエンティティを抽出
        text_entities = dwg_processor.extract_text_entities(job.file_path)
        job.extracted_texts = text_entities
        job.debug_info["extracted_count"] = len(text_entities)
        job.debug_info["extracted_texts"] = [entity.text for entity in text_entities]

        # 中国語テキストをフィルタリング
        all_texts = [entity.text for entity in text_entities]
        chinese_texts = translation_service.filter_chinese_texts(all_texts)
        job.debug_info["chinese_texts_found"] = len(chinese_texts)
        job.debug_info["chinese_texts"] = chinese_texts

        if not chinese_texts:
            job.status = "completed"
            job.progress = 100
            job.completed_at = datetime.now()
            job.translated_file_path = job.file_path
            job.debug_info["no_chinese_text"] = True
            return

        job.status = "translating"
        job.progress = 30
        job.debug_info["translation_started"] = datetime.now().isoformat()

        # 専門辞書を取得
        glossary = translation_service.create_technical_glossary()

        # 翻訳を実行
        translation_results = await translation_service.translate(chinese_texts, glossary)
        job.debug_info["translation_results"] = translation_results

        # 翻訳マッピングを作成
        text_to_translation = {}
        for i, result in enumerate(translation_results):
            text_to_translation[chinese_texts[i]] = result['translated_text']

        job.translations = text_to_translation
        job.debug_info["translation_mapping"] = text_to_translation

        job.status = "replacing"
        job.progress = 70
        job.debug_info["replacement_started"] = datetime.now().isoformat()

        # DWGファイル内のテキストを置換
        handle_to_translation = {}
        for entity in text_entities:
            if entity.text in text_to_translation:
                handle_to_translation[entity.handle] = text_to_translation[entity.text]
                job.debug_info[f"replacement_{entity.handle}"] = {
                    "original": entity.text,
                    "translated": text_to_translation[entity.text],
                    "entity_type": entity.entity_type
                }

        # テキストを置換
        translated_file_path = dwg_processor.replace_text_entities(job.file_path, handle_to_translation)

        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.now()
        job.translated_file_path = translated_file_path
        job.debug_info["replacement_completed"] = datetime.now().isoformat()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        job.debug_info["error"] = str(e)
        import traceback
        job.debug_info["error_traceback"] = traceback.format_exc()
        print(f"Error in job {job_id}: {e}")

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

        # バックグラウンド処理を開始
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
        "translations_count": len(job.translations),
        "debug_info": job.debug_info
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
                "completed_at": job.completed_at,
                "debug_info": job.debug_info
            }
            for job in jobs.values()
        ]
    }

@app.get("/debug/translations")
async def debug_translations():
    """翻訳マッピングを表示"""
    return {
        "available_translations": translation_service.mock_translations,
        "total_count": len(translation_service.mock_translations)
    }

@app.get("/debug/test-chinese-detection/{text}")
async def test_chinese_detection(text: str):
    """中国語検出をテスト"""
    is_chinese = translation_service.detect_chinese_text(text)
    return {
        "text": text,
        "is_chinese": is_chinese,
        "translation": translation_service.mock_translations.get(text, "No translation available")
    }

@app.get("/debug/test-file/{filename}")
async def test_file_processing(filename: str):
    """ファイル処理をテスト"""
    file_path = os.path.join("test_files", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Test file not found")

    try:
        # ファイル情報を取得
        file_info = dwg_processor.get_file_info(file_path)

        # テキスト抽出をテスト
        text_entities = dwg_processor.extract_text_entities(file_path)
        all_texts = [entity.text for entity in text_entities]
        chinese_texts = translation_service.filter_chinese_texts(all_texts)

        return {
            "filename": filename,
            "file_info": file_info,
            "total_texts": len(all_texts),
            "chinese_texts": len(chinese_texts),
            "all_texts": all_texts,
            "chinese_only": chinese_texts
        }
    except Exception as e:
        return {
            "filename": filename,
            "error": str(e)
        }

@app.get("/debug/test-dwg-conversion/{filename}")
async def test_dwg_conversion(filename: str):
    """DWG変換をテスト"""
    file_path = os.path.join("test_files", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Test file not found")

    try:
        # DWG変換をテスト
        if filename.lower().endswith('.dwg'):
            dxf_path = dwg_processor.convert_dwg_to_dxf(file_path)
            conversion_success = os.path.exists(dxf_path)
        else:
            conversion_success = True
            dxf_path = file_path

        return {
            "filename": filename,
            "conversion_success": conversion_success,
            "converted_path": dxf_path if conversion_success else None,
            "original_path": file_path
        }
    except Exception as e:
        return {
            "filename": filename,
            "conversion_success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(), "mode": "debug"}

@app.get("/")
async def root():
    return {
        "message": "AutoCAD DWG Translator API (Debug Mode)",
        "version": "1.0.0",
        "debug_endpoints": [
            "/debug/translations - Show available translations",
            "/debug/test-chinese-detection/{text} - Test Chinese detection",
            "/debug/test-file/{filename} - Test file processing",
            "/debug/test-dwg-conversion/{filename} - Test DWG to DXF conversion"
        ],
        "supported_formats": [".dwg", ".dxf"],
        "note": "This is a debug version with enhanced logging and DWG support"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)