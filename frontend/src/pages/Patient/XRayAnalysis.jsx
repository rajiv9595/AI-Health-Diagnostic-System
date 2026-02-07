import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { xrayAPI } from '../../services/api';
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { toast } from 'react-toastify';

const XRayAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await xrayAPI.getReports();
      setReports(response.data.reports);
    } catch (error) {
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }

      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select an X-ray image');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await xrayAPI.upload(formData);
      setResult(response.data.report);
      toast.success('X-ray analyzed successfully!');
      fetchReports(); // Refresh reports list
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze X-ray');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">X-ray Analysis</h1>
          <p className="text-gray-600 mt-1">Upload chest X-ray images for AI-powered analysis</p>
        </div>

        {/* Upload Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Card */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload X-ray Image</h2>

            {!preview ? (
              <label className="block cursor-pointer">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-500 transition-colors">
                  <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
                  <p className="text-sm text-gray-500">PNG, JPG up to 16MB</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileSelect}
                />
              </label>
            ) : (
              <div className="space-y-4">
                <img
                  src={preview}
                  alt="X-ray preview"
                  className="w-full h-64 object-contain bg-gray-100 rounded-lg"
                />
                <div className="flex space-x-3">
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="flex-1 btn-primary"
                  >
                    {uploading ? (
                      <Loader className="h-5 w-5 animate-spin mx-auto" />
                    ) : (
                      'Analyze X-ray'
                    )}
                  </button>
                  <button
                    onClick={handleReset}
                    disabled={uploading}
                    className="flex-1 btn-secondary"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Result Card */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Result</h2>

            {result ? (
              <div className="space-y-6">
                <div className={`p-6 rounded-xl border-l-4 shadow-sm ${result.predicted_class === 'Normal'
                    ? 'bg-green-50 border-green-500'
                    : 'bg-red-50 border-red-500'
                  }`}>
                  <div className="flex items-center space-x-4 mb-3">
                    {result.predicted_class === 'Normal' ? (
                      <CheckCircle className="h-8 w-8 text-green-600" />
                    ) : (
                      <AlertCircle className="h-8 w-8 text-red-600" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {result.predicted_class} Detected
                      </h3>
                      <p className="text-sm font-medium text-gray-600">
                        Confidence: {(result.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>

                  {result.predicted_class !== 'Normal' && (
                    <div className="mt-2 text-sm text-red-700 bg-red-100 p-3 rounded-md">
                      <strong>⚠️ Attention:</strong> High probability of abnormality detected. Please consult a specialist immediately.
                    </div>
                  )}
                </div>

                {/* AI Interpretability Section (Grad-CAM) */}
                {result.gradcam_path && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50">
                      <h4 className="font-semibold text-gray-800 flex items-center">
                        <ImageIcon className="w-5 h-5 mr-2 text-primary-600" />
                        AI Visual Explanation (Grad-CAM)
                      </h4>
                    </div>
                    <div className="p-4 relative group">
                      <div className="aspect-w-4 aspect-h-3 bg-gray-900 rounded-lg overflow-hidden">
                        <img
                          src={xrayAPI.getImage(result.gradcam_path.split(/[\\/]/).pop())}
                          alt="AI Heatmap Visualization"
                          className="w-full h-full object-contain transform transition-transform duration-500 group-hover:scale-105"
                        />
                      </div>
                      <p className="mt-3 text-xs text-gray-500 text-center">
                        <span className="font-semibold text-primary-600">heatmap</span> highlights regions influencing the AI's diagnosis. Red areas indicate high attention.
                      </p>
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                    <span className="w-2 h-8 bg-primary-600 rounded-full mr-2"></span>
                    Detailed Probability Breakdown
                  </h4>
                  <div className="space-y-3">
                    {Object.entries(result.predictions).sort(([, a], [, b]) => b - a).map(([disease, confidence]) => (
                      <div key={disease} className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-200">
                              {disease}
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold inline-block text-primary-600">
                              {(confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary-100">
                          <div style={{ width: `${confidence * 100}%` }} className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${disease === result.predicted_class ? 'bg-primary-600' : 'bg-primary-300'
                            }`}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <p className="text-xs text-blue-800 flex items-center">
                    <span className="bg-blue-200 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded mr-2">NEW</span>
                    Enhanced Accuracy: Results are verified using Test-Time Augmentation (TTA).
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500 animate-fade-in-up">
                <div className={`transition-all duration-300 ${uploading ? 'scale-110 opacity-50' : 'scale-100 opacity-100'}`}>
                  <ImageIcon className="h-20 w-20 mx-auto mb-4 text-gray-300" />
                </div>
                <p className="text-lg font-medium text-gray-600">Ready for Analysis</p>
                <p className="text-sm mt-2 text-gray-400">Upload a chest X-ray to detect potential anomalies</p>
                {uploading && (
                  <div className="mt-6 flex flex-col items-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    <p className="text-sm text-primary-600 mt-2 font-medium animate-pulse">Analyzing image patterns...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Previous Reports */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Previous Reports</h2>

          {loading ? (
            <div className="flex justify-center py-8">
              <Loader className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : reports.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Prediction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(report.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report.predicted_class}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(report.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge-${report.status === 'urgent' ? 'error' :
                            report.status === 'reviewed' ? 'success' : 'info'
                          }`}>
                          {report.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No previous reports</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default XRayAnalysis;










