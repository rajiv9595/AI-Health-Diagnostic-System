import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { symptomAPI } from '../../services/api';
import { MessageSquare, Send, AlertCircle, Loader } from 'lucide-react';
import { toast } from 'react-toastify';

const SymptomChecker = () => {
  const [symptoms, setSymptoms] = useState('');
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);
  const [parsed, setParsed] = useState(null);
  const [useAdvanced, setUseAdvanced] = useState(false);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await symptomAPI.getHistory();
      setHistory(response.data.checks);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!symptoms.trim()) {
      toast.error('Please describe your symptoms');
      return;
    }

    setChecking(true);

    try {
      // Use v2 endpoint with free text
      const response = await symptomAPI.checkV2({ text: symptoms.trim(), use_advanced: useAdvanced });
      setResult(response.data.result);
      setParsed(response.data.parsed);
      toast.success('Symptoms analyzed successfully!');
      fetchHistory(); // Refresh history
      setSymptoms('');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze symptoms');
    } finally {
      setChecking(false);
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'severe':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Symptom Checker</h1>
          <p className="text-gray-600 mt-1">Describe your symptoms to get AI-powered health insights</p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Describe Your Symptoms</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Example: I have fever, cough, and difficulty breathing..."
                    rows={6}
                    className="input-field resize-none"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Be specific about your symptoms, duration, and severity
                  </p>
                </div>

                {/* Advanced model toggle */}
                <label className="flex items-center space-x-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={useAdvanced}
                    onChange={(e) => setUseAdvanced(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <span>Use advanced model (if available)</span>
                </label>

                <button
                  type="submit"
                  disabled={checking || !symptoms.trim()}
                  className="w-full btn-primary flex items-center justify-center space-x-2"
                >
                  {checking ? (
                    <Loader className="h-5 w-5 animate-spin" />
                  ) : (
                    <>
                      <Send className="h-5 w-5" />
                      <span>Analyze Symptoms</span>
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Quick Examples */}
            <div className="card bg-blue-50 border border-blue-200">
              <h3 className="font-semibold text-gray-900 mb-3">Example Symptoms</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• "Fever, cough, and chest pain for 3 days"</li>
                <li>• "Severe headache, nausea, and sensitivity to light"</li>
                <li>• "Persistent fatigue, increased thirst, and blurred vision"</li>
                <li>• "Shortness of breath, chest tightness, and wheezing"</li>
              </ul>
            </div>
          </div>

          {/* Results Section */}
          <div className="card h-full flex flex-col">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Result</h2>

            {checking ? (
              <div className="flex flex-col items-center justify-center py-12 flex-1">
                <div className="relative">
                  <div className="h-16 w-16 rounded-full border-b-2 border-primary-600 animate-spin"></div>
                  <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-t-2 border-purple-500 animate-ping opacity-20"></div>
                </div>
                <p className="mt-4 text-gray-600 font-medium animate-pulse">Consulting medical knowledge base...</p>
                <div className="mt-2 text-xs text-gray-400">Processing natural language inputs</div>
              </div>
            ) : result ? (
              <div className="space-y-6 flex-1 animate-fade-in-up">
                {/* Parsed Entities */}
                {parsed && (
                  <div className="p-3 bg-gray-50 rounded border border-gray-200">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Detailed Understanding</h4>
                    <div className="flex flex-wrap gap-2">
                      {(parsed.extracted || []).map((s, i) => (
                        <span key={`e-${i}`} className="px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100 flex items-center">
                          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1.5"></span>
                          {s}
                        </span>
                      ))}
                      {(parsed.negated || []).map((s, i) => (
                        <span key={`n-${i}`} className="px-2 py-1 rounded-md text-xs text-gray-500 border border-gray-200 bg-gray-50 line-through opacity-70">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Primary Prediction */}
                <div className={`p-5 rounded-xl border-l-4 shadow-sm ${getUrgencyColor(result.urgency_level).replace('bg-', 'bg-opacity-10 bg-')}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h5 className="text-xs font-bold uppercase tracking-wide opacity-70 mb-1">Top Prediction</h5>
                      <h3 className="text-2xl font-bold mb-1 flex items-center">
                        {result.predicted_disease}
                        {result.urgency_level === 'severe' && (
                          <span className="ml-2 relative flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                          </span>
                        )}
                      </h3>
                      <p className="text-sm font-medium opacity-80">
                        Confidence: {(result.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase border ${result.urgency_level === 'severe' ? 'border-red-200 text-red-700 bg-red-50' :
                        result.urgency_level === 'moderate' ? 'border-yellow-200 text-yellow-700 bg-yellow-50' :
                          'border-green-200 text-green-700 bg-green-50'
                      }`}>
                      {result.urgency_level}
                    </div>
                  </div>

                  {/* Confidence Bar */}
                  <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                    <div
                      className={`h-2.5 rounded-full ${result.confidence > 0.7 ? 'bg-green-500' : result.confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                      style={{ width: `${result.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <div className="bg-primary-100 p-1.5 rounded-lg mr-2">
                      <MessageSquare className="h-4 w-4 text-primary-600" />
                    </div>
                    Suggested Actions
                  </h4>
                  <ul className="space-y-3">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start p-3 bg-white border border-gray-100 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        <span className="flex-shrink-0 h-5 w-5 rounded-full bg-primary-50 text-primary-600 flex items-center justify-center text-xs font-bold mt-0.5 mr-3">
                          {index + 1}
                        </span>
                        <span className="text-sm text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Alternative Predictions */}
                {result.top_predictions && result.top_predictions.length > 1 && (
                  <div className="pt-4 border-t border-gray-100">
                    <button
                      className="text-xs font-medium text-gray-500 hover:text-primary-600 flex items-center mb-2"
                      onClick={() => toast.info("Showing alternative diagnoses considered by the AI")}
                    >
                      Other possibilities considered
                    </button>
                    <div className="space-y-2">
                      {result.top_predictions.slice(1, 3).map((pred, index) => (
                        <div key={index} className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">{pred.disease}</span>
                          <span className="font-medium text-gray-400">{(pred.confidence * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Disclaimer */}
                <div className="bg-orange-50 border border-orange-100 p-3 rounded-lg flex items-start">
                  <AlertCircle className="h-5 w-5 text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                  <p className="text-xs text-orange-800">
                    <strong>Medical Disclaimer:</strong> This analysis is generated by AI and may be inaccurate. It is not a clinical diagnosis. Please verify all information with a healthcare provider.
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500 flex flex-col items-center justify-center flex-1">
                <div className="bg-gray-50 p-6 rounded-full mb-4">
                  <MessageSquare className="h-12 w-12 text-gray-300" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">Ready to Analyze</h3>
                <p className="text-sm text-gray-400 mt-1 max-w-xs mx-auto">Describe your symptoms in detail on the left to receive an AI-powered assessment.</p>
              </div>
            )}
          </div>
        </div>

        {/* History */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Previous Checks</h2>

          {loading ? (
            <div className="flex justify-center py-8">
              <Loader className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : history.length > 0 ? (
            <div className="space-y-3">
              {history.map((check) => (
                <div key={check.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-medium text-gray-900">{check.predicted_disease}</p>
                      <p className="text-sm text-gray-600">{check.symptoms}</p>
                    </div>
                    <span className={`badge-${check.urgency_level === 'severe' ? 'error' :
                        check.urgency_level === 'moderate' ? 'warning' : 'success'
                      }`}>
                      {check.urgency_level}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {new Date(check.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No previous symptom checks</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SymptomChecker;


