# 📁 Project Structure - AI Health Diagnostic System

Complete overview of the project architecture and file organization.

## 📊 Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   React     │─────▶│   Flask     │─────▶│  PostgreSQL  │
│  Frontend   │      │   Backend   │      │   Database   │
│  (Port 3000)│◀─────│  (Port 5000)│      │              │
└─────────────┘      └─────────────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  AI Models  │
                     │ • X-ray     │
                     │ • Symptoms  │
                     └─────────────┘
```

## 🗂️ Directory Structure

```
ai_health_diagnostic_system/
│
├── 📄 README.md                        # Main project documentation
├── 📄 SETUP_GUIDE.md                   # Detailed setup instructions
├── 📄 API_DOCUMENTATION.md             # API endpoint reference
├── 📄 PROJECT_STRUCTURE.md             # This file
├── 📄 requirements.txt                 # Python dependencies
├── 📄 docker-compose.yml               # Docker orchestration
├── 📄 .gitignore                       # Git ignore rules
├── 🔧 start.bat                        # Windows quick start
├── 🔧 start.sh                         # macOS/Linux quick start
│
├── 📂 backend/                         # Flask API Backend
│   ├── 📄 app.py                       # Main Flask application
│   ├── 📄 config.py                    # Configuration settings
│   ├── 📄 Dockerfile                   # Backend Docker image
│   ├── 📄 .env.example                 # Environment variables template
│   │
│   ├── 📂 models/                      # Data & ML models
│   │   ├── 📄 database.py              # SQLAlchemy models
│   │   └── 📂 ml_models/               # Machine Learning models
│   │       ├── 📄 xray_model.py        # X-ray CNN + Grad-CAM
│   │       └── 📄 symptom_model.py     # NLP symptom checker
│   │
│   ├── 📂 routes/                      # API endpoints
│   │   ├── 📄 auth.py                  # Authentication routes
│   │   ├── 📄 xray.py                  # X-ray analysis routes
│   │   ├── 📄 symptoms.py              # Symptom checker routes
│   │   └── 📄 dashboard.py             # Dashboard routes
│   │
│   ├── 📂 uploads/                     # User uploaded files
│   │   ├── 📂 xrays/                   # X-ray images
│   │   └── 📂 gradcam/                 # Grad-CAM visualizations
│   │
│   └── 📂 saved_models/                # Trained ML models
│       ├── 📄 xray_model.h5            # X-ray DenseNet121
│       ├── 📄 symptom_model.pkl        # Symptom classifier
│       ├── 📄 symptom_vectorizer.pkl   # TF-IDF vectorizer
│       └── 📄 symptom_label_encoder.pkl # Label encoder
│
├── 📂 frontend/                        # React Frontend
│   ├── 📄 package.json                 # Node dependencies
│   ├── 📄 vite.config.js               # Vite configuration
│   ├── 📄 tailwind.config.js           # Tailwind CSS config
│   ├── 📄 postcss.config.js            # PostCSS config
│   ├── 📄 Dockerfile                   # Frontend Docker image
│   ├── 📄 index.html                   # HTML entry point
│   │
│   └── 📂 src/                         # Source code
│       ├── 📄 main.jsx                 # Application entry
│       ├── 📄 App.jsx                  # Main app component
│       ├── 📄 index.css                # Global styles
│       │
│       ├── 📂 components/              # Reusable components
│       │   └── 📄 Layout.jsx           # Main layout wrapper
│       │
│       ├── 📂 contexts/                # React contexts
│       │   └── 📄 AuthContext.jsx      # Authentication state
│       │
│       ├── 📂 services/                # API integration
│       │   └── 📄 api.js               # Axios API client
│       │
│       └── 📂 pages/                   # Application pages
│           ├── 📂 Auth/                # Authentication pages
│           │   ├── 📄 Login.jsx        # Login page
│           │   └── 📄 Register.jsx     # Registration page
│           │
│           ├── 📂 Patient/             # Patient portal
│           │   ├── 📄 Dashboard.jsx    # Patient dashboard
│           │   ├── 📄 XRayAnalysis.jsx # X-ray upload & analysis
│           │   └── 📄 SymptomChecker.jsx # Symptom checker
│           │
│           ├── 📂 Doctor/              # Doctor portal
│           │   ├── 📄 Dashboard.jsx    # Doctor dashboard
│           │   ├── 📄 Patients.jsx     # Patient list
│           │   └── 📄 PatientDetails.jsx # Patient details
│           │
│           └── 📄 Profile.jsx          # User profile page
│
└── 📂 datasets/                        # Training data & scripts
    ├── 📄 disease_symptom.csv          # Symptom-disease dataset
    ├── 📄 train_models.py              # Model training script
    ├── 📄 README.md                    # Dataset documentation
    └── 📂 sample_xrays/                # Sample X-ray images (optional)
```

## 🔧 Technology Stack

### Backend (Flask)
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM
- **Flask-JWT-Extended**: Authentication
- **Flask-CORS**: Cross-origin requests
- **PostgreSQL**: Database
- **TensorFlow/Keras**: Deep learning
- **scikit-learn**: Machine learning
- **OpenCV**: Image processing
- **NLTK**: Natural language processing

### Frontend (React)
- **React 18**: UI framework
- **Vite**: Build tool
- **React Router**: Navigation
- **Axios**: HTTP client
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **React Toastify**: Notifications
- **Chart.js**: Data visualization

### Database
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM layer

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password
- `role`: 'patient' or 'doctor'
- `created_at`: Account creation timestamp

### Patients Table
- `id`: Primary key
- `user_id`: Foreign key to Users
- `full_name`: Patient name
- `date_of_birth`: Birth date
- `gender`: Gender
- `phone`: Contact number
- `address`: Address
- `medical_history`: Medical history text

### Doctors Table
- `id`: Primary key
- `user_id`: Foreign key to Users
- `full_name`: Doctor name
- `specialization`: Medical specialization
- `license_number`: Medical license
- `phone`: Contact number
- `hospital`: Hospital affiliation

### XRayReports Table
- `id`: Primary key
- `patient_id`: Foreign key to Patients
- `image_path`: Path to X-ray image
- `gradcam_path`: Path to Grad-CAM image
- `predictions`: JSON of all predictions
- `predicted_class`: Top prediction
- `confidence`: Confidence score
- `status`: 'pending', 'reviewed', 'urgent'
- `created_at`: Upload timestamp

### SymptomChecks Table
- `id`: Primary key
- `patient_id`: Foreign key to Patients
- `symptoms`: Symptom description
- `predicted_disease`: Predicted disease
- `confidence`: Confidence score
- `urgency_level`: 'mild', 'moderate', 'severe'
- `top_predictions`: JSON of top 3 predictions
- `recommendations`: Medical recommendations
- `created_at`: Check timestamp

### Alerts Table
- `id`: Primary key
- `patient_id`: Foreign key to Patients
- `alert_type`: 'xray' or 'symptom'
- `reference_id`: ID of related report/check
- `message`: Alert message
- `severity`: 'low', 'medium', 'high', 'critical'
- `is_read`: Read status
- `created_at`: Alert timestamp

## 🔄 Data Flow

### X-ray Analysis Flow
1. Patient uploads X-ray image via React frontend
2. Image sent to Flask backend via multipart/form-data
3. Backend saves image to uploads/xrays/
4. XRayAnalyzer preprocesses image (224x224, normalization)
5. DenseNet121 model predicts disease class
6. Grad-CAM generates heatmap visualization
7. Results saved to PostgreSQL database
8. If abnormal + high confidence, create Alert
9. Response sent back to frontend with predictions
10. Frontend displays results and Grad-CAM

### Symptom Checker Flow
1. Patient enters symptoms in text form
2. Symptoms sent to Flask backend
3. SymptomChecker preprocesses text (tokenization, stopword removal)
4. TF-IDF vectorization of symptoms
5. Naive Bayes classifier predicts disease
6. Urgency level determined based on disease
7. Recommendations generated
8. Results saved to database
9. If severe + high confidence, create Alert
10. Response sent to frontend
11. Frontend displays prediction and recommendations

### Authentication Flow
1. User submits credentials (email, password)
2. Backend validates credentials
3. JWT access token and refresh token generated
4. Tokens sent to frontend
5. Frontend stores tokens in localStorage
6. Subsequent requests include Bearer token
7. Backend validates token on each request
8. If token expired, use refresh token to get new access token

## 🚀 API Routes

### Authentication (`/api/auth`)
- POST `/register` - Register new user
- POST `/login` - User login
- GET `/profile` - Get user profile
- PUT `/profile` - Update profile
- POST `/refresh` - Refresh access token

### X-ray Analysis (`/api/xray`)
- POST `/upload` - Upload and analyze X-ray
- GET `/reports` - Get all reports
- GET `/report/<id>` - Get specific report
- PUT `/report/<id>` - Update report (doctor only)
- DELETE `/report/<id>` - Delete report
- GET `/image/<filename>` - Get image file

### Symptom Checker (`/api/symptoms`)
- POST `/check` - Check symptoms
- GET `/history` - Get symptom history
- GET `/check/<id>` - Get specific check
- PUT `/check/<id>` - Update check
- DELETE `/check/<id>` - Delete check
- GET `/diseases` - Get disease list

### Dashboard (`/api/dashboard`)
- GET `/stats` - Get statistics
- GET `/patients` - Get all patients (doctor only)
- GET `/patient/<id>` - Get patient details (doctor only)
- GET `/alerts` - Get urgent alerts
- PUT `/alert/<id>/read` - Mark alert as read
- GET `/analytics/trends` - Get disease trends

## 🎨 Frontend Routes

### Public Routes
- `/login` - Login page
- `/register` - Registration page

### Patient Routes
- `/patient/dashboard` - Patient dashboard
- `/patient/xray` - X-ray analysis
- `/patient/symptoms` - Symptom checker
- `/patient/profile` - Patient profile

### Doctor Routes
- `/doctor/dashboard` - Doctor dashboard
- `/doctor/patients` - Patient list
- `/doctor/patient/:id` - Patient details
- `/doctor/profile` - Doctor profile

## 🔐 Security Features

1. **Password Hashing**: Werkzeug SHA-256
2. **JWT Authentication**: Access & refresh tokens
3. **Role-Based Access**: Patient vs Doctor permissions
4. **CORS Protection**: Configured allowed origins
5. **Input Validation**: Request data validation
6. **SQL Injection Protection**: SQLAlchemy ORM
7. **File Upload Validation**: File type and size checks

## 🧪 Testing Strategy

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test API endpoints
3. **E2E Tests**: Test complete user flows
4. **Model Tests**: Validate ML predictions
5. **Load Tests**: Test system under load

## 📈 Performance Optimization

1. **Database Indexing**: Index on frequently queried fields
2. **Lazy Loading**: Load data on demand
3. **Image Compression**: Optimize uploaded images
4. **Caching**: Cache model predictions
5. **Pagination**: Limit query results
6. **Connection Pooling**: Reuse database connections

## 🔮 Future Enhancements

1. **Real-time Notifications**: WebSocket alerts
2. **Mobile App**: React Native version
3. **Telemedicine**: Video consultations
4. **EHR Integration**: Connect with existing systems
5. **Multi-language**: Internationalization
6. **Voice Input**: Speech-to-text for symptoms
7. **Advanced Analytics**: ML-powered insights
8. **Appointment Booking**: Scheduling system

## 📝 Development Guidelines

1. **Code Style**: Follow PEP 8 (Python) and ESLint (JavaScript)
2. **Git Workflow**: Feature branches, pull requests
3. **Documentation**: Comment complex logic
4. **Testing**: Write tests for new features
5. **Security**: Never commit secrets or API keys
6. **Performance**: Profile and optimize bottlenecks

## 🆘 Troubleshooting

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed troubleshooting steps.

---

**Last Updated**: January 2024










