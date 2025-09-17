# Deployment Guide

## Backend Deployment

### Option 1: Docker (Recommended)
1. Copy `.env.example` to `.env` and add your API keys
2. Build and run with Docker Compose:
```bash
cd backend
docker-compose up -d
```

### Option 2: Direct Python
1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DEEPL_API_KEY="your_deepl_api_key"
export GOOGLE_TRANSLATE_API_KEY="your_google_api_key"
```

3. Run the application:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Option 3: Cloud Deployment

#### AWS Elastic Beanstalk
1. Create a new Python application
2. Upload the backend folder
3. Configure environment variables in the console

#### Google Cloud Run
1. Build Docker image:
```bash
cd backend
docker build -t gcr.io/your-project/dwg-translator .
```

2. Push to Google Container Registry:
```bash
docker push gcr.io/your-project/dwg-translator
```

3. Deploy to Cloud Run

#### Heroku
1. Create `Procfile`:
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

2. Deploy using Heroku CLI

## Frontend Deployment

### Netlify (Recommended)
1. Connect your GitHub repository to Netlify
2. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Add environment variables for API URL

### Manual Deployment
1. Build the frontend:
```bash
cd frontend
npm install
npm run build
```

2. Deploy the `dist` folder to any static hosting service

## Environment Variables

### Backend
- `DEEPL_API_KEY`: DeepL API key for translation
- `GOOGLE_TRANSLATE_API_KEY`: Google Translate API key (fallback)
- `APS_CLIENT_ID`: Autodesk Platform Services client ID (optional)
- `APS_CLIENT_SECRET`: Autodesk Platform Services client secret (optional)
- `AWS_ACCESS_KEY_ID`: AWS access key (for S3 storage)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (for S3 storage)
- `AWS_S3_BUCKET`: S3 bucket name

### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)

## API Endpoints

- `POST /upload` - Upload DWG file for translation
- `GET /jobs/{job_id}` - Get job status
- `GET /download/{job_id}` - Download translated file
- `GET /jobs` - List all jobs
- `GET /health` - Health check

## Security Considerations

1. Always use HTTPS in production
2. Secure your API keys and never commit them to version control
3. Implement rate limiting for API endpoints
4. Use CORS properly to restrict access
5. Implement file size limits and validation
6. Regular security updates for dependencies