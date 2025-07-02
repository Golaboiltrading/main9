import React from 'react';
// Assuming LeadCaptureForm is in components/Analytics as per App.js
// If it's used by PremiumPage, it needs to be imported.
// For now, I'll assume it's imported in App.js and passed if needed, or PremiumPage has its own.
// Let's include it here for completeness if it was part of the inline component.
import { LeadCaptureForm } from '../components/Analytics';

// This component might need 'user', 'setSelectedTier', 'setShowPaymentModal' from App.js as props.
const PremiumPage = ({ user, setSelectedTier, setShowPaymentModal }) => {
  const subscriptionPlans = [
    {
      id: 'premium_basic',
      name: 'Energy Trader',
      price: 10,
      features: [
        'Enhanced listing visibility',
        'Basic market analytics',
        'Priority customer support',
        'Up to 20 listings per month',
        'Email market alerts'
      ]
    },
    {
      id: 'premium_advanced',
      name: 'Energy Pro',
      price: 25,
      popular: true,
      features: [
        'Everything in Energy Trader',
        'Advanced market intelligence',
        'Unlimited featured listings',
        'Real-time price alerts',
        'Connection recommendations',
        'API access for data'
      ]
    },
    {
      id: 'enterprise',
      name: 'Energy Enterprise',
      price: 45,
      features: [
        'Everything in Energy Pro',
        'Dedicated account manager',
        'Custom market reports',
        'White-label solutions',
        'Priority technical support',
        'Custom integrations'
      ]
    }
  ];

  const handleSubscriptionSelect = (planId) => {
    if (setSelectedTier && setShowPaymentModal) {
      setSelectedTier(planId);
      setShowPaymentModal(true);
    } else {
      console.warn("setSelectedTier or setShowPaymentModal not provided to PremiumPage");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose Your Energy Trading Plan</h1>
          <p className="text-xl text-gray-600">Unlock advanced features and grow your energy trading business</p>
        </div>

        {/* Demo Request Form */}
        <div className="max-w-md mx-auto mb-12">
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-orange-800 mb-2">Want to See Premium Features?</h3>
            <p className="text-orange-600 mb-4">Schedule a personalized demo and see how premium features can grow your energy business.</p>
            <LeadCaptureForm
              formType="demo_request"
              title=""
              description=""
              buttonText="Request Demo"
              fields={['email', 'name', 'company']}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {subscriptionPlans.map((plan) => (
            <div key={plan.id} className={`relative bg-white rounded-lg shadow-lg p-8 ${plan.popular ? 'ring-2 ring-orange-500 scale-105' : ''}`}>
              {plan.popular && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-orange-500 text-white px-4 py-1 rounded-full text-sm font-semibold">Most Popular</span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="text-4xl font-bold text-orange-600 mb-2">${plan.price}</div>
                <div className="text-gray-600">per month</div>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscriptionSelect(plan.id)}
                className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                  plan.popular
                    ? 'bg-orange-600 hover:bg-orange-500 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                }`}
              >
                {user?.role === 'basic' ? 'Upgrade Now' : 'Switch Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PremiumPage;
