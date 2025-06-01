import React, { useState, useEffect } from 'react';

// Prominent disclaimer banner component
export const DisclaimerBanner = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isAccepted, setIsAccepted] = useState(false);

  useEffect(() => {
    // Check if user has already accepted disclaimer
    const accepted = localStorage.getItem('disclaimer_accepted');
    if (!accepted) {
      setIsVisible(true);
    } else {
      setIsAccepted(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('disclaimer_accepted', 'true');
    localStorage.setItem('disclaimer_date', new Date().toISOString());
    setIsVisible(false);
    setIsAccepted(true);
  };

  const handleDecline = () => {
    // Redirect away from platform
    window.location.href = 'https://google.com';
  };

  if (!isVisible && isAccepted) {
    return null;
  }

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
          {/* Header */}
          <div className="bg-red-600 text-white p-6 rounded-t-lg">
            <h2 className="text-2xl font-bold flex items-center">
              <span className="mr-3">⚠️</span>
              CRITICAL LEGAL DISCLAIMER
            </h2>
            <p className="mt-2 text-red-100">
              Please read carefully before using Oil & Gas Finder
            </p>
          </div>
          
          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Main Warning */}
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <h3 className="font-bold text-yellow-800 text-lg mb-2">
                PLATFORM LIMITATION NOTICE
              </h3>
              <p className="text-yellow-700">
                Oil & Gas Finder is a <strong>connection platform only</strong>. We do not participate in, 
                guarantee, or take responsibility for any transactions between users.
              </p>
            </div>
            
            {/* Sanctions Warning */}
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <h3 className="font-bold text-red-800 text-lg mb-2">
                SANCTIONS COMPLIANCE WARNING
              </h3>
              <p className="text-red-700">
                Users are <strong>solely responsible</strong> for ensuring compliance with all applicable 
                international sanctions (US, EU, UN). Oil & Gas Finder provides no sanctions guidance 
                and accepts no liability for violations.
              </p>
            </div>
            
            {/* Fraud Warning */}
            <div className="bg-orange-50 border-l-4 border-orange-500 p-4">
              <h3 className="font-bold text-orange-800 text-lg mb-2">
                FRAUD & SCAM WARNING
              </h3>
              <p className="text-orange-700">
                The oil & gas industry experiences frequent fraud. Common scams include fake refineries, 
                advance fee fraud, and document forgery. <strong>Conduct thorough due diligence</strong> 
                before any transactions.
              </p>
            </div>
            
            {/* No Responsibility */}
            <div className="bg-gray-50 border-l-4 border-gray-500 p-4">
              <h3 className="font-bold text-gray-800 text-lg mb-2">
                NO RESPONSIBILITY DISCLAIMER
              </h3>
              <p className="text-gray-700">
                Oil & Gas Finder accepts <strong>no responsibility</strong> for:
              </p>
              <ul className="list-disc list-inside text-gray-700 mt-2 space-y-1">
                <li>Fraudulent activities or scams by users</li>
                <li>Financial losses or transaction disputes</li>
                <li>Sanctions violations or regulatory issues</li>
                <li>Product quality, delivery, or payment problems</li>
                <li>Identity verification or user credentials</li>
              </ul>
            </div>
            
            {/* Recommendations */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
              <h3 className="font-bold text-blue-800 text-lg mb-2">
                STRONGLY RECOMMENDED
              </h3>
              <p className="text-blue-700">
                Before engaging in transactions, consult with:
              </p>
              <ul className="list-disc list-inside text-blue-700 mt-2 space-y-1">
                <li>Legal counsel specializing in energy law</li>
                <li>Sanctions compliance specialists</li>
                <li>Financial advisors familiar with commodity trading</li>
                <li>Industry verification services</li>
              </ul>
            </div>
            
            {/* Age and Competency */}
            <div className="bg-purple-50 border-l-4 border-purple-500 p-4">
              <h3 className="font-bold text-purple-800 text-lg mb-2">
                USER REQUIREMENTS
              </h3>
              <p className="text-purple-700">
                By using this platform, you confirm that you are:
              </p>
              <ul className="list-disc list-inside text-purple-700 mt-2 space-y-1">
                <li>18+ years old and legally competent</li>
                <li>Authorized to bind your organization (if applicable)</li>
                <li>Familiar with oil & gas trading risks</li>
                <li>Capable of conducting proper due diligence</li>
              </ul>
            </div>
            
            {/* Legal Links */}
            <div className="text-sm text-gray-600">
              <p>
                For complete terms, please review our{' '}
                <a href="/terms" className="text-blue-600 underline">Terms of Service</a>,{' '}
                <a href="/privacy" className="text-blue-600 underline">Privacy Policy</a>, and{' '}
                <a href="/disclaimer" className="text-blue-600 underline">Legal Disclaimer</a>.
              </p>
            </div>
          </div>
          
          {/* Footer Actions */}
          <div className="bg-gray-50 px-6 py-4 rounded-b-lg flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleDecline}
              className="flex-1 bg-gray-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
            >
              I DO NOT AGREE - Exit Platform
            </button>
            <button
              onClick={handleAccept}
              className="flex-1 bg-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-700 transition-colors"
            >
              I UNDERSTAND & ACCEPT ALL RISKS
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

// Persistent footer disclaimer
export const FooterDisclaimer = () => {
  return (
    <div className="bg-red-50 border-t-2 border-red-200 py-3">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between text-sm">
          <p className="text-red-700 font-medium">
            ⚠️ Platform connects users only - No responsibility for transactions, sanctions, or fraud
          </p>
          <div className="flex space-x-4 mt-2 sm:mt-0">
            <a href="/disclaimer" className="text-red-600 hover:text-red-800 underline">
              Legal Disclaimer
            </a>
            <a href="/terms" className="text-red-600 hover:text-red-800 underline">
              Terms
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

// Header warning banner (smaller, persistent)
export const HeaderWarning = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return null;
  }

  return (
    <div className="bg-yellow-400 text-yellow-900 py-2">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between text-sm">
          <p className="font-medium">
            ⚠️ Connection platform only - Users responsible for sanctions compliance & fraud prevention
          </p>
          <button
            onClick={() => setIsVisible(false)}
            className="text-yellow-700 hover:text-yellow-900"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};

