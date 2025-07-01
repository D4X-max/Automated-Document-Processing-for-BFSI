# Automated Document Processing for BFSI

This project is a comprehensive platform for automating the ingestion, classification, and information extraction from various financial and KYC documents in India. It leverages OCR, NLP, and machine learning to create a scalable and accurate solution.

## Features

- **Automatic Document Classification**: Identifies document type (PAN, Aadhaar, Voter ID).
- **Multi-language OCR**: Extracts text from documents containing English and Hindi using EasyOCR.
- **Hybrid Data Extraction**: Uses a combination of Regular Expressions and Named Entity Recognition (spaCy) for robust field extraction.
- **Duplicate Detection**: Integrates with a MongoDB database to flag duplicate KYC submissions.
- **Web Interface**: A React-based frontend for easy document upload and result visualization.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js, Tailwind CSS
- **AI / ML**: EasyOCR, spaCy, Scikit-learn, PyTorch
- **Database**: MongoDB
- **Deployment**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js & npm
- Docker & Docker Compose

### Backend Setup

1. Navigate to the project root directory.
2. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the database service:
   ```
   docker-compose up -d
   ```
5. Run the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```
The backend will be running at `http://127.0.0.1:8000`.

### Frontend Setup

1. Open a new terminal and navigate to the `doc-automation-ui` directory.
2. Install dependencies:
   ```
   npm install
   ```
3. Start the React development server:
   ```
   npm start
   ```
The frontend will be running at `http://localhost:3000`.
```

