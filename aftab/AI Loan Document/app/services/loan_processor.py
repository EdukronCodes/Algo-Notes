from typing import Dict, List, Optional
from langchain.llms import OpenAI, Anthropic, Cohere
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class LoanInfo(BaseModel):
    loan_amount: float = Field(description="The total loan amount requested")
    interest_rate: float = Field(description="The annual interest rate as a percentage")
    tenure_months: int = Field(description="The loan tenure in months")
    borrower_name: str = Field(description="The name of the borrower")
    loan_purpose: str = Field(description="The stated purpose of the loan")
    confidence_score: float = Field(description="Confidence score of the extraction (0-1)")

class LoanProcessor:
    def __init__(self, llm_provider: str = "openai"):
        self.llm = self._initialize_llm(llm_provider)
        self.output_parser = PydanticOutputParser(pydantic_object=LoanInfo)

    def _initialize_llm(self, provider: str):
        """Initialize the chosen LLM provider"""
        if provider == "openai" and settings.OPENAI_API_KEY:
            return OpenAI(temperature=0, model_name="gpt-4")
        elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            return Anthropic(temperature=0)
        elif provider == "cohere" and settings.COHERE_API_KEY:
            return Cohere(temperature=0)
        else:
            raise ValueError(f"Invalid or unconfigured LLM provider: {provider}")

    def create_extraction_prompt(self) -> PromptTemplate:
        """Create the prompt template for loan information extraction"""
        template = """
        Extract the following information from the loan document text below. 
        If a piece of information is not found, return null for that field.
        
        {format_instructions}
        
        Document Text:
        {text}
        
        Extracted Information:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["text"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )

    def extract_loan_info(self, text: str) -> Dict[str, any]:
        """Extract loan information from document text using LangChain"""
        try:
            # Create the chain
            prompt = self.create_extraction_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = chain.run(text=text)
            
            # Parse the output
            parsed_output = self.output_parser.parse(result)
            
            return {
                'status': 'success',
                'data': parsed_output.dict(),
            }
            
        except Exception as e:
            logger.error(f"Loan information extraction error: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def process_loan_application(self, document_texts: List[str]) -> Dict[str, any]:
        """Process multiple documents for a loan application"""
        try:
            combined_text = "\n\n".join(document_texts)
            extraction_result = self.extract_loan_info(combined_text)
            
            if extraction_result['status'] == 'success':
                # Additional validation could be added here
                return extraction_result
            else:
                raise Exception(extraction_result['error_message'])
                
        except Exception as e:
            logger.error(f"Loan application processing error: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def validate_extraction(self, extracted_info: Dict[str, any]) -> bool:
        """Validate the extracted loan information"""
        try:
            # Basic validation rules
            if extracted_info['loan_amount'] <= 0:
                return False
            
            if extracted_info['interest_rate'] <= 0 or extracted_info['interest_rate'] > 100:
                return False
            
            if extracted_info['tenure_months'] <= 0:
                return False
            
            if not extracted_info['borrower_name']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False 