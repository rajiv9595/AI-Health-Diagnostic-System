import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { dashboardAPI, xrayAPI, symptomAPI } from '../../services/api';
import {
  Activity,
  ImageIcon,
  MessageSquare,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { toast } from 'react-toastify';

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PatientDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentXrays, setRecentXrays] = useState([]);
  const [recentSymptoms, setRecentSymptoms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [healthScore, setHealthScore] = useState(100);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const calculateHealthScore = (xrays, symptoms) => {
    let score = 100;
    // Analyze last 5 xrays
    xrays.slice(0, 5).forEach(r => {
      if (r.predicted_class !== 'Normal') score -= 15;
    });
    // Analyze last 5 symptom checks
    symptoms.slice(0, 5).forEach(s => {
      if (s.urgency_level === 'severe') score -= 20;
      else if (s.urgency_level === 'moderate') score -= 10;
    });
    return Math.max(0, Math.min(100, score));
  };

  const fetchDashboardData = async () => {
    try {
      const [statsRes, xraysRes, symptomsRes] = await Promise.all([
        dashboardAPI.getStats(),
        xrayAPI.getReports(),
        symptomAPI.getHistory(),
      ]);

      setStats(statsRes.data.stats);
      const xrays = xraysRes.data.reports;
      const symptoms = symptomsRes.data.checks;

      setRecentXrays(xrays.slice(0, 3));
      setRecentSymptoms(symptoms.slice(0, 3));
      setHealthScore(calculateHealthScore(xrays, symptoms));

    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  const overview = stats?.overview || {};

  // Mock data for chart if not enough history
  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Wellness Score',
        data: [85, 88, 92, 90, 85, healthScore],
        fill: true,
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgb(59, 130, 246)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
      },
    },
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-primary-600 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold mb-2">Welcome to Your Health Dashboard</h1>
              <p className="opacity-90">Track your health reports and get AI-powered insights</p>
            </div>
            <div className="hidden md:block text-right">
              <div className="text-sm opacity-80">Current Health Score</div>
              <div className="text-4xl font-bold">{healthScore}</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/patient/xray"
            className="card hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 cursor-pointer group"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-4 rounded-xl group-hover:bg-blue-600 transition-colors duration-300">
                <ImageIcon className="h-8 w-8 text-blue-600 group-hover:text-white transition-colors duration-300" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Upload X-ray</h3>
                <p className="text-sm text-gray-600">Analyze chest X-rays with AI</p>
              </div>
            </div>
          </Link>

          <Link
            to="/patient/symptoms"
            className="card hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 cursor-pointer group"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 p-4 rounded-xl group-hover:bg-green-600 transition-colors duration-300">
                <MessageSquare className="h-8 w-8 text-green-600 group-hover:text-white transition-colors duration-300" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Check Symptoms</h3>
                <p className="text-sm text-gray-600">AI symptom analysis</p>
              </div>
            </div>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Statistics Cards */}
          <div className="lg:col-span-1 space-y-4">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total X-rays</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {overview.total_xray_reports || 0}
                  </p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <ImageIcon className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Symptom Checks</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {overview.total_symptom_checks || 0}
                  </p>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <MessageSquare className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="card bg-purple-50 border-purple-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-700">Health Status</p>
                  <p className={`text-2xl font-bold mt-1 ${healthScore > 80 ? 'text-green-600' : healthScore > 50 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                    {healthScore > 80 ? 'Excellent' : healthScore > 50 ? 'Fair' : 'Attention Needed'}
                  </p>
                </div>
                <div className="bg-white p-2 rounded-full shadow-sm">
                  <Activity className="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div className="mt-3 w-full bg-purple-200 rounded-full h-1.5">
                <div className="bg-purple-600 h-1.5 rounded-full transition-all duration-1000" style={{ width: `${healthScore}%` }}></div>
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="card lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Wellness Trends</h3>
              <div className="bg-gray-100 px-3 py-1 rounded-full text-xs text-gray-600">Last 6 Months</div>
            </div>
            <div className="h-64 w-full">
              <Line options={chartOptions} data={chartData} />
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent X-rays */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent X-rays</h3>
              <Link to="/patient/xray" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </Link>
            </div>

            {recentXrays.length > 0 ? (
              <div className="space-y-3">
                {recentXrays.map((xray) => (
                  <div key={xray.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <ImageIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{xray.predicted_class}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(xray.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className={`badge-${xray.predicted_class === 'Normal' ? 'success' : 'warning'}`}>
                      {(xray.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No X-ray reports yet</p>
                <Link to="/patient/xray" className="text-sm text-primary-600 hover:underline mt-2 inline-block">
                  Upload your first X-ray
                </Link>
              </div>
            )}
          </div>

          {/* Recent Symptom Checks */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Symptom Checks</h3>
              <Link to="/patient/symptoms" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </Link>
            </div>

            {recentSymptoms.length > 0 ? (
              <div className="space-y-3">
                {recentSymptoms.map((symptom) => (
                  <div key={symptom.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <MessageSquare className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{symptom.predicted_disease}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(symptom.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className={`badge-${symptom.urgency_level === 'severe' ? 'error' :
                        symptom.urgency_level === 'moderate' ? 'warning' : 'success'
                      }`}>
                      {symptom.urgency_level}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No symptom checks yet</p>
                <Link to="/patient/symptoms" className="text-sm text-primary-600 hover:underline mt-2 inline-block">
                  Start symptom checker
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Health Tips */}
        <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Health Reminder</h3>
              <ul className="space-y-1 text-sm text-gray-700">
                <li>• This AI system is for educational purposes only</li>
                <li>• Always consult healthcare professionals for medical decisions</li>
                <li>• Keep your health records up to date</li>
                <li>• Regular check-ups are important for early detection</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PatientDashboard;










