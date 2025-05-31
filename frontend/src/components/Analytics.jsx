import React, { useEffect } from 'react';

// Analytics and Conversion Tracking System
export class AnalyticsManager {
  constructor() {
    this.userId = null;
    this.sessionId = this.generateSessionId();
    this.pageViews = [];
    this.events = [];
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Initialize analytics with user data
  init(userId = null) {
    this.userId = userId;
    this.trackPageView(window.location.pathname);
    this.setupGoogleAnalytics();
    this.setupHotjar();
  }

  // Setup Google Analytics 4
  setupGoogleAnalytics() {
    // Add GA4 script
    const script1 = document.createElement('script');
    script1.async = true;
    script1.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
    document.head.appendChild(script1);

    const script2 = document.createElement('script');
    script2.innerHTML = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'GA_MEASUREMENT_ID', {
        page_title: document.title,
        page_location: window.location.href,
        custom_map: {
          custom_parameter_1: 'user_type',
          custom_parameter_2: 'subscription_tier'
        }
      });
    `;
    document.head.appendChild(script2);

    // Make gtag available globally
    window.gtag = window.gtag || function() {
      window.dataLayer.push(arguments);
    };
  }

  // Setup Hotjar for user behavior tracking
  setupHotjar() {
    const script = document.createElement('script');
    script.innerHTML = `
      (function(h,o,t,j,a,r){
        h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
        h._hjSettings={hjid:YOUR_HOTJAR_ID,hjsv:6};
        a=o.getElementsByTagName('head')[0];
        r=o.createElement('script');r.async=1;
        r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
        a.appendChild(r);
      })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
    `;
    document.head.appendChild(script);
  }

  // Track page views
  trackPageView(path, title = document.title) {
    const pageView = {
      path,
      title,
      timestamp: Date.now(),
      userId: this.userId,
      sessionId: this.sessionId,
      referrer: document.referrer,
      userAgent: navigator.userAgent
    };

    this.pageViews.push(pageView);
    this.sendToBackend('pageview', pageView);

    // Google Analytics
    if (window.gtag) {
      window.gtag('config', 'GA_MEASUREMENT_ID', {
        page_path: path,
        page_title: title
      });
    }
  }

  // Track custom events
  trackEvent(eventName, parameters = {}) {
    const event = {
      event: eventName,
      parameters: {
        ...parameters,
        timestamp: Date.now(),
        userId: this.userId,
        sessionId: this.sessionId,
        path: window.location.pathname
      }
    };

    this.events.push(event);
    this.sendToBackend('event', event);

    // Google Analytics
    if (window.gtag) {
      window.gtag('event', eventName, {
        event_category: parameters.category || 'engagement',
        event_label: parameters.label,
        value: parameters.value,
        custom_parameter_1: parameters.userType,
        custom_parameter_2: parameters.subscriptionTier
      });
    }

    // Hotjar
    if (window.hj) {
      window.hj('event', eventName);
    }
  }

  // Track lead generation events
  trackLead(leadType, leadData = {}) {
    this.trackEvent('lead_generated', {
      category: 'lead_generation',
      label: leadType,
      value: this.getLeadValue(leadType),
      leadType,
      ...leadData
    });
  }

  // Track conversion events
  trackConversion(conversionType, value = 0, currency = 'USD') {
    this.trackEvent('conversion', {
      category: 'conversions',
      label: conversionType,
      value,
      currency,
      conversionType
    });

    // Google Analytics Enhanced Ecommerce
    if (window.gtag) {
      window.gtag('event', 'purchase', {
        transaction_id: Date.now().toString(),
        value: value,
        currency: currency,
        items: [{
          item_id: conversionType,
          item_name: conversionType,
          category: 'subscription',
          quantity: 1,
          price: value
        }]
      });
    }
  }

  // Track user engagement
  trackEngagement(action, details = {}) {
    this.trackEvent('user_engagement', {
      category: 'engagement',
      label: action,
      ...details
    });
  }

  // Get lead value based on type
  getLeadValue(leadType) {
    const leadValues = {
      'newsletter_signup': 5,
      'demo_request': 25,
      'premium_inquiry': 50,
      'contact_form': 15,
      'phone_call': 100,
      'free_trial': 75
    };
    return leadValues[leadType] || 0;
  }

  // Send data to backend
  async sendToBackend(type, data) {
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
    } catch (error) {
      console.error('Analytics tracking error:', error);
    }
  }

  // A/B Testing Support
  getVariant(testName, variants = ['A', 'B']) {
    const stored = localStorage.getItem(`ab_test_${testName}`);
    if (stored) return stored;

    const variant = variants[Math.floor(Math.random() * variants.length)];
    localStorage.setItem(`ab_test_${testName}`, variant);
    
    this.trackEvent('ab_test_assignment', {
      testName,
      variant,
      category: 'experimentation'
    });

    return variant;
  }
}

// Global analytics instance
export const analytics = new AnalyticsManager();

// React Hook for Analytics
export const useAnalytics = () => {
  useEffect(() => {
    // Initialize analytics when component mounts
    const userId = localStorage.getItem('userId');
    analytics.init(userId);
  }, []);

  return {
    trackPageView: analytics.trackPageView.bind(analytics),
    trackEvent: analytics.trackEvent.bind(analytics),
    trackLead: analytics.trackLead.bind(analytics),
    trackConversion: analytics.trackConversion.bind(analytics),
    trackEngagement: analytics.trackEngagement.bind(analytics),
    getVariant: analytics.getVariant.bind(analytics)
  };
};

// HOC for automatic page view tracking
export const withAnalytics = (WrappedComponent) => {
  return function AnalyticsWrappedComponent(props) {
    const analytics = useAnalytics();

    useEffect(() => {
      analytics.trackPageView(window.location.pathname);
    }, []);

    return <WrappedComponent {...props} analytics={analytics} />;
  };
};

// Conversion Tracking Components
export const ConversionTracker = ({ children, conversionType, value }) => {
  const analytics = useAnalytics();

  const handleConversion = () => {
    analytics.trackConversion(conversionType, value);
  };

  return React.cloneElement(children, {
    onClick: (e) => {
      handleConversion();
      if (children.props.onClick) {
        children.props.onClick(e);
      }
    }
  });
};

// Lead Capture Form with Analytics
export const LeadCaptureForm = ({ 
  formType = 'newsletter', 
  onSubmit, 
  title = "Stay Updated", 
  description = "Get the latest market insights",
  buttonText = "Subscribe",
  fields = ['email']
}) => {
  const [formData, setFormData] = React.useState({});
  const [submitted, setSubmitted] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const analytics = useAnalytics();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Track lead generation
      analytics.trackLead(formType, formData);

      // Submit to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          formType,
          source: window.location.pathname,
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        setSubmitted(true);
        analytics.trackConversion('lead_capture', analytics.getLeadValue(formType));
        
        if (onSubmit) {
          onSubmit(formData);
        }
      }
    } catch (error) {
      console.error('Lead capture error:', error);
      analytics.trackEvent('form_error', {
        category: 'errors',
        label: formType,
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Track form interaction
    analytics.trackEngagement('form_field_interaction', {
      field,
      formType
    });
  };

  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="text-green-600 text-2xl mb-2">✓</div>
        <h3 className="text-lg font-semibold text-green-800 mb-2">Thank you!</h3>
        <p className="text-green-700">We'll be in touch with valuable insights.</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-md">
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6">{description}</p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {fields.includes('email') && (
          <input
            type="email"
            placeholder="Enter your email address"
            required
            onChange={(e) => handleInputChange('email', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
        
        {fields.includes('name') && (
          <input
            type="text"
            placeholder="Enter your full name"
            required
            onChange={(e) => handleInputChange('name', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
        
        {fields.includes('company') && (
          <input
            type="text"
            placeholder="Company name"
            onChange={(e) => handleInputChange('company', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
        
        {fields.includes('phone') && (
          <input
            type="tel"
            placeholder="Phone number"
            onChange={(e) => handleInputChange('phone', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Submitting...' : buttonText}
        </button>
      </form>
      
      <p className="text-xs text-gray-500 mt-4 text-center">
        No spam, unsubscribe anytime. Your data is protected.
      </p>
    </div>
  );
};

export default { AnalyticsManager, analytics, useAnalytics, withAnalytics, ConversionTracker, LeadCaptureForm };