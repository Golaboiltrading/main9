import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const ProductAnalysisPage = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  });

  const analyzeDocument = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/analyze-document`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysis(result);
      } else {
        throw new Error('Analysis failed');
      }
    } catch (err) {
      setError('Failed to analyze document. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        {/* Header with Disclaimer */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Oil & Gas Product Analysis
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
            Upload oil & gas documents for instant product analysis. Get quality assessments, 
            specification verification, and technical recommendations.
          </p>
          
          {/* Important Disclaimer */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-4xl mx-auto">
            <h3 className="font-bold text-red-800 mb-3 flex items-center">
              ⚠️ IMPORTANT DISCLAIMER
            </h3>
            <div className="text-red-700 text-sm space-y-2 text-left">
              <p><strong>• Analysis Tool Only:</strong> This is a preliminary analysis tool. Results are not certified or guaranteed.</p>
              <p><strong>• Not Professional Advice:</strong> Do not rely solely on this analysis for trading decisions.</p>
              <p><strong>• Independent Verification Required:</strong> Always verify specifications with certified laboratories.</p>
              <p><strong>• No Liability:</strong> We are not responsible for any trading decisions based on this analysis.</p>
              <p><strong>• Connection Platform:</strong> We only provide connections to trading partners, not trading services.</p>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6">Upload Product Document</h2>
            
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive 
                  ? 'border-orange-500 bg-orange-50' 
                  : 'border-gray-300 hover:border-orange-400'
              }`}
            >
              <input {...getInputProps()} />
              <div className="text-6xl mb-4">📄</div>
              {isDragActive ? (
                <p className="text-orange-600 text-lg">Drop the document here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 text-lg mb-2">
                    Drag & drop a product document here, or click to select
                  </p>
                  <p className="text-gray-500 text-sm">
                    Supports PDF, JPG, PNG (Max 10MB) • Product specs, certificates, test reports
                  </p>
                </div>
              )}
            </div>

            {uploadedFile && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{uploadedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={analyzeDocument}
                    disabled={loading}
                    className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50"
                  >
                    {loading ? 'Analyzing...' : 'Analyze Product'}
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">{error}</p>
              </div>
            )}
          </div>

          {/* Analysis Results */}
          {analysis && (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6">Product Analysis Results</h2>
              
              {/* Overall Assessment */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4">Overall Assessment</h3>
                <div className={`p-4 rounded-lg ${
                  analysis.overall_score > 80 ? 'bg-green-50 border border-green-200' :
                  analysis.overall_score > 60 ? 'bg-yellow-50 border border-yellow-200' :
                  'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">Quality Score</span>
                    <span className={`text-2xl font-bold ${
                      analysis.overall_score > 80 ? 'text-green-600' :
                      analysis.overall_score > 60 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {analysis.overall_score}/100
                    </span>
                  </div>
                  <p className="text-gray-700">{analysis.summary}</p>
                </div>
              </div>

              {/* Product Classification */}
              {analysis.product_classification && (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold mb-4">Product Classification</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="font-semibold text-gray-700">Product Type</div>
                      <div className="text-lg">{analysis.product_classification.type}</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="font-semibold text-gray-700">API Gravity</div>
                      <div className="text-lg">{analysis.product_classification.api_gravity || 'N/A'}</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="font-semibold text-gray-700">Sulfur Content</div>
                      <div className="text-lg">{analysis.product_classification.sulfur_content || 'N/A'}</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="font-semibold text-gray-700">Quality Grade</div>
                      <div className="text-lg">{analysis.product_classification.grade || 'N/A'}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Red Flags - Always show section */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4 text-red-600 flex items-center">
                  ⚠️ Risk Assessment & Red Flags
                </h3>
                {analysis.red_flags && analysis.red_flags.length > 0 ? (
                  <div className="space-y-3">
                    {analysis.red_flags.map((flag, index) => (
                      <div key={index} className="bg-red-50 border border-red-200 p-4 rounded-lg">
                        <div className="flex items-start">
                          <div className="text-red-500 text-xl mr-3">⚠️</div>
                          <div>
                            <div className="font-semibold text-red-800">{flag.type}</div>
                            <div className="text-red-700">{flag.description}</div>
                            <div className="text-sm text-red-600 mt-1">
                              Risk Level: <span className="font-semibold">{flag.severity}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                    <div className="flex items-center">
                      <div className="text-green-500 text-xl mr-3">✅</div>
                      <div>
                        <div className="font-semibold text-green-800">No Major Red Flags Detected</div>
                        <div className="text-green-700">Initial analysis shows standard product documentation</div>
                        <div className="text-sm text-green-600 mt-1">
                          Note: This is a preliminary assessment. Independent verification still required.
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Technical Analysis */}
              {analysis.technical_analysis && (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold mb-4">Technical Analysis</h3>
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="space-y-4">
                      {analysis.technical_analysis.map((item, index) => (
                        <div key={index} className="border-b border-gray-200 pb-3 last:border-b-0">
                          <div className="font-semibold text-gray-800">{item.parameter}</div>
                          <div className="text-gray-700">{item.value}</div>
                          {item.recommendation && (
                            <div className="text-sm text-blue-600 mt-1">
                              💡 {item.recommendation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Market Insights */}
              {analysis.market_insights && (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold mb-4">Market Insights</h3>
                  <div className="bg-blue-50 p-6 rounded-lg">
                    <div className="space-y-3">
                      {analysis.market_insights.map((insight, index) => (
                        <div key={index} className="flex items-start">
                          <div className="text-blue-500 text-lg mr-3">💡</div>
                          <div className="text-blue-800">{insight}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {analysis.recommendations && (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold mb-4">Recommendations</h3>
                  <div className="bg-green-50 p-6 rounded-lg">
                    <div className="space-y-3">
                      {analysis.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start">
                          <div className="text-green-500 text-lg mr-3">✅</div>
                          <div className="text-green-800">{rec}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Final Disclaimer */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h4 className="font-bold text-yellow-800 mb-3">⚠️ IMPORTANT REMINDER</h4>
                <div className="text-yellow-700 text-sm space-y-1">
                  <p>• This analysis is for informational purposes only and should not be used as the sole basis for trading decisions</p>
                  <p>• Always conduct independent laboratory testing and verification before any transactions</p>
                  <p>• Consult with qualified professionals for technical and commercial advice</p>
                  <p>• Oil & Gas Finder provides connection services only - we do not trade commodities</p>
                </div>
              </div>
            </div>
          )}

          {/* Sample Analysis Demo */}
          {!analysis && !loading && (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6">What Our Product Analysis Covers</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-orange-600">Document Types Supported</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center"><span className="mr-2">📄</span> Product specifications</li>
                    <li className="flex items-center"><span className="mr-2">🧪</span> Laboratory reports</li>
                    <li className="flex items-center"><span className="mr-2">📋</span> Inspection certificates</li>
                    <li className="flex items-center"><span className="mr-2">📊</span> Quality assessments</li>
                    <li className="flex items-center"><span className="mr-2">🛡️</span> Safety datasheets</li>
                  </ul>
                </div>
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-green-600">Analysis Features</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-center"><span className="mr-2">🔍</span> Quality verification</li>
                    <li className="flex items-center"><span className="mr-2">⚠️</span> Red flag detection</li>
                    <li className="flex items-center"><span className="mr-2">🏷️</span> Product classification</li>
                    <li className="flex items-center"><span className="mr-2">💡</span> Technical recommendations</li>
                    <li className="flex items-center"><span className="mr-2">📈</span> Market insights</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductAnalysisPage;