import React from 'react';
import { SEO } from './SEO';

// Terms of Service Page
export const TermsOfService = () => {
  return (
    <div className="bg-white">
      <SEO 
        title="Terms of Service | Oil & Gas Finder"
        description="Terms and conditions for using the Oil & Gas Finder trading platform"
        url="/terms"
      />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Terms of Service</h1>
        <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>
        
        <div className="prose prose-lg max-w-none">
          <h2>1. ACCEPTANCE OF TERMS</h2>
          <p>
            By accessing and using Oil & Gas Finder ("Platform"), you accept and agree to be bound by the terms 
            and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
          </p>
          
          <h2>2. PLATFORM PURPOSE AND LIMITATIONS</h2>
          <p>
            Oil & Gas Finder is a <strong>connecting platform only</strong>. We facilitate connections between buyers 
            and sellers in the oil and gas industry but do not:
          </p>
          <ul>
            <li>Participate in, facilitate, or guarantee any transactions</li>
            <li>Hold, transfer, or handle any funds or commodities</li>
            <li>Verify the authenticity, legality, or quality of listed products</li>
            <li>Guarantee the identity, credentials, or legitimacy of users</li>
            <li>Provide legal, financial, or trade advice</li>
          </ul>
          
          <h2>3. DISCLAIMER OF RESPONSIBILITY</h2>
          <div className="bg-red-50 border-l-4 border-red-500 p-4 my-6">
            <p className="font-semibold text-red-800">IMPORTANT DISCLAIMER:</p>
            <p className="text-red-700">
              Oil & Gas Finder accepts <strong>NO RESPONSIBILITY OR LIABILITY</strong> for:
            </p>
            <ul className="text-red-700 mt-2">
              <li>• Any transactions, contracts, or agreements made between users</li>
              <li>• Fraudulent activities, scams, or misrepresentations by users</li>
              <li>• Financial losses, damages, or disputes arising from user interactions</li>
              <li>• Sanctions violations, illegal trade, or regulatory compliance issues</li>
              <li>• Product quality, delivery, payment, or contract fulfillment</li>
              <li>• Identity theft, data breaches, or privacy violations by third parties</li>
            </ul>
          </div>
          
          <h2>4. SANCTIONS AND PROHIBITED PRODUCTS</h2>
          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 my-6">
            <p className="font-semibold text-yellow-800">SANCTIONS COMPLIANCE WARNING:</p>
            <p className="text-yellow-700">
              Users are <strong>strictly prohibited</strong> from listing, trading, or facilitating transactions involving:
            </p>
            <ul className="text-yellow-700 mt-2">
              <li>• Products from sanctioned countries, entities, or individuals</li>
              <li>• Oil, gas, or petroleum products subject to international sanctions</li>
              <li>• Any commodities restricted by US, EU, UN, or other applicable sanctions</li>
              <li>• Products that violate export controls or trade restrictions</li>
            </ul>
            <p className="text-yellow-700 mt-2">
              <strong>Users are solely responsible</strong> for ensuring compliance with all applicable 
              sanctions, export controls, and trade regulations. Oil & Gas Finder provides no guidance 
              or assistance with sanctions compliance.
            </p>
          </div>
          
          <h2>5. ANTI-FRAUD AND SCAM PREVENTION</h2>
          <div className="bg-orange-50 border-l-4 border-orange-500 p-4 my-6">
            <p className="font-semibold text-orange-800">FRAUD WARNING:</p>
            <p className="text-orange-700">
              The oil and gas industry is frequently targeted by scammers. Common fraud schemes include:
            </p>
            <ul className="text-orange-700 mt-2">
              <li>• Fake product offers or non-existent refineries</li>
              <li>• Advance fee frauds and upfront payment requests</li>
              <li>• Document fraud and fake certificates of origin</li>
              <li>• Identity theft and impersonation of legitimate companies</li>
              <li>• Money laundering and financial crimes</li>
            </ul>
            <p className="text-orange-700 mt-2 font-semibold">
              Oil & Gas Finder cannot and does not verify user identities, product authenticity, 
              or transaction legitimacy. Users engage at their own risk.
            </p>
          </div>
          
          <h2>6. USER RESPONSIBILITIES</h2>
          <p>Users are solely responsible for:</p>
          <ul>
            <li>Verifying the identity and legitimacy of potential trading partners</li>
            <li>Conducting proper due diligence on all transactions</li>
            <li>Ensuring compliance with all applicable laws and regulations</li>
            <li>Protecting their own financial and personal information</li>
            <li>Reporting suspicious activities to appropriate authorities</li>
            <li>Obtaining proper legal and financial advice before transactions</li>
          </ul>
          
          <h2>7. PROHIBITED ACTIVITIES</h2>
          <p>Users may not use the platform to:</p>
          <ul>
            <li>Engage in fraudulent, deceptive, or illegal activities</li>
            <li>List non-existent, stolen, or sanctioned products</li>
            <li>Impersonate other individuals or companies</li>
            <li>Violate any applicable laws, regulations, or sanctions</li>
            <li>Engage in money laundering or terrorist financing</li>
            <li>Manipulate market prices or engage in market manipulation</li>
            <li>Spam, harass, or abuse other users</li>
          </ul>
          
          <h2>8. ACCOUNT TERMINATION</h2>
          <p>
            We reserve the right to suspend or terminate user accounts at any time, without notice, 
            for any violation of these terms or for any reason we deem necessary to protect the platform 
            and its users.
          </p>
          
          <h2>9. LIMITATION OF LIABILITY</h2>
          <p>
            IN NO EVENT SHALL OIL & GAS FINDER, ITS OFFICERS, DIRECTORS, EMPLOYEES, OR AGENTS BE LIABLE 
            FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING 
            WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.
          </p>
          
          <h2>10. INDEMNIFICATION</h2>
          <p>
            Users agree to indemnify and hold harmless Oil & Gas Finder from any claims, damages, 
            obligations, losses, liabilities, costs, and expenses arising from their use of the platform 
            or violation of these terms.
          </p>
          
          <h2>11. GOVERNING LAW</h2>
          <p>
            These terms shall be governed by and construed in accordance with the laws of the United States, 
            without regard to its conflict of law provisions.
          </p>
          
          <h2>12. CHANGES TO TERMS</h2>
          <p>
            Oil & Gas Finder reserves the right to modify these terms at any time. Users will be notified 
            of significant changes, and continued use of the platform constitutes acceptance of modified terms.
          </p>
          
          <div className="bg-gray-100 p-6 rounded-lg mt-8">
            <h3 className="font-bold text-gray-900 mb-2">Contact Information</h3>
            <p className="text-gray-700">
              For questions about these Terms of Service, please contact us at:
              <br />Email: legal@oilgasfinder.com
              <br />Address: [Your Legal Address]
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Privacy Policy Page
export const PrivacyPolicy = () => {
  return (
    <div className="bg-white">
      <SEO 
        title="Privacy Policy | Oil & Gas Finder"
        description="Privacy policy and data protection information for Oil & Gas Finder"
        url="/privacy"
      />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
        <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>
        
        <div className="prose prose-lg max-w-none">
          <h2>1. INFORMATION WE COLLECT</h2>
          <p>We collect information you provide directly to us, such as:</p>
          <ul>
            <li>Account registration information (name, email, company details)</li>
            <li>Profile information and trading preferences</li>
            <li>Communications with other users (for safety and fraud prevention)</li>
            <li>Payment information (processed by third-party providers)</li>
            <li>Usage data and analytics</li>
          </ul>
          
          <h2>2. HOW WE USE YOUR INFORMATION</h2>
          <p>We use collected information to:</p>
          <ul>
            <li>Provide and maintain our platform services</li>
            <li>Facilitate connections between buyers and sellers</li>
            <li>Detect and prevent fraud and abuse</li>
            <li>Comply with legal obligations and sanctions screening</li>
            <li>Improve our services and user experience</li>
            <li>Send important updates and notifications</li>
          </ul>
          
          <h2>3. INFORMATION SHARING</h2>
          <p>We may share your information:</p>
          <ul>
            <li>With other users as part of platform functionality</li>
            <li>With law enforcement when required by law</li>
            <li>With service providers who assist in platform operations</li>
            <li>In connection with business transfers or acquisitions</li>
          </ul>
          
          <h2>4. DATA SECURITY</h2>
          <p>
            We implement appropriate security measures to protect your information. 
            However, no method of transmission over the internet is 100% secure.
          </p>
          
          <h2>5. YOUR RIGHTS</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Access and update your personal information</li>
            <li>Request deletion of your account and data</li>
            <li>Opt out of non-essential communications</li>
            <li>Request data portability where applicable</li>
          </ul>
          
          <h2>6. COOKIES AND TRACKING</h2>
          <p>
            We use cookies and similar technologies to improve user experience, 
            analyze usage, and prevent fraud. You can control cookie settings 
            through your browser.
          </p>
          
          <h2>7. INTERNATIONAL TRANSFERS</h2>
          <p>
            Your information may be transferred to and processed in countries 
            other than your country of residence. We ensure appropriate 
            safeguards are in place for such transfers.
          </p>
          
          <h2>8. CHILDREN'S PRIVACY</h2>
          <p>
            Our platform is not intended for individuals under 18 years of age. 
            We do not knowingly collect personal information from children.
          </p>
          
          <h2>9. CHANGES TO PRIVACY POLICY</h2>
          <p>
            We may update this privacy policy from time to time. We will notify 
            users of significant changes through the platform or email.
          </p>
          
          <div className="bg-gray-100 p-6 rounded-lg mt-8">
            <h3 className="font-bold text-gray-900 mb-2">Contact Information</h3>
            <p className="text-gray-700">
              For privacy-related questions, please contact us at:
              <br />Email: privacy@oilgasfinder.com
              <br />Address: [Your Privacy Officer Address]
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Disclaimer Page
export const Disclaimer = () => {
  return (
    <div className="bg-white">
      <SEO 
        title="Legal Disclaimer | Oil & Gas Finder"
        description="Legal disclaimers and liability limitations for Oil & Gas Finder platform"
        url="/disclaimer"
      />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Legal Disclaimer</h1>
        
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-red-800 mb-4">⚠️ IMPORTANT LEGAL NOTICE ⚠️</h2>
          <p className="text-red-700 font-semibold">
            READ THIS DISCLAIMER CAREFULLY BEFORE USING THE PLATFORM. 
            BY USING OIL & GAS FINDER, YOU ACKNOWLEDGE AND AGREE TO ALL TERMS BELOW.
          </p>
        </div>
        
        <div className="prose prose-lg max-w-none">
          <h2>1. PLATFORM NATURE AND LIMITATIONS</h2>
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
            <p className="font-semibold text-yellow-800">Oil & Gas Finder is:</p>
            <ul className="text-yellow-700">
              <li>• A CONNECTION PLATFORM ONLY - not a trading company</li>
              <li>• NOT a broker, dealer, or trading intermediary</li>
              <li>• NOT responsible for any transactions between users</li>
              <li>• NOT a financial or legal advisory service</li>
            </ul>
          </div>
          
          <h2>2. NO RESPONSIBILITY FOR TRANSACTIONS</h2>
          <p className="font-semibold text-red-600">
            OIL & GAS FINDER EXPLICITLY DISCLAIMS ALL RESPONSIBILITY FOR:
          </p>
          <ul className="text-red-600">
            <li>• Any contracts, agreements, or transactions between users</li>
            <li>• Financial losses, damages, or disputes arising from user interactions</li>
            <li>• Fraud, scams, misrepresentations, or illegal activities by users</li>
            <li>• Product quality, authenticity, delivery, or payment issues</li>
            <li>• Identity verification or credential validation of users</li>
            <li>• Sanctions compliance or regulatory adherence by users</li>
          </ul>
          
          <h2>3. SANCTIONS AND COMPLIANCE WARNING</h2>
          <div className="bg-red-100 border border-red-300 p-4 rounded">
            <p className="font-bold text-red-800">CRITICAL SANCTIONS NOTICE:</p>
            <p className="text-red-700">
              The oil and gas industry is subject to complex international sanctions. 
              Users must ensure full compliance with:
            </p>
            <ul className="text-red-700">
              <li>• US sanctions (OFAC, Department of Commerce)</li>
              <li>• EU sanctions and restrictive measures</li>
              <li>• UN Security Council sanctions</li>
              <li>• National sanctions of relevant jurisdictions</li>
            </ul>
            <p className="text-red-700 font-semibold mt-2">
              OIL & GAS FINDER PROVIDES NO SANCTIONS GUIDANCE AND ACCEPTS NO LIABILITY 
              FOR SANCTIONS VIOLATIONS BY USERS.
            </p>
          </div>
          
          <h2>4. FRAUD AND SCAM WARNINGS</h2>
          <div className="bg-orange-100 border border-orange-300 p-4 rounded">
            <p className="font-bold text-orange-800">HIGH-RISK INDUSTRY NOTICE:</p>
            <p className="text-orange-700">
              The oil and gas trading sector experiences frequent fraudulent activities:
            </p>
            <ul className="text-orange-700">
              <li>• Fake refineries and non-existent products</li>
              <li>• Advance fee frauds and upfront payment scams</li>
              <li>• Document forgery and certificate fraud</li>
              <li>• Corporate identity theft and impersonation</li>
              <li>• Money laundering and financial crimes</li>
            </ul>
            <p className="text-orange-700 font-semibold mt-2">
              USERS MUST CONDUCT THOROUGH DUE DILIGENCE AND VERIFICATION 
              BEFORE ENGAGING IN ANY TRANSACTIONS.
            </p>
          </div>
          
          <h2>5. NO WARRANTIES OR GUARANTEES</h2>
          <p>
            The platform is provided "AS IS" without warranties of any kind. We disclaim:
          </p>
          <ul>
            <li>• Accuracy or completeness of user-provided information</li>
            <li>• Availability, reliability, or security of the platform</li>
            <li>• Fitness for any particular purpose</li>
            <li>• Non-infringement of third-party rights</li>
          </ul>
          
          <h2>6. LIMITATION OF LIABILITY</h2>
          <div className="bg-gray-100 border border-gray-300 p-4 rounded">
            <p className="font-bold text-gray-800">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, OIL & GAS FINDER SHALL NOT BE LIABLE FOR:
            </p>
            <ul className="text-gray-700">
              <li>• Any direct, indirect, incidental, or consequential damages</li>
              <li>• Loss of profits, revenue, data, or business opportunities</li>
              <li>• Personal injury or property damage</li>
              <li>• Criminal activities or regulatory violations by users</li>
              <li>• Third-party claims or legal proceedings</li>
            </ul>
          </div>
          
          <h2>7. USER ACKNOWLEDGMENT</h2>
          <p>By using the platform, users acknowledge they:</p>
          <ul>
            <li>• Have read and understood this disclaimer</li>
            <li>• Assume all risks associated with platform use</li>
            <li>• Will conduct proper due diligence before any transactions</li>
            <li>• Will comply with all applicable laws and regulations</li>
            <li>• Will not hold Oil & Gas Finder liable for any losses or damages</li>
          </ul>
          
          <h2>8. PROFESSIONAL ADVICE RECOMMENDATION</h2>
          <div className="bg-blue-50 border border-blue-200 p-4 rounded">
            <p className="font-semibold text-blue-800">STRONGLY RECOMMENDED:</p>
            <p className="text-blue-700">
              Before engaging in oil and gas transactions, consult with:
            </p>
            <ul className="text-blue-700">
              <li>• Legal counsel specializing in energy law</li>
              <li>• Financial advisors familiar with commodity trading</li>
              <li>• Sanctions compliance specialists</li>
              <li>• Industry experts and verification services</li>
            </ul>
          </div>
          
          <h2>9. GOVERNING LAW AND JURISDICTION</h2>
          <p>
            This disclaimer is governed by the laws of [Your Jurisdiction]. 
            Any disputes shall be resolved in the courts of [Your Jurisdiction].
          </p>
          
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mt-8">
            <h3 className="font-bold text-red-800 mb-2">FINAL WARNING</h3>
            <p className="text-red-700 font-semibold">
              If you do not agree with any part of this disclaimer or are not comfortable 
              with the risks involved, DO NOT USE the Oil & Gas Finder platform.
            </p>
          </div>
          
          <div className="bg-gray-100 p-6 rounded-lg mt-8">
            <h3 className="font-bold text-gray-900 mb-2">Legal Contact Information</h3>
            <p className="text-gray-700">
              For legal matters, please contact:
              <br />Email: legal@oilgasfinder.com
              <br />Address: [Your Legal Department Address]
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export { TermsOfService, PrivacyPolicy, Disclaimer };