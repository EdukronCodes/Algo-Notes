from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import os
from ...db.database import get_db
from ...models.models import Document, LoanApplication
from ...services.document_processor import DocumentProcessor
from ...services.loan_processor import LoanProcessor
from ...core.config import settings
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: List[UploadFile] = File(...),
    loan_application_id: int = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Upload multiple loan documents
    """
    try:
        document_processor = DocumentProcessor()
        results = []
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        for file in files:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
            
            # Save file temporarily
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Process document
            process_result = document_processor.process_document(
                file_path=file_path,
                object_name=unique_filename
            )
            
            if process_result['status'] == 'success':
                # Create document record
                document = Document(
                    filename=file.filename,
                    file_path=process_result['storage_path'],
                    file_type=file.content_type,
                    file_size=len(content),
                    status='processed',
                    extracted_text=process_result['extraction_result']['text_content'],
                    metadata=process_result['extraction_result']['metadata'],
                    loan_application_id=loan_application_id
                )
                
                db.add(document)
                db.commit()
                db.refresh(document)
                
                results.append({
                    'document_id': document.id,
                    'status': 'success',
                    'filename': file.filename
                })
            else:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'error': process_result['error_message']
                })
            
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {'results': results}
        
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/process/{loan_application_id}", status_code=status.HTTP_200_OK)
async def process_loan_documents(
    loan_application_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Process documents for a loan application
    """
    try:
        # Get all documents for the loan application
        documents = db.query(Document).filter(
            Document.loan_application_id == loan_application_id
        ).all()
        
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found for this loan application"
            )
        
        # Get loan application
        loan_application = db.query(LoanApplication).filter(
            LoanApplication.id == loan_application_id
        ).first()
        
        if not loan_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan application not found"
            )
        
        # Extract text from all documents
        document_texts = []
        for doc in documents:
            if isinstance(doc.extracted_text, list):
                for page in doc.extracted_text:
                    document_texts.append(page.get('content', ''))
            elif isinstance(doc.extracted_text, str):
                document_texts.append(doc.extracted_text)
        
        # Process loan information
        loan_processor = LoanProcessor()
        processing_result = loan_processor.process_loan_application(document_texts)
        
        if processing_result['status'] == 'success':
            # Update loan application with extracted data
            loan_application.extracted_data = processing_result['data']
            loan_application.processing_status = 'completed'
            db.commit()
            
            return {
                'status': 'success',
                'loan_application_id': loan_application_id,
                'extracted_data': processing_result['data']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=processing_result['error_message']
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Loan document processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/documents/{document_id}", status_code=status.HTTP_200_OK)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get document details by ID
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.get("/loan-application/{loan_application_id}/documents", status_code=status.HTTP_200_OK)
async def get_loan_application_documents(
    loan_application_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get all documents for a loan application
    """
    documents = db.query(Document).filter(
        Document.loan_application_id == loan_application_id
    ).all()
    
    return documents 