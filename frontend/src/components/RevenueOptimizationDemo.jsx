import React from 'react';
import { SubscriptionProvider, FeatureGate } from './SubscriptionManager';
import TradingAnalytics from './TradingAnalytics';

// Simple component to test revenue optimization features
const RevenueOptimizationDemo = () => {
  return (
    <SubscriptionProvider>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🚀 Oil & Gas Finder Revenue Optimization Features
            </h1>
            <p className="text-lg text-gray-600">
              Advanced analytics dashboard and subscription management system
            </p>
          </div>

          {/* Feature Gating Demo */}
          <div className="mb-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">💰 Feature Gating Demo</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Basic Features - Always Available */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-green-600 mb-2">✅ Basic Features</h3>
                <p className="text-sm text-gray-600 mb-3">Available to all users</p>
                <div className="space-y-2 text-sm">
                  <div>• Basic Search</div>
                  <div>• Basic Listings</div>
                  <div>• Basic Profile</div>
                  <div>• Contact Traders</div>
                </div>
              </div>

              {/* Premium Features - Gated */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-blue-600 mb-2">🎯 Premium Features</h3>
                <p className="text-sm text-gray-600 mb-3">Requires Premium subscription</p>
                <FeatureGate feature="MARKET_ANALYTICS">
                  <div className="space-y-2 text-sm">
                    <div>• Market Analytics</div>
                    <div>• Price Alerts</div>
                    <div>• Export Data</div>
                    <div>• Unlimited Listings</div>
                  </div>
                </FeatureGate>
              </div>

              {/* Enterprise Features - Gated */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-purple-600 mb-2">🏢 Enterprise Features</h3>
                <p className="text-sm text-gray-600 mb-3">Requires Enterprise subscription</p>
                <FeatureGate feature="ADVANCED_ANALYTICS">
                  <div className="space-y-2 text-sm">
                    <div>• Advanced Analytics</div>
                    <div>• API Access</div>
                    <div>• Custom Branding</div>
                    <div>• Priority Support</div>
                  </div>
                </FeatureGate>
              </div>
            </div>
          </div>

          {/* Analytics Dashboard Demo */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">📊 Real-time Analytics Dashboard</h2>
            <FeatureGate 
              feature="MARKET_ANALYTICS" 
              fallback={
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                  <div className="text-blue-600 text-6xl mb-4">📈</div>
                  <h3 className="text-xl font-semibold text-blue-800 mb-2">
                    Advanced Analytics Available with Premium
                  </h3>
                  <p className="text-blue-700 mb-4">
                    Unlock real-time market data, profit calculators, and risk analysis
                  </p>
                  <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
                    Upgrade to Premium - $19/month
                  </button>
                </div>
              }
            >
              <TradingAnalytics />
            </FeatureGate>
          </div>

          {/* Subscription Plans Display */}
          <div className="mb-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">💳 Subscription Plans</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Basic Plan */}
              <div className="border rounded-lg p-6 text-center">
                <h3 className="text-xl font-semibold mb-2">Basic</h3>
                <div className="text-3xl font-bold text-gray-900 mb-4">
                  FREE
                </div>
                <ul className="text-sm text-gray-600 space-y-2 mb-6">
                  <li>✅ Basic Search</li>
                  <li>✅ 5 Listings/month</li>
                  <li>✅ 10 Connections/month</li>
                  <li>✅ Basic Profile</li>
                </ul>
                <button className="w-full bg-gray-100 text-gray-700 py-2 rounded-md">
                  Current Plan
                </button>
              </div>

              {/* Premium Plan */}
              <div className="border-2 border-blue-500 rounded-lg p-6 text-center relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                    Most Popular
                  </span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Premium</h3>
                <div className="text-3xl font-bold text-blue-600 mb-4">
                  $19<span className="text-lg text-gray-500">/month</span>
                </div>
                <ul className="text-sm text-gray-600 space-y-2 mb-6">
                  <li>✅ Everything in Basic</li>
                  <li>✅ Unlimited Listings</li>
                  <li>✅ Market Analytics</li>
                  <li>✅ Price Alerts</li>
                  <li>✅ Export Data</li>
                </ul>
                <button className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">
                  Upgrade to Premium
                </button>
              </div>

              {/* Enterprise Plan */}
              <div className="border rounded-lg p-6 text-center">
                <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
                <div className="text-3xl font-bold text-purple-600 mb-4">
                  $45<span className="text-lg text-gray-500">/month</span>
                </div>
                <ul className="text-sm text-gray-600 space-y-2 mb-6">
                  <li>✅ Everything in Premium</li>
                  <li>✅ Advanced Analytics</li>
                  <li>✅ API Access</li>
                  <li>✅ Priority Support</li>
                  <li>✅ Custom Branding</li>
                </ul>
                <button className="w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700">
                  Upgrade to Enterprise
                </button>
              </div>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <div className="text-green-600 text-2xl mb-2">✅</div>
              <div className="font-semibold text-green-800">Backend API</div>
              <div className="text-green-600 text-sm">Operational</div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
              <div className="text-blue-600 text-2xl mb-2">📊</div>
              <div className="font-semibold text-blue-800">Analytics</div>
              <div className="text-blue-600 text-sm">Ready</div>
            </div>
            
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
              <div className="text-purple-600 text-2xl mb-2">💳</div>
              <div className="font-semibold text-purple-800">Subscriptions</div>
              <div className="text-purple-600 text-sm">Active</div>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <div className="text-yellow-600 text-2xl mb-2">🚀</div>
              <div className="font-semibold text-yellow-800">Revenue Features</div>
              <div className="text-yellow-600 text-sm">Implemented</div>
            </div>
          </div>
        </div>
      </div>
    </SubscriptionProvider>
  );
};

export default RevenueOptimizationDemo;