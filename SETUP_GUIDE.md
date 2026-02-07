# 🚀 Setup Guide - AI Health Diagnostic System

Complete step-by-step guide to set up and run the AI Health Diagnostic System locally.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **PostgreSQL 13+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)

## 🔧 Installation Steps

### Step 1: Clone the Repository

```bash
cd ai_health_diagnostic_system
```

### Step 2: Database Setup

#### Option A: Local PostgreSQL

1. **Start PostgreSQL service**
   ```bash
   # Windows (if installed as service)
   net start postgresql
   
   # macOS
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   ```

2. **Create database**
   ```bash
   # Access PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE health_diagnostic;
   
   # Exit
   \q
   ```

#### Option B: Docker PostgreSQL

```bash
docker run -d \
  --name health_diagnostic_db \
  -e POSTGRES_DB=health_diagnostic \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

### Step 3: Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. **Create .env file** (copy from example)
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

6. **Edit .env file** with your settings
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/health_diagnostic
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-here
   ```

### Step 4: Train Models

```bash
cd ../datasets
python train_models.py
```

This will:
- Train the symptom checker model
- Create the X-ray model structure
- Save models to `backend/saved_models/`

### Step 5: Initialize Database

```bash
cd ../backend
python app.py
```

This will:
- Create all database tables
- Create default doctor and patient accounts
- Start the Flask server on http://localhost:5000

Press `Ctrl+C` to stop, we'll restart it later.

### Step 6: Frontend Setup

Open a **new terminal window**.

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env file**
   ```bash
   # Windows
   echo VITE_API_URL=http://localhost:5000/api > .env
   
   # macOS/Linux
   echo "VITE_API_URL=http://localhost:5000/api" > .env
   ```

### Step 7: Start the Application

#### Terminal 1 - Backend
```bash
cd backend
# Activate virtual environment if not already active
python app.py
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

## 🎉 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## 👥 Default Login Credentials

### Doctor Account
- **Email**: `doctor@hospital.com`
- **Password**: `doctor123`

### Patient Account
- **Email**: `patient@email.com`
- **Password**: `patient123`

## 🐳 Docker Setup (Alternative)

If you prefer to use Docker:

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## 🧪 Testing the System

### Test X-ray Analysis

1. Login as patient
2. Go to "X-ray Analysis"
3. Upload a chest X-ray image (you can use any chest X-ray image for testing)
4. Click "Analyze X-ray"
5. View the AI prediction and confidence scores

### Test Symptom Checker

1. Login as patient
2. Go to "Symptom Checker"
3. Enter symptoms like: "fever, cough, difficulty breathing"
4. Click "Analyze Symptoms"
5. View the predicted disease and recommendations

### Test Doctor Dashboard

1. Login as doctor
2. View patient statistics
3. Check alerts for urgent cases
4. Browse patient records
5. View detailed patient reports

## 🔍 Troubleshooting

### Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
- Ensure PostgreSQL is running
- Check if port 5432 is available
- Verify DATABASE_URL in .env file

### NLTK Data Not Found

**Error**: `Resource punkt not found`

**Solution**:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Windows - Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### React Build Errors

**Error**: `Module not found: Can't resolve...`

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Environment Variables Reference

### Backend (.env)

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

## 🎯 Next Steps

1. **For Development**:
   - Modify the code as needed
   - Train models on real datasets
   - Add more features

2. **For Production**:
   - Change all secret keys
   - Use production database
   - Enable HTTPS
   - Set up proper logging
   - Configure CORS for production domain

3. **For Deployment**:
   - See [DEPLOYMENT.md](./DEPLOYMENT.md) for AWS/Heroku instructions
   - Set up CI/CD pipeline
   - Configure monitoring and alerts

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error logs in terminal
3. Ensure all prerequisites are installed
4. Verify environment variables are set correctly

## ⚠️ Important Notes

- This system is for **educational purposes only**
- **NOT** for actual medical diagnosis
- Always consult healthcare professionals for medical decisions
- Keep your secret keys secure in production

---

**Happy Coding! 🚀**










