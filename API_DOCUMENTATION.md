## API Documentation - AI Health Diagnostic System

Complete API reference for the backend endpoints.

**Base URL**: `http://localhost:5000/api`

---

## 🔐 Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Register

**POST** `/auth/register`

Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "patient",
  "full_name": "John Doe",
  "phone": "555-0100"
}
```

**Response** (201):
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "patient",
    "profile": { ... }
  }
}
```

### Login

**POST** `/auth/login`

Login to existing account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200):
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

### Get Profile

**GET** `/auth/profile`

Get current user profile (authenticated).

**Response** (200):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "patient",
    "profile": {
      "full_name": "John Doe",
      "phone": "555-0100",
      ...
    }
  }
}
```

### Update Profile

**PUT** `/auth/profile`

Update user profile (authenticated).

**Request Body**:
```json
{
  "full_name": "John Smith",
  "phone": "555-0200"
}
```

**Response** (200):
```json
{
  "message": "Profile updated successfully",
  "profile": { ... }
}
```

---

## 🩻 X-ray Analysis

### Upload X-ray

**POST** `/xray/upload`

Upload and analyze chest X-ray image (authenticated).

**Request**: `multipart/form-data`
- `file`: Image file (PNG, JPG, JPEG)
- `notes`: Optional notes (text)

**Response** (201):
```json
{
  "message": "X-ray analyzed successfully",
  "report": {
    "id": 1,
    "predicted_class": "Pneumonia",
    "confidence": 0.87,
    "predictions": {
      "Normal": 0.05,
      "Pneumonia": 0.87,
      "Tuberculosis": 0.06,
      "COVID-19": 0.02
    },
    "image_path": "uploads/xrays/...",
    "gradcam_path": "uploads/gradcam/...",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Get All Reports

**GET** `/xray/reports`

Get X-ray reports (authenticated).
- Patients: their own reports
- Doctors: all reports

**Response** (200):
```json
{
  "reports": [
    {
      "id": 1,
      "patient_name": "John Doe",
      "predicted_class": "Pneumonia",
      "confidence": 0.87,
      "status": "urgent",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

### Get Specific Report

**GET** `/xray/report/<id>`

Get details of specific X-ray report (authenticated).

**Response** (200):
```json
{
  "report": {
    "id": 1,
    "patient_id": 1,
    "patient_name": "John Doe",
    "predicted_class": "Pneumonia",
    "confidence": 0.87,
    "predictions": { ... },
    "image_path": "...",
    "gradcam_path": "...",
    "notes": "...",
    "status": "urgent",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Update Report

**PUT** `/xray/report/<id>`

Update X-ray report (doctor only).

**Request Body**:
```json
{
  "notes": "Confirmed pneumonia diagnosis",
  "status": "reviewed"
}
```

**Response** (200):
```json
{
  "message": "Report updated successfully",
  "report": { ... }
}
```

### Delete Report

**DELETE** `/xray/report/<id>`

Delete X-ray report (authenticated).

**Response** (200):
```json
{
  "message": "Report deleted successfully"
}
```

### Get Image

**GET** `/xray/image/<filename>`

Get X-ray or Grad-CAM image (authenticated).

**Response**: Image file

---

## 💬 Symptom Checker

### Check Symptoms

**POST** `/symptoms/check`

Analyze symptoms and predict disease (authenticated).

**Request Body**:
```json
{
  "symptoms": "fever, cough, difficulty breathing"
}
```

**Response** (201):
```json
{
  "message": "Symptoms analyzed successfully",
  "result": {
    "id": 1,
    "predicted_disease": "Pneumonia",
    "confidence": 0.85,
    "urgency_level": "severe",
    "top_predictions": [
      {
        "disease": "Pneumonia",
        "confidence": 0.85,
        "urgency": "severe"
      },
      {
        "disease": "Bronchitis",
        "confidence": 0.10,
        "urgency": "moderate"
      }
    ],
    "recommendations": "⚠️ URGENT: Seek immediate medical attention\nVisit the emergency room...",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Get Symptom History

**GET** `/symptoms/history`

Get symptom check history (authenticated).
- Patients: their own history
- Doctors: all checks

**Response** (200):
```json
{
  "checks": [
    {
      "id": 1,
      "patient_name": "John Doe",
      "symptoms": "fever, cough, difficulty breathing",
      "predicted_disease": "Pneumonia",
      "confidence": 0.85,
      "urgency_level": "severe",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

### Get Specific Check

**GET** `/symptoms/check/<id>`

Get details of specific symptom check (authenticated).

**Response** (200):
```json
{
  "check": {
    "id": 1,
    "patient_name": "John Doe",
    "symptoms": "...",
    "predicted_disease": "Pneumonia",
    "confidence": 0.85,
    "urgency_level": "severe",
    "top_predictions": [ ... ],
    "recommendations": "...",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Update Check Status

**PUT** `/symptoms/check/<id>`

Update symptom check status (authenticated).

**Request Body**:
```json
{
  "status": "resolved"
}
```

**Response** (200):
```json
{
  "message": "Symptom check updated successfully",
  "check": { ... }
}
```

### Delete Check

**DELETE** `/symptoms/check/<id>`

Delete symptom check (authenticated).

**Response** (200):
```json
{
  "message": "Symptom check deleted successfully"
}
```

### Get Diseases List

**GET** `/symptoms/diseases`

Get list of diseases that can be predicted.

**Response** (200):
```json
{
  "diseases": [
    "Common Cold",
    "Pneumonia",
    "COVID-19",
    ...
  ],
  "count": 25
}
```

---

## 📊 Dashboard

### Get Statistics

**GET** `/dashboard/stats`

Get dashboard statistics (authenticated).

**Response for Doctor** (200):
```json
{
  "stats": {
    "overview": {
      "total_patients": 50,
      "total_xray_reports": 120,
      "total_symptom_checks": 85,
      "urgent_cases": 5
    },
    "disease_distribution": [
      { "disease": "Normal", "count": 60 },
      { "disease": "Pneumonia", "count": 35 }
    ],
    "urgency_distribution": [
      { "level": "mild", "count": 40 },
      { "level": "moderate", "count": 30 },
      { "level": "severe", "count": 15 }
    ],
    "recent_activity": {
      "xrays_last_7_days": 15,
      "symptoms_last_7_days": 12
    }
  },
  "role": "doctor"
}
```

**Response for Patient** (200):
```json
{
  "stats": {
    "overview": {
      "total_xray_reports": 3,
      "total_symptom_checks": 2,
      "latest_xray": { ... },
      "latest_symptom": { ... }
    }
  },
  "role": "patient"
}
```

### Get All Patients

**GET** `/dashboard/patients`

Get list of all patients (doctor only).

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `search`: Search by name

**Response** (200):
```json
{
  "patients": [
    {
      "id": 1,
      "full_name": "John Doe",
      "gender": "Male",
      "phone": "555-0100",
      "xray_count": 3,
      "symptom_count": 2,
      "latest_xray": { ... },
      "latest_symptom": { ... }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

### Get Patient Details

**GET** `/dashboard/patient/<id>`

Get detailed information about specific patient (doctor only).

**Response** (200):
```json
{
  "patient": {
    "id": 1,
    "full_name": "John Doe",
    "gender": "Male",
    "phone": "555-0100",
    "xray_reports": [ ... ],
    "symptom_checks": [ ... ]
  }
}
```

### Get Alerts

**GET** `/dashboard/alerts`

Get alerts for urgent cases (authenticated).

**Response** (200):
```json
{
  "alerts": [
    {
      "id": 1,
      "patient_id": 1,
      "patient_name": "John Doe",
      "alert_type": "xray",
      "message": "Abnormal X-ray detected: Pneumonia (87% confidence)",
      "severity": "high",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

### Mark Alert as Read

**PUT** `/dashboard/alert/<id>/read`

Mark alert as read (doctor only).

**Response** (200):
```json
{
  "message": "Alert marked as read"
}
```

### Get Trends

**GET** `/dashboard/analytics/trends`

Get disease trends over time (doctor only).

**Query Parameters**:
- `days`: Number of days (default: 30)

**Response** (200):
```json
{
  "xray_trends": [
    {
      "date": "2024-01-15",
      "disease": "Pneumonia",
      "count": 3
    }
  ],
  "symptom_trends": [ ... ],
  "period_days": 30
}
```

---

## 🔧 Health Check

### API Health

**GET** `/health`

Check if API is running.

**Response** (200):
```json
{
  "status": "healthy",
  "message": "AI Health Diagnostic System API is running"
}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "error": "Missing field: email"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "error": "Unauthorized - Doctor access required"
}
```

### 404 Not Found
```json
{
  "error": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- File uploads limited to 16MB
- Supported image formats: PNG, JPG, JPEG
- JWT tokens expire after 24 hours
- Refresh tokens expire after 30 days

---

**For more information, see the [SETUP_GUIDE.md](./SETUP_GUIDE.md)**










