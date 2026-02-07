import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { dashboardAPI } from '../../services/api';
import { User, ArrowLeft, Activity, Loader } from 'lucide-react';
import { toast } from 'react-toastify';

const PatientDetails = () => {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatientDetails();
  }, [id]);

  const fetchPatientDetails = async () => {
    try {
      const response = await dashboardAPI.getPatientDetails(id);
      setPatient(response.data.patient);
    } catch (error) {
      toast.error('Failed to load patient details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loader className="h-12 w-12 animate-spin text-primary-600" />
        </div>
      </Layout>
    );
  }

  if (!patient) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Patient not found</p>
          <Link to="/doctor/patients" className="text-primary-600 hover:underline mt-4 inline-block">
            Back to Patients
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              to="/doctor/patients"
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Patient Details</h1>
              <p className="text-gray-600 mt-1">{patient.full_name}</p>
            </div>
          </div>
        </div>

        {/* Patient Info */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Full Name</p>
              <p className="text-gray-900 font-medium">{patient.full_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Gender</p>
              <p className="text-gray-900 font-medium">{patient.gender || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="text-gray-900 font-medium">{patient.phone || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Date of Birth</p>
              <p className="text-gray-900 font-medium">
                {patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString() : 'N/A'}
              </p>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm text-gray-600">Address</p>
              <p className="text-gray-900 font-medium">{patient.address || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* X-ray Reports */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">X-ray Reports</h2>
          {patient.xray_reports && patient.xray_reports.length > 0 ? (
            <div className="space-y-3">
              {patient.xray_reports.map((report) => (
                <div key={report.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{report.predicted_class}</p>
                      <p className="text-sm text-gray-600">
                        Confidence: {(report.confidence * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(report.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`badge-${report.status === 'urgent' ? 'error' : 'info'}`}>
                      {report.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No X-ray reports</p>
          )}
        </div>

        {/* Symptom Checks */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Symptom Check History</h2>
          {patient.symptom_checks && patient.symptom_checks.length > 0 ? (
            <div className="space-y-3">
              {patient.symptom_checks.map((check) => (
                <div key={check.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900">{check.predicted_disease}</p>
                    <span className={`badge-${
                      check.urgency_level === 'severe' ? 'error' : 
                      check.urgency_level === 'moderate' ? 'warning' : 'success'
                    }`}>
                      {check.urgency_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{check.symptoms}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(check.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No symptom checks</p>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PatientDetails;










