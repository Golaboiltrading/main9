import React from 'react';

export const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
          
          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Platform Description</h2>
              <p>
                Oil & Gas Finder operates as a CONNECTION SERVICE ONLY. We provide a platform for 
                potential trading partners to find and connect with each other. We do not engage in 
                actual trading, financing, escrow services, or transaction processing.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. User Responsibilities</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Conduct thorough due diligence on all potential trading partners</li>
                <li>Verify all documentation, certificates, and credentials independently</li>
                <li>Comply with all applicable international sanctions, export controls, and local laws</li>
                <li>Use secure payment methods and proper legal contracts</li>
                <li>Report suspicious or fraudulent activities immediately</li>
                <li>Provide accurate information when creating listings or profiles</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Platform Limitations</h2>
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="font-semibold text-yellow-800 mb-2">We explicitly DO NOT:</p>
                <ul className="list-disc pl-6 space-y-1 text-yellow-700">
                  <li>Verify product quality, authenticity, or specifications</li>
                  <li>Handle payments, escrow, or financial transactions</li>
                  <li>Guarantee successful completion of any deals</li>
                  <li>Provide legal, financial, or trading advice</li>
                  <li>Take responsibility for user actions or transactions</li>
                  <li>Verify the legitimacy of users or their business credentials</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Sanctions & Compliance</h2>
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <p className="text-red-700">
                  Users must comply with all applicable sanctions, export controls, and trade regulations 
                  including but not limited to US, EU, UN, and local jurisdiction requirements. Trading 
                  with sanctioned entities or in prohibited commodities is strictly forbidden.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Fraud Prevention</h2>
              <p>
                Users are strongly advised to be aware of common fraud schemes including advance fee 
                frauds, fake product certificates, non-existent refineries, and too-good-to-be-true offers. 
                Always verify independently and never transfer funds without proper documentation.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibent text-gray-900 mb-4">6. Limitation of Liability</h2>
              <p>
                Oil & Gas Finder shall not be liable for any direct, indirect, incidental, special, 
                or consequential damages arising from the use of our platform or any transactions 
                between users. Users engage at their own risk.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Account Termination</h2>
              <p>
                We reserve the right to terminate accounts for violations of these terms, suspicious 
                activities, or at our sole discretion without prior notice.
              </p>
            </section>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Last updated: December 2024 | These terms are subject to change without notice.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
          
          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Information We Collect</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Account information (name, email, company details)</li>
                <li>Trading preferences and listing data</li>
                <li>Communication records between users</li>
                <li>Usage analytics and platform interaction data</li>
                <li>IP addresses and device information</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">How We Use Information</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Facilitate connections between trading partners</li>
                <li>Improve platform functionality and user experience</li>
                <li>Send important platform updates and notifications</li>
                <li>Comply with legal requirements and sanctions screening</li>
                <li>Prevent fraud and maintain platform security</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Information Sharing</h2>
              <p>
                We do not sell personal information. We may share information with:
              </p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Other users as part of the connection service</li>
                <li>Legal authorities when required by law</li>
                <li>Service providers who assist in platform operations</li>
                <li>Compliance with sanctions and regulatory requirements</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Security</h2>
              <p>
                We implement industry-standard security measures to protect your information, 
                including encryption, secure servers, and regular security audits.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your Rights</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Access and update your personal information</li>
                <li>Request deletion of your account and data</li>
                <li>Opt-out of non-essential communications</li>
                <li>Data portability where applicable</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export const Disclaimer = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Full Legal Disclaimer</h1>
          
          <div className="space-y-6 text-gray-700">
            <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
              <h2 className="text-2xl font-semibold text-red-800 mb-4">⚠️ CRITICAL WARNINGS</h2>
              <div className="space-y-3 text-red-700">
                <p><strong>CONNECTION SERVICE ONLY:</strong> We are not traders, brokers, or dealers. We only provide a platform for introductions.</p>
                <p><strong>NO TRANSACTION INVOLVEMENT:</strong> We do not handle payments, escrow, or any financial aspects of trading.</p>
                <p><strong>NO GUARANTEES:</strong> We make no guarantees about user legitimacy, product quality, or transaction success.</p>
              </div>
            </div>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Sanctions & Regulatory Compliance</h2>
              <p>
                Users must comply with all applicable sanctions and export control regulations including:
              </p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>US OFAC sanctions and export controls</li>
                <li>EU sanctions and trade restrictions</li>
                <li>UN Security Council sanctions</li>
                <li>Local jurisdiction trade laws</li>
                <li>Industry-specific regulations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Common Fraud Schemes</h2>
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="font-semibold text-yellow-800 mb-2">Be aware of these common frauds:</p>
                <ul className="list-disc pl-6 space-y-1 text-yellow-700">
                  <li>Advance fee frauds requiring upfront payments</li>
                  <li>Fake product certificates and test reports</li>
                  <li>Non-existent refineries and storage facilities</li>
                  <li>Below-market pricing schemes</li>
                  <li>Fake bank guarantees and letters of credit</li>
                  <li>Identity theft and impersonation</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Due Diligence Requirements</h2>
              <p>Before engaging with any potential trading partner, you must:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Verify company registration and business licenses</li>
                <li>Confirm physical business addresses and facilities</li>
                <li>Validate bank references and financial standing</li>
                <li>Check sanctions and restricted party lists</li>
                <li>Obtain independent product quality verification</li>
                <li>Use proper legal contracts and secure payment methods</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Limitation of Liability</h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, OIL & GAS FINDER SHALL NOT BE LIABLE 
                FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES 
                ARISING FROM OR RELATED TO YOUR USE OF THE PLATFORM OR ANY TRANSACTIONS BETWEEN USERS.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Indemnification</h2>
              <p>
                Users agree to indemnify and hold harmless Oil & Gas Finder from any claims, 
                damages, or expenses arising from their use of the platform or violation of these terms.
              </p>
            </section>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              This disclaimer is part of our Terms of Service. By using our platform, you acknowledge 
              that you have read, understood, and agree to these terms.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default { TermsOfService, PrivacyPolicy, Disclaimer };