from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import DocumentMetadata
from app.utils.extractors import extract_text
from app.services.chunking import get_splitter
from app.services.vector_store import vector_store
from app.core.config import settings
import shutil
import os
import uuid
from typing import Optional

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    strategy: str = Form("recursive"),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    db: AsyncSession = Depends(get_db)
):
    # 1. Save temp file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(temp_dir, f"{file_id}{ext}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Extract Text
        text = extract_text(temp_path)
        
        # 3. Chunking
        splitter = get_splitter(strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
        
        # 4. Vectorize & Index
        doc_metadata = {
            "filename": file.filename,
            "file_id": file_id,
            "strategy": strategy,
        }
        vector_store.upsert_chunks(chunks, doc_metadata)
        
        # 5. Save Metadata in SQL
        db_doc = DocumentMetadata(
            filename=file.filename,
            chunking_strategy=strategy,
            chunk_count=len(chunks),
            metadata_json={"file_id": file_id, "ext": ext}
        )
        db.add(db_doc)
        await db.commit()
        await db.refresh(db_doc)
        
        return {
            "status": "success",
            "document_id": db_doc.id,
            "filename": file.filename,
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
