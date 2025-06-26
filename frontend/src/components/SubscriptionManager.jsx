import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Subscription plans configuration
const SUBSCRIPTION_PLANS = {
  basic: {
    id: 'basic',
    name: 'Basic',
    price: 0,
    billing: 'free',
    features: {
      BASIC_SEARCH: true,
      BASIC_LISTINGS: true,
      BASIC_PROFILE: true,
      CONTACT_TRADERS: true,
    },
    limits: {
      listings_per_month: 5,
      connections_per_month: 10,
      search_results: 20,
    },
    description: 'Perfect for getting started in oil & gas trading',
  },
  premium: {
    id: 'premium',
    name: 'Premium',
    price: 19,
    billing: 'monthly',
    features: {
      BASIC_SEARCH: true,
      BASIC_LISTINGS: true,
      BASIC_PROFILE: true,
      CONTACT_TRADERS: true,
      ADVANCED_SEARCH: true,
      UNLIMITED_LISTINGS: true,
      MARKET_ANALYTICS: true,
      PRICE_ALERTS: true,
      EXPORT_DATA: true,
    },
    limits: {
      listings_per_month: -1, // unlimited
      connections_per_month: 100,
      search_results: 100,
    },
    description: 'Enhanced features for active traders',
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 45,
    billing: 'monthly',
    features: {
      BASIC_SEARCH: true,
      BASIC_LISTINGS: true,
      BASIC_PROFILE: true,
      CONTACT_TRADERS: true,
      ADVANCED_SEARCH: true,
      UNLIMITED_LISTINGS: true,
      MARKET_ANALYTICS: true,
      PRICE_ALERTS: true,
      EXPORT_DATA: true,
      ADVANCED_ANALYTICS: true,
      API_ACCESS: true,
      PRIORITY_SUPPORT: true,
      CUSTOM_BRANDING: true,
      BULK_OPERATIONS: true,
      ADVANCED_REPORTING: true,
    },
    limits: {
      listings_per_month: -1,
      connections_per_month: -1,
      search_results: -1,
    },
    description: 'Complete solution for enterprise trading operations',
  },
};

// Subscription Context
const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

// Subscription Provider
export const SubscriptionProvider = ({ children }) => {
  const [userSubscription, setUserSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch user subscription data
  useEffect(() => {
    const fetchSubscription = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          setUserSubscription({ plan: 'basic', status: 'active' });
          setLoading(false);
          return;
        }

        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/current`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const subscription = await response.json();
          setUserSubscription(subscription);
        } else {
          // Default to basic plan if subscription fetch fails
          setUserSubscription({ plan: 'basic', status: 'active' });
        }
      } catch (err) {
        console.error('Error fetching subscription:', err);
        setError(err.message);
        setUserSubscription({ plan: 'basic', status: 'active' });
      } finally {
        setLoading(false);
      }
    };

    fetchSubscription();
  }, []);

  const upgradeSubscription = useCallback(async (planId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/upgrade`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      });

      if (response.ok) {
        const updatedSubscription = await response.json();
        setUserSubscription(updatedSubscription);
        return { success: true, subscription: updatedSubscription };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upgrade subscription');
      }
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  const cancelSubscription = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const updatedSubscription = await response.json();
        setUserSubscription(updatedSubscription);
        return { success: true };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to cancel subscription');
      }
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  const checkFeatureAccess = useCallback((feature) => {
    if (!userSubscription) return false;
    
    const plan = SUBSCRIPTION_PLANS[userSubscription.plan];
    return plan?.features[feature] === true;
  }, [userSubscription]);

  const checkUsageLimit = useCallback((limitType, currentUsage = 0) => {
    if (!userSubscription) return { hasAccess: false, limit: 0, remaining: 0 };
    
    const plan = SUBSCRIPTION_PLANS[userSubscription.plan];
    const limit = plan?.limits[limitType];
    
    if (limit === -1) {
      return { hasAccess: true, limit: -1, remaining: -1 }; // unlimited
    }
    
    const remaining = Math.max(0, limit - currentUsage);
    return {
      hasAccess: remaining > 0,
      limit,
      remaining,
      currentUsage
    };
  }, [userSubscription]);

  const value = {
    userSubscription,
    loading,
    error,
    checkFeatureAccess,
    checkUsageLimit,
    upgradeSubscription,
    cancelSubscription,
    plans: SUBSCRIPTION_PLANS,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};

// Feature Gate Component
export const FeatureGate = ({ feature, children, fallback, upgradePrompt = true }) => {
  const { checkFeatureAccess, userSubscription, plans } = useSubscription();
  const hasAccess = checkFeatureAccess(feature);

  if (hasAccess) {
    return children;
  }

  if (fallback) {
    return fallback;
  }

  if (!upgradePrompt) {
    return null;
  }

  return <UpgradePrompt feature={feature} currentPlan={userSubscription?.plan} plans={plans} />;
};

// Usage Limit Gate Component
export const UsageLimitGate = ({ 
  limitType, 
  currentUsage, 
  children, 
  fallback, 
  showUsage = true 
}) => {
  const { checkUsageLimit } = useSubscription();
  const usage = checkUsageLimit(limitType, currentUsage);

  if (usage.hasAccess) {
    return (
      <div>
        {showUsage && usage.limit !== -1 && (
          <div className="mb-2 text-sm text-gray-600">
            {limitType.replace('_', ' ')}: {usage.currentUsage}/{usage.limit} used
          </div>
        )}
        {children}
      </div>
    );
  }

  if (fallback) {
    return fallback;
  }

  return <UsageLimitReached limitType={limitType} usage={usage} />;
};

// Upgrade Prompt Component
const UpgradePrompt = ({ feature, currentPlan = 'basic' }) => {
  const { plans, upgradeSubscription } = useSubscription();
  const [upgrading, setUpgrading] = useState(false);

  // Find the minimum plan that supports this feature
  const recommendedPlan = Object.values(plans).find(plan => 
    plan.features[feature] && plan.id !== currentPlan
  );

  const handleUpgrade = async (planId) => {
    setUpgrading(true);
    const result = await upgradeSubscription(planId);
    if (result.success) {
      // Reload page to reflect new subscription
      window.location.reload();
    } else {
      alert(`Upgrade failed: ${result.error}`);
    }
    setUpgrading(false);
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-lg p-6 text-center">
      <div className="mb-4">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 rounded-full mb-3">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Premium Feature</h3>
        <p className="text-gray-600 mb-4">
          This feature requires a {recommendedPlan?.name} subscription or higher.
        </p>
      </div>

      {recommendedPlan && (
        <div className="bg-white rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium text-gray-900">{recommendedPlan.name} Plan</span>
            <span className="text-2xl font-bold text-blue-600">
              ${recommendedPlan.price}
              <span className="text-sm text-gray-500">/{recommendedPlan.billing}</span>
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-3">{recommendedPlan.description}</p>
          
          <button
            onClick={() => handleUpgrade(recommendedPlan.id)}
            disabled={upgrading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {upgrading ? 'Upgrading...' : `Upgrade to ${recommendedPlan.name}`}
          </button>
        </div>
      )}

      <p className="text-xs text-gray-500">
        Cancel anytime • 30-day money-back guarantee
      </p>
    </div>
  );
};

// Usage Limit Reached Component
const UsageLimitReached = ({ limitType, usage }) => {
  const { plans, upgradeSubscription } = useSubscription();
  const [upgrading, setUpgrading] = useState(false);

  // Find a plan with higher limits
  const upgradeOptions = Object.values(plans).filter(plan => 
    plan.limits[limitType] > usage.limit || plan.limits[limitType] === -1
  );

  const handleUpgrade = async (planId) => {
    setUpgrading(true);
    const result = await upgradeSubscription(planId);
    if (result.success) {
      window.location.reload();
    } else {
      alert(`Upgrade failed: ${result.error}`);
    }
    setUpgrading(false);
  };

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
      <div className="mb-3">
        <svg className="w-8 h-8 text-yellow-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <h3 className="text-lg font-medium text-yellow-800">Usage Limit Reached</h3>
        <p className="text-yellow-700 text-sm mt-1">
          You've reached your {limitType.replace('_', ' ')} limit of {usage.limit} for this month.
        </p>
      </div>

      {upgradeOptions.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-yellow-700 mb-3">Upgrade for higher limits:</p>
          {upgradeOptions.slice(0, 2).map((plan) => (
            <button
              key={plan.id}
              onClick={() => handleUpgrade(plan.id)}
              disabled={upgrading}
              className="w-full bg-yellow-600 text-white py-2 px-3 rounded-md hover:bg-yellow-700 disabled:opacity-50 text-sm transition-colors"
            >
              {upgrading ? 'Upgrading...' : `Upgrade to ${plan.name} - $${plan.price}/${plan.billing}`}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Subscription Plans Display Component
export const SubscriptionPlans = ({ onSelectPlan, currentPlan = 'basic' }) => {
  const [selectedPlan, setSelectedPlan] = useState(currentPlan);
  const [loading, setLoading] = useState(false);

  const handleSelectPlan = async (planId) => {
    if (planId === currentPlan) return;
    
    setLoading(true);
    setSelectedPlan(planId);
    
    if (onSelectPlan) {
      await onSelectPlan(planId);
    }
    
    setLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Choose Your Plan</h2>
        <p className="text-lg text-gray-600">
          Unlock powerful features to accelerate your oil & gas trading business
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.values(SUBSCRIPTION_PLANS).map((plan) => (
          <div
            key={plan.id}
            className={`relative bg-white rounded-lg shadow-md border-2 transition-all ${
              selectedPlan === plan.id
                ? 'border-blue-500 transform scale-105'
                : 'border-gray-200 hover:border-gray-300'
            } ${plan.id === 'premium' ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}
          >
            {plan.id === 'premium' && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            )}

            <div className="p-6">
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{plan.name}</h3>
                <div className="mb-3">
                  <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
                  {plan.price > 0 && (
                    <span className="text-gray-600">/{plan.billing}</span>
                  )}
                </div>
                <p className="text-gray-600 text-sm">{plan.description}</p>
              </div>

              <div className="space-y-3 mb-6">
                <h4 className="font-medium text-gray-900">Features:</h4>
                <ul className="space-y-2 text-sm">
                  {Object.entries(plan.features).map(([feature, enabled]) => (
                    enabled && (
                      <li key={feature} className="flex items-center text-gray-600">
                        <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        {feature.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                      </li>
                    )
                  ))}
                </ul>
              </div>

              <button
                onClick={() => handleSelectPlan(plan.id)}
                disabled={loading || plan.id === currentPlan}
                className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                  plan.id === currentPlan
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : selectedPlan === plan.id
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-600'
                }`}
              >
                {loading && selectedPlan === plan.id
                  ? 'Processing...'
                  : plan.id === currentPlan
                  ? 'Current Plan'
                  : `Select ${plan.name}`
                }
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionProvider;