from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel, Base

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)  # admin, agent, customer
    is_active = Column(Boolean, default=True)

    documents = relationship("Document", back_populates="user")
    loan_applications = relationship("LoanApplication", back_populates="user")

class Document(BaseModel):
    __tablename__ = "documents"

    filename = Column(String)
    file_path = Column(String)  # S3 path or local path
    file_type = Column(String)
    file_size = Column(Integer)
    status = Column(String)  # uploaded, processed, failed
    extracted_text = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"))
    
    user = relationship("User", back_populates="documents")
    loan_application = relationship("LoanApplication", back_populates="documents")

class LoanApplication(BaseModel):
    __tablename__ = "loan_applications"

    loan_amount = Column(Float)
    interest_rate = Column(Float)
    tenure_months = Column(Integer)
    status = Column(String)  # pending, approved, rejected
    processing_status = Column(String)  # new, processing, completed
    extracted_data = Column(JSON)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="loan_applications")
    documents = relationship("Document", back_populates="loan_application")

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(JSON)
    ip_address = Column(String) 