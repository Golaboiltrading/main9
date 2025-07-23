import React, { useState, useEffect } from 'react';

// Modal Banner Component
export const DisclaimerBanner = () => {
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Show modal on first visit
    const hasSeenDisclaimer = localStorage.getItem('oil_gas_finder_disclaimer_accepted');
    if (!hasSeenDisclaimer) {
      setShowModal(true);
      
      // Auto-dismiss after 10 seconds to prevent navigation blocking
      const autoDismissTimer = setTimeout(() => {
        acceptDisclaimer();
      }, 10000);
      
      return () => clearTimeout(autoDismissTimer);
    }
  }, []);

  const acceptDisclaimer = () => {
    localStorage.setItem('oil_gas_finder_disclaimer_accepted', 'true');
    setShowModal(false);
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <div className="text-3xl mr-3">⚠️</div>
            <h2 className="text-2xl font-bold text-red-600">IMPORTANT LEGAL NOTICE</h2>
          </div>
          
          <div className="space-y-4 text-gray-700">
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <h3 className="font-bold text-red-800 mb-2">🚨 SANCTIONS & COMPLIANCE WARNING</h3>
              <p className="text-sm">
                Oil & Gas Finder is a CONNECTION SERVICE ONLY. We do not engage in actual trading, 
                financing, or transaction processing. All users must comply with international sanctions, 
                export controls, and local regulations. We are not responsible for any illegal activities.
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
              <h3 className="font-bold text-yellow-800 mb-2">⚠️ FRAUD PROTECTION</h3>
              <p className="text-sm">
                Always verify trader credentials independently. Never transfer money without proper 
                documentation. Be aware of advance fee frauds, fake certificates, and too-good-to-be-true offers. 
                We provide a platform for connections only.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h3 className="font-bold text-blue-800 mb-2">ℹ️ PLATFORM LIMITATIONS</h3>
              <p className="text-sm">
                Our platform facilitates introductions between potential trading partners. We do not:
                • Verify product quality or authenticity
                • Handle payments or escrow services  
                • Guarantee successful transactions
                • Provide legal or financial advice
              </p>
            </div>

            <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
              <h3 className="font-bold text-gray-800 mb-2">📋 USER RESPONSIBILITIES</h3>
              <ul className="text-sm space-y-1">
                <li>• Conduct proper due diligence on all potential partners</li>
                <li>• Verify all documentation and certifications independently</li>
                <li>• Comply with all applicable laws and regulations</li>
                <li>• Use secure payment methods and proper contracts</li>
                <li>• Report suspicious activities to relevant authorities</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <button
              onClick={acceptDisclaimer}
              className="flex-1 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold"
            >
              I Understand & Accept
            </button>
            <button
              onClick={() => window.location.href = 'https://google.com'}
              className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-3 rounded-lg font-semibold"
            >
              Exit Site
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-4 text-center">
            By using this platform, you acknowledge that you have read and understood these warnings.
          </p>
        </div>
      </div>
    </div>
  );
};

// Header Warning Component
export const HeaderWarning = () => {
  return (
    <div className="bg-red-600 text-white py-2">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center text-center">
          <span className="text-sm font-medium">
            ⚠️ CONNECTION SERVICE ONLY - Verify all traders independently • Comply with sanctions • Beware of fraud
          </span>
        </div>
      </div>
    </div>
  );
};

// Footer Disclaimer Component
export const FooterDisclaimer = () => {
  return (
    <div className="bg-gray-900 text-gray-300 py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-white font-bold mb-3">Legal Disclaimer</h3>
            <p className="text-sm">
              Oil & Gas Finder operates as a connection service only. We do not engage in trading, 
              provide financial services, or guarantee transaction outcomes.
            </p>
          </div>
          
          <div>
            <h3 className="text-white font-bold mb-3">Risk Warning</h3>
            <p className="text-sm">
              Commodity trading involves substantial risk. Always conduct proper due diligence, 
              verify credentials, and comply with applicable regulations before engaging in any transactions.
            </p>
          </div>
          
          <div>
            <h3 className="text-white font-bold mb-3">Compliance Notice</h3>
            <p className="text-sm">
              Users must comply with international sanctions, export controls, and local laws. 
              Report suspicious activities to relevant authorities immediately.
            </p>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-sm text-gray-400">
            © 2024 Oil & Gas Finder. All rights reserved. | 
            <a href="/terms" className="hover:text-white ml-1">Terms of Service</a> | 
            <a href="/privacy" className="hover:text-white ml-1">Privacy Policy</a> | 
            <a href="/disclaimer" className="hover:text-white ml-1">Full Disclaimer</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default { DisclaimerBanner, HeaderWarning, FooterDisclaimer };