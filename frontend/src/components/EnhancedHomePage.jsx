import React, { useState, useEffect } from 'react';
import { LeadCaptureForm } from './Analytics';

export const EnhancedHomePage = ({ user, navigateToPage }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const heroImages = [
    'https://images.pexels.com/photos/3192669/pexels-photo-3192669.jpeg',
    'https://images.unsplash.com/photo-1521111756787-d2f69136cedf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHxwZXRyb2xldW0lMjBpbmR1c3RyeXxlbnwwfHx8fDE3NDg3NjAzNjN8MA&ixlib=rb-4.1.0&q=85',
    'https://images.pexels.com/photos/19091613/pexels-photo-19091613.jpeg'
  ];

  const heroTitles = [
    'Global Oil & Gas Trading Platform',
    'Connect with Verified Energy Traders',
    'AI-Powered Technical Analysis'
  ];

  const heroSubtitles = [
    'Premier platform connecting buyers and sellers worldwide with real-time market data and secure trading connections.',
    'Join thousands of verified oil and gas professionals in the world\'s most trusted trading network.',
    'Upload product specs and get instant AI analysis with red flag detection and technical recommendations.'
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroImages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-white">
      {/* Enhanced Hero Section with Slideshow */}
      <div className="relative h-screen overflow-hidden">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              index === currentSlide ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <div
              className="absolute inset-0 bg-cover bg-center bg-no-repeat"
              style={{ backgroundImage: `url(${image})` }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/50 to-transparent" />
          </div>
        ))}
        
        <div className="relative z-10 flex items-center justify-center h-full">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              {heroTitles[currentSlide]}
            </h1>
            <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-4xl mx-auto leading-relaxed">
              {heroSubtitles[currentSlide]}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <button
                onClick={() => navigateToPage('register')}
                className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Start Trading Now
              </button>
              <button
                onClick={() => navigateToPage('browse')}
                className="border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-gray-900 transform hover:scale-105 transition-all duration-200"
              >
                Browse Traders
              </button>
              <button
                onClick={() => navigateToPage('ai-analysis')}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-purple-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Try AI Analysis
              </button>
            </div>

            {/* Slide Indicators */}
            <div className="flex justify-center space-x-2">
              {heroImages.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-200 ${
                    index === currentSlide ? 'bg-white scale-125' : 'bg-white/50'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis Feature Highlight */}
      <div className="py-20 bg-gradient-to-r from-purple-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              🤖 AI-Powered Technical Analysis
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Upload product specifications and get instant expert-level analysis with red flag detection and technical recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-purple-500">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">📄 Document Analysis</h3>
                <p className="text-gray-600">
                  Upload PDFs or images of product specs, lab reports, or certificates. Our AI analyzes content instantly.
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">🔍 Red Flag Detection</h3>
                <p className="text-gray-600">
                  Automatic identification of quality issues, safety concerns, and compliance problems.
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">⚗️ Product Classification</h3>
                <p className="text-gray-600">
                  Identify heavy/light crude, API gravity, sulfur content, and other technical specifications.
                </p>
              </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-xl">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                Try AI Analysis Now
              </h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-500 transition-colors cursor-pointer">
                <div className="text-6xl mb-4">📁</div>
                <p className="text-lg text-gray-600 mb-4">
                  Drop your product specs here or click to upload
                </p>
                <button 
                  onClick={() => navigateToPage('ai-analysis')}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
                >
                  Upload Document
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Statistics Section */}
      <div className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-4xl font-bold text-blue-400">10,000+</div>
              <div className="text-gray-300">Verified Traders</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-green-400">$2.5B</div>
              <div className="text-gray-300">Trading Volume</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-purple-400">50+</div>
              <div className="text-gray-300">Countries</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-yellow-400">24/7</div>
              <div className="text-gray-300">Market Access</div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Features Grid */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose Oil & Gas Finder?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The most advanced and trusted platform for oil and gas trading professionals worldwide.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon="🔐"
              title="Verified Traders"
              description="All traders undergo thorough verification for secure and reliable transactions."
              image="https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=300&fit=crop"
            />
            <FeatureCard
              icon="📊"
              title="Real-time Market Data"
              description="Access live pricing, market trends, and trading insights from global energy markets."
              image="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=300&fit=crop"
            />
            <FeatureCard
              icon="🤖"
              title="AI Technical Analysis"
              description="Upload documents and get instant AI-powered analysis with red flag detection."
              image="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=300&fit=crop"
            />
            <FeatureCard
              icon="🌍"
              title="Global Network"
              description="Connect with traders from over 50 countries across all major energy markets."
              image="https://images.pexels.com/photos/379964/pexels-photo-379964.jpeg?w=400&h=300&fit=crop"
            />
            <FeatureCard
              icon="💰"
              title="Premium Features"
              description="Advanced tools and priority listings for serious trading professionals."
              image="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=300&fit=crop"
            />
            <FeatureCard
              icon="📰"
              title="Industry News"
              description="Stay updated with real-time oil and gas industry news and market analysis."
              image="https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop"
            />
          </div>
        </div>
      </div>

      {/* Enhanced CTA Section */}
      <div className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Join the world's most advanced oil and gas trading platform with AI-powered analysis and global reach.
          </p>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-white mb-4">Start Trading</h3>
              <p className="text-blue-100 mb-6">
                Create your free account and access thousands of verified traders worldwide.
              </p>
              <button
                onClick={() => navigateToPage('register')}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 w-full"
              >
                Create Free Account
              </button>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-white mb-4">AI Analysis</h3>
              <p className="text-blue-100 mb-6">
                Upload your first document and experience our advanced AI technical analysis.
              </p>
              <button
                onClick={() => navigateToPage('ai-analysis')}
                className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 w-full"
              >
                Try AI Analysis
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const FeatureCard = ({ icon, title, description, image }) => (
  <div className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
    <div className="h-48 bg-cover bg-center" style={{ backgroundImage: `url(${image})` }}>
      <div className="h-full bg-black bg-opacity-40 flex items-center justify-center">
        <div className="text-6xl">{icon}</div>
      </div>
    </div>
    <div className="p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  </div>
);

export default EnhancedHomePage;