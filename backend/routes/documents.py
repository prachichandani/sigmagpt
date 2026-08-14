from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional
from ai.rag import process_document, delete_document, get_conversation_documents
import os

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    file_type: Optional[str] = Form(None)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        filename = file.filename
        file_ext = os.path.splitext(filename)[1].lower()

        if not file_type:
            if file_ext == ".pdf":
                file_type = "PDF"
            elif file_ext == ".txt":
                file_type = "TXT"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file extension: {file_ext}. Use PDF or TXT."
                )
        else:
            file_type = file_type.upper()

        if file_type not in ["PDF", "TXT"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF or TXT."
            )

        if file_type == "PDF" and file_ext != ".pdf":
            raise HTTPException(status_code=400, detail="PDF file must have .pdf extension")

        if file_type == "TXT" and file_ext != ".txt":
            raise HTTPException(status_code=400, detail="TXT file must have .txt extension")

        file_bytes = await file.read()

        result = process_document(
            file_bytes=file_bytes,
            filename=filename,
            conversation_id=conversation_id,
            file_type=file_type
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Document uploaded and processed successfully",
                "data": result
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )
    finally:
        await file.close()


@router.get("/{conversation_id}")
async def list_documents(conversation_id: str):
    try:
        documents = get_conversation_documents(conversation_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": documents
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document_endpoint(
    document_id: str,
    conversation_id: str = Query(...)
):
    try:
        result = delete_document(document_id, conversation_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )