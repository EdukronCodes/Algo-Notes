# Automated Loan Processing System

This is an end-to-end system for processing loan documents using AI and machine learning capabilities.

## Features

- Document Upload & Storage
- Document Parsing with OCR Support
- LangChain + LLM Integration
- Data Storage & Database Management
- REST API & Frontend Features
- Security, Monitoring & Extensibility

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/loan_processing
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=your-region
   S3_BUCKET_NAME=your-bucket-name
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   COHERE_API_KEY=your-cohere-key
   ```
5. Initialize the database:
   ```bash
   python app/db/init_db.py
   ```
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
.
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── src/
│   └── public/
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## API Documentation

The API documentation is available at `/docs` when running the application.

## Security

- JWT Authentication
- Rate Limiting
- File Type Validation
- Access Control
- Audit Logging

## License

MIT 