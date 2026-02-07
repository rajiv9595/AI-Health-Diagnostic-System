# ⚡ Quick Start Guide

Get up and running with the AI Health Diagnostic System in 5 minutes!

## 🎯 Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed  
- [ ] PostgreSQL 13+ installed
- [ ] Git installed

## 🚀 Super Quick Start (3 Steps)

### Step 1: Setup Database

```bash
# Start PostgreSQL and create database
psql -U postgres -c "CREATE DATABASE health_diagnostic;"
```

### Step 2: Train Models

```bash
# Install Python dependencies
cd backend
pip install -r ../requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Train AI models
cd ../datasets
python train_models.py
```

### Step 3: Start Application

**Windows:**
```bash
# Double-click start.bat or run:
start.bat
```

**macOS/Linux:**
```bash
# Make script executable and run:
chmod +x start.sh
./start.sh
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🔑 Login Credentials

### Doctor Account
- Email: `doctor@hospital.com`
- Password: `doctor123`

### Patient Account  
- Email: `patient@email.com`
- Password: `patient123`

## 📱 What to Try

### As a Patient:
1. ✅ Login with patient credentials
2. ✅ Upload a chest X-ray image
3. ✅ Use the symptom checker
4. ✅ View your health reports

### As a Doctor:
1. ✅ Login with doctor credentials
2. ✅ View patient statistics
3. ✅ Check urgent alerts
4. ✅ Browse patient records

## 🐳 Docker Quick Start (Alternative)

If you have Docker installed:

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## 📚 Next Steps

- Read [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions
- Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API reference
- See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for architecture

## ⚠️ Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"
```

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Module Not Found
```bash
# Reinstall dependencies
cd backend
pip install -r ../requirements.txt
```

## 🆘 Need Help?

1. Check the [Troubleshooting](./SETUP_GUIDE.md#troubleshooting) section
2. Review error messages in terminal
3. Ensure all prerequisites are installed
4. Verify PostgreSQL is running

## 🎉 Success!

If you see:
- ✅ "Database initialized with default users"
- ✅ Backend running on port 5000
- ✅ Frontend running on port 3000

**You're all set! Start exploring the AI Health Diagnostic System! 🩺**

---

**Remember**: This is for educational purposes only. Not for actual medical diagnosis.










