# 🩺 AI Health Diagnostic System

A complete full-stack AI-powered health diagnostic system that runs 100% locally. Features chest X-ray analysis, symptom checking, and a comprehensive doctor dashboard.

## 🌟 Features

### 1. **Image Analysis (Deep Learning + Grad-CAM)**
- Analyze chest X-rays to detect diseases (Pneumonia, TB, COVID-19, etc.)
- Pre-trained CNN models (ResNet50/DenseNet121)
- Grad-CAM visualization of affected areas
- Confidence scores and detailed predictions

### 2. **Symptom Checker (NLP Chatbot)**
- AI-powered symptom analysis
- Disease prediction with confidence scores
- Urgency level classification (mild/moderate/severe)
- Interactive chatbot interface

### 3. **Doctor Dashboard**
- Role-based access (Doctor/Patient)
- Patient management system
- AI reports and analytics
- Disease trend visualization
- Alert system for severe cases

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask + Flask-RESTful |
| **Frontend** | React + Tailwind CSS |
| **Database** | PostgreSQL |
| **Deep Learning** | TensorFlow + Keras |
| **NLP** | scikit-learn + NLTK |
| **Image Processing** | OpenCV + Grad-CAM |
| **Authentication** | JWT Tokens |
| **Visualization** | Chart.js + Plotly |
| **Deployment** | Docker Compose |

## 📁 Project Structure

```
ai_health_diagnostic_system/
├── backend/
│   ├── app.py                      # Flask application
│   ├── config.py                   # Configuration
│   ├── models/
│   │   ├── database.py             # Database models
│   │   ├── ml_models/
│   │   │   ├── xray_model.py       # X-ray analysis
│   │   │   ├── symptom_model.py    # Symptom checker
│   │   │   └── gradcam.py          # Grad-CAM implementation
│   ├── routes/
│   │   ├── auth.py                 # Authentication routes
│   │   ├── xray.py                 # X-ray analysis routes
│   │   ├── symptoms.py             # Symptom checker routes
│   │   └── dashboard.py            # Dashboard routes
│   ├── utils/
│   │   ├── helpers.py              # Helper functions
│   │   └── validators.py           # Input validation
│   └── saved_models/               # Trained models (.h5, .pkl)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/               # Login/Register
│   │   │   ├── Patient/            # Patient portal
│   │   │   ├── Doctor/             # Doctor dashboard
│   │   │   └── Common/             # Shared components
│   │   ├── services/               # API services
│   │   ├── utils/                  # Utilities
│   │   └── App.jsx                 # Main app
│   ├── package.json
│   └── tailwind.config.js
├── datasets/
│   ├── sample_xrays/               # Sample X-ray images
│   ├── disease_symptom.csv         # Symptom dataset
│   └── train_models.py             # Model training script
├── docker-compose.yml              # Docker setup
├── requirements.txt                # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

### Option 1: Docker Setup (Recommended)

```bash
# Clone the repository
cd ai_health_diagnostic_system

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Setup database
# Create PostgreSQL database named 'health_diagnostic'
# Update DATABASE_URL in .env

# Run migrations
flask db upgrade

# Train models (if not already trained)
python datasets/train_models.py

# Start backend server
python app.py
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/health_diagnostic

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Model Paths
XRAY_MODEL_PATH=saved_models/xray_model.h5
SYMPTOM_MODEL_PATH=saved_models/symptom_model.pkl
```

## 📊 Default Login Credentials

### Doctor Account
- Email: `doctor@hospital.com`
- Password: `doctor123`

### Patient Account
- Email: `patient@email.com`
- Password: `patient123`

## 🧪 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### X-ray Analysis
- `POST /api/xray/upload` - Upload and analyze X-ray
- `GET /api/xray/reports` - Get all reports
- `GET /api/xray/report/<id>` - Get specific report

### Symptom Checker
- `POST /api/symptoms/check` - Check symptoms
- `GET /api/symptoms/history` - Get symptom check history

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/patients` - Get all patients (doctor only)
- `GET /api/dashboard/alerts` - Get urgent cases

## 🎯 Usage

### For Patients

1. **Register/Login**: Create an account or login
2. **Upload X-ray**: Navigate to "X-ray Analysis" and upload chest X-ray image
3. **Check Symptoms**: Use the symptom checker chatbot to describe symptoms
4. **View Reports**: Check your AI-generated reports and predictions
5. **Track History**: View all past diagnoses and reports

### For Doctors

1. **Login**: Use doctor credentials
2. **Dashboard**: View patient statistics and trends
3. **Patient Management**: Access all patient records and AI reports
4. **Alerts**: Monitor urgent cases requiring immediate attention
5. **Analytics**: View disease trends and prediction accuracy

## 🔬 Model Information

### X-ray Analysis Model
- **Architecture**: DenseNet121 (pre-trained on ImageNet)
- **Fine-tuned on**: NIH Chest X-ray Dataset
- **Classes**: Normal, Pneumonia, TB, COVID-19
- **Input Size**: 224x224x3
- **Output**: Multi-class predictions with confidence scores

### Symptom Checker Model
- **Algorithm**: Naive Bayes Classifier
- **Features**: TF-IDF vectorization of symptoms
- **Classes**: 41 diseases
- **Urgency Classification**: Rule-based + confidence threshold

## 🔍 Grad-CAM Visualization

Grad-CAM (Gradient-weighted Class Activation Mapping) highlights the regions in the X-ray that most influenced the AI's decision. This helps doctors understand what the model is "looking at."

## 🐳 Docker Services

- **backend**: Flask API server (Port 5000)
- **frontend**: React development server (Port 3000)
- **postgres**: PostgreSQL database (Port 5432)

## 📈 Future Enhancements

- [ ] Deploy to AWS/Heroku
- [ ] Add more disease categories
- [ ] Implement real-time notifications (Twilio/SendGrid)
- [ ] Add patient appointment booking
- [ ] Integrate with EHR systems
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Voice-based symptom input

## 🤝 Contributing

This is a local development project. For production deployment, consider:
- Adding proper SSL/TLS
- Implementing rate limiting
- Adding comprehensive logging
- Setting up monitoring (Prometheus/Grafana)
- Implementing backup strategies

## ⚠️ Medical Disclaimer

**This system is for educational and research purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.**

## 📝 License

MIT License - Feel free to use this project for learning and development.

## 🙏 Acknowledgments

- NIH Clinical Center for Chest X-ray datasets
- TensorFlow and PyTorch communities
- Open-source medical AI research community

## 📧 Support

For issues and questions, check the documentation or create an issue in the repository.

---

**Built with ❤️ for healthcare innovation**










