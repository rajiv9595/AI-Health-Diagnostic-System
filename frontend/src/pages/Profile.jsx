import React, { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Phone, Briefcase } from 'lucide-react';
import { toast } from 'react-toastify';

const Profile = () => {
  const { user } = useAuth();
  const profile = user?.profile || {};
  const healthScore = profile?.health_score;
  const healthTip = profile?.health_tip;

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
          <p className="text-gray-600 mt-1">View your account information</p>
        </div>

        {/* Profile Card */}
        <div className="card">
          <div className="flex items-center space-x-4 mb-6 pb-6 border-b border-gray-200">
            <div className="bg-primary-100 p-4 rounded-full">
              <User className="h-12 w-12 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{profile.full_name}</h2>
              <p className="text-sm text-gray-600 capitalize">{user?.role}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <Mail className="h-5 w-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-gray-900">{user?.email}</p>
              </div>
            </div>

            {profile.phone && (
              <div className="flex items-start space-x-3">
                <Phone className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="text-gray-900">{profile.phone}</p>
                </div>
              </div>
            )}

            {user?.role === 'doctor' && profile.specialization && (
              <div className="flex items-start space-x-3">
                <Briefcase className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Specialization</p>
                  <p className="text-gray-900">{profile.specialization}</p>
                </div>
              </div>
            )}

            {user?.role === 'doctor' && profile.hospital && (
              <div className="flex items-start space-x-3">
                <Briefcase className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Hospital</p>
                  <p className="text-gray-900">{profile.hospital}</p>
                </div>
              </div>
            )}

            {user?.role === 'patient' && profile.address && (
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Address</p>
                  <p className="text-gray-900">{profile.address}</p>
                </div>
              </div>
            )}

            {user?.role === 'patient' && profile.date_of_birth && (
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Date of Birth</p>
                  <p className="text-gray-900">{new Date(profile.date_of_birth).toLocaleDateString()}</p>
                </div>
              </div>
            )}

            {user?.role === 'patient' && typeof healthScore === 'number' && (
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200">
                <span className="text-sm text-gray-700">Health Score</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  healthScore >= 80 ? 'bg-green-100 text-green-800' : healthScore >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                }`}>
                  {healthScore}/100
                </span>
              </div>
            )}

            {user?.role === 'patient' && healthTip && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-sm text-blue-800">{healthTip}</p>
              </div>
            )}
          </div>
        </div>

        {/* Account Info */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Account Type</p>
              <p className="text-gray-900 capitalize">{user?.role}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Member Since</p>
              <p className="text-gray-900">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="card bg-blue-50 border border-blue-200">
          <h3 className="font-semibold text-gray-900 mb-2">System Information</h3>
          <p className="text-sm text-gray-700">
            This is a demo AI Health Diagnostic System for educational purposes only.
            All predictions are generated by AI models and should not be used for actual medical diagnosis.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;


