import os
from typing import Optional, Dict, List
import pypdf
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import boto3
from ..core.config import settings
import magic
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        ) if settings.AWS_ACCESS_KEY_ID else None

    def validate_file(self, file_path: str) -> bool:
        """Validate file type and size"""
        try:
            file_type = magic.from_file(file_path, mime=True)
            file_size = os.path.getsize(file_path)
            
            if file_type not in settings.ALLOWED_FILE_TYPES:
                raise ValueError(f"Invalid file type: {file_type}")
            
            if file_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_size} bytes")
            
            return True
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False

    def upload_to_s3(self, file_path: str, object_name: str) -> str:
        """Upload file to S3 and return the S3 URL"""
        if not self.s3_client:
            return file_path
        
        try:
            self.s3_client.upload_file(
                file_path,
                settings.S3_BUCKET_NAME,
                object_name
            )
            return f"s3://{settings.S3_BUCKET_NAME}/{object_name}"
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

    def extract_text_from_pdf(self, file_path: str) -> Dict[str, any]:
        """Extract text from PDF and perform OCR if needed"""
        try:
            # Try direct text extraction first
            pdf_reader = pypdf.PdfReader(file_path)
            text_content = []
            metadata = {}
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                # If page is empty or has very little text, try OCR
                if len(text.strip()) < 50:
                    images = convert_from_path(file_path, first_page=page_num+1, last_page=page_num+1)
                    for image in images:
                        text = pytesseract.image_to_string(image)
                
                if text.strip():  # Only add non-empty pages
                    text_content.append({
                        'page_number': page_num + 1,
                        'content': text.strip()
                    })
            
            # Extract metadata
            metadata = {
                'title': pdf_reader.metadata.get('/Title', ''),
                'author': pdf_reader.metadata.get('/Author', ''),
                'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                'total_pages': len(pdf_reader.pages)
            }
            
            return {
                'text_content': text_content,
                'metadata': metadata,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {
                'text_content': [],
                'metadata': {},
                'status': 'error',
                'error_message': str(e)
            }

    def process_document(self, file_path: str, object_name: str) -> Dict[str, any]:
        """Main method to process a document"""
        try:
            # Validate file
            if not self.validate_file(file_path):
                raise ValueError("File validation failed")
            
            # Upload to S3 if configured
            storage_path = self.upload_to_s3(file_path, object_name)
            
            # Extract text and metadata
            extraction_result = self.extract_text_from_pdf(file_path)
            
            return {
                'storage_path': storage_path,
                'extraction_result': extraction_result,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            } 