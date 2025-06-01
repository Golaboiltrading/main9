import React, { useState, useRef } from 'react';
import { SEO } from './SEO';

export const AIAnalysisPage = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
      if (!allowedTypes.includes(file.type)) {
        setError('Please upload a PDF, JPG, or PNG file');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setUploadedFile(file);
      setError('');
      setAnalysis(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      const fakeEvent = { target: { files: [file] } };
      handleFileUpload(fakeEvent);
    }
  };

  const analyzeDocument = async () => {
    if (!uploadedFile) return;
    
    setAnalyzing(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', uploadedFile);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/analyze-document`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setAnalysis(result.analysis);
      } else {
        setError(result.message || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setError('Failed to analyze document. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const resetUpload = () => {
    setUploadedFile(null);
    setAnalysis(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      <SEO 
        title="AI Document Analysis | Oil & Gas Finder"
        description="Upload product specifications and get instant AI-powered analysis with red flag detection and technical recommendations."
        keywords="AI analysis, document analysis, oil gas specs, technical analysis, red flags"
        url="/ai-analysis"
      />
      
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold mb-4">🤖 AI Document Analysis</h1>
          <p className="text-xl text-purple-100">
            Upload product specifications and get instant expert-level analysis with red flag detection
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Document</h2>
              
              {!uploadedFile ? (
                <div
                  className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-purple-500 transition-colors cursor-pointer"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="text-8xl mb-4">📁</div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Drop your document here
                  </h3>
                  <p className="text-gray-500 mb-4">
                    or click to browse files
                  </p>
                  <div className="text-sm text-gray-400">
                    Supports: PDF, JPG, PNG (max 10MB)
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* File Preview */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-4xl">
                          {uploadedFile.type.includes('pdf') ? '📄' : '🖼️'}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{uploadedFile.name}</h3>
                          <p className="text-sm text-gray-500">
                            {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={resetUpload}
                        className="text-red-600 hover:text-red-800 font-semibold"
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {/* Analyze Button */}
                  <button
                    onClick={analyzeDocument}
                    disabled={analyzing}
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    {analyzing ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Analyzing Document...</span>
                      </div>
                    ) : (
                      '🔍 Analyze Document'
                    )}
                  </button>
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileUpload}
                className="hidden"
              />

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800">{error}</p>
                </div>
              )}
            </div>

            {/* Analysis Results */}
            {analysis && <AnalysisResults analysis={analysis} />}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <AnalysisFeatures />
            <SampleAnalysis />
          </div>
        </div>
      </div>
    </div>
  );
};

const AnalysisResults = ({ analysis }) => (
  <div className="bg-white rounded-2xl shadow-xl p-8 mt-8">
    <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Analysis Results</h2>
    
    <div className="space-y-6">
      {/* Product Classification */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">⚗️ Product Classification</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-blue-700 font-medium">Product Type:</span>
            <p className="text-blue-900 font-semibold">{analysis.product_type || 'Unknown'}</p>
          </div>
          <div>
            <span className="text-sm text-blue-700 font-medium">Grade:</span>
            <p className="text-blue-900 font-semibold">{analysis.grade || 'Not specified'}</p>
          </div>
          <div>
            <span className="text-sm text-blue-700 font-medium">API Gravity:</span>
            <p className="text-blue-900 font-semibold">{analysis.api_gravity || 'Not found'}</p>
          </div>
          <div>
            <span className="text-sm text-blue-700 font-medium">Sulfur Content:</span>
            <p className="text-blue-900 font-semibold">{analysis.sulfur_content || 'Not found'}</p>
          </div>
        </div>
      </div>

      {/* Red Flags */}
      {analysis.red_flags && analysis.red_flags.length > 0 && (
        <div className="bg-red-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-3">🚨 Red Flags Detected</h3>
          <ul className="space-y-2">
            {analysis.red_flags.map((flag, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="text-red-600 mt-1">⚠️</span>
                <span className="text-red-800">{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Technical Specifications */}
      {analysis.specifications && (
        <div className="bg-green-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-3">📋 Technical Specifications</h3>
          <div className="space-y-2">
            {Object.entries(analysis.specifications).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-green-700 font-medium capitalize">{key.replace('_', ' ')}:</span>
                <span className="text-green-900">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && (
        <div className="bg-purple-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-purple-900 mb-3">💡 Recommendations</h3>
          <ul className="space-y-2">
            {analysis.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="text-purple-600 mt-1">✓</span>
                <span className="text-purple-800">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Market Insights */}
      {analysis.market_insights && (
        <div className="bg-yellow-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">💰 Market Insights</h3>
          <p className="text-yellow-800">{analysis.market_insights}</p>
        </div>
      )}
    </div>

    {/* Disclaimer */}
    <div className="mt-8 bg-gray-100 rounded-lg p-4">
      <p className="text-sm text-gray-600">
        <strong>Disclaimer:</strong> This AI analysis is for informational purposes only and should not replace professional technical evaluation. Always conduct proper due diligence and consult with industry experts before making trading decisions.
      </p>
    </div>
  </div>
);

const AnalysisFeatures = () => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <h3 className="text-lg font-bold text-gray-900 mb-4">🔍 What We Analyze</h3>
    <div className="space-y-3">
      <div className="flex items-center space-x-3">
        <span className="text-blue-600">⚗️</span>
        <span className="text-gray-700">Product type & grade identification</span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-red-600">🚨</span>
        <span className="text-gray-700">Quality issues & red flags</span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-green-600">📊</span>
        <span className="text-gray-700">Technical specifications</span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-purple-600">🛡️</span>
        <span className="text-gray-700">Safety & compliance concerns</span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-yellow-600">💰</span>
        <span className="text-gray-700">Market value insights</span>
      </div>
    </div>
  </div>
);

const SampleAnalysis = () => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <h3 className="text-lg font-bold text-gray-900 mb-4">📄 Sample Analysis</h3>
    <div className="text-sm text-gray-600 space-y-2">
      <p><strong>Product:</strong> Light Sweet Crude Oil</p>
      <p><strong>API Gravity:</strong> 42.5°</p>
      <p><strong>Sulfur:</strong> 0.3% (Sweet)</p>
      <p><strong>Red Flags:</strong> None detected</p>
      <p><strong>Recommendation:</strong> Premium grade suitable for high-value markets</p>
    </div>
  </div>
);

export default AIAnalysisPage;