import React, { useState, useEffect } from 'react';
import './App.css';
import { LeadCaptureForm } from './components/Analytics';
import { DisclaimerBanner, FooterDisclaimer, HeaderWarning } from './components/DisclaimerBanner';
import { TermsOfService, PrivacyPolicy, Disclaimer } from './components/LegalPages';
import EnhancedHomePage from './components/EnhancedHomePage';
import NewsBar, { NewsSidebar } from './components/NewsBar';
import AIAnalysisPage from './components/AIAnalysisPage';
import PayPalButton from './PayPalButton';
import RevenueOptimizationDemo from './components/RevenueOptimizationDemo';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [marketData, setMarketData] = useState({});
  const [listings, setListings] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState('');
  const [editingListing, setEditingListing] = useState(null);
  const [selectedListing, setSelectedListing] = useState(null);

  // URL routing
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/browse') setCurrentPage('browse');
    else if (path === '/premium') setCurrentPage('premium');
    else if (path === '/register') setCurrentPage('register');
    else if (path === '/login') setCurrentPage('login');
    else if (path === '/ai-analysis') setCurrentPage('ai-analysis');
    else setCurrentPage('home');
  }, []);

  // Update page and URL
  const navigateToPage = (page) => {
    setCurrentPage(page);
    window.history.pushState({}, '', `/${page === 'home' ? '' : page}`);
  };

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
    fetchStats();
    fetchMarketData();
    fetchListings();
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchMarketData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/market-data`);
      const data = await response.json();
      setMarketData(data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const fetchListings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/listings`);
      const data = await response.json();
      setListings(data.listings || []);
    } catch (error) {
      console.error('Error fetching listings:', error);
    }
  };

  const handleLogin = async (email, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('token', data.access_token);
        setCurrentPage('dashboard');
      } else {
        alert('Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    }
    setLoading(false);
  };

  const handleRegister = async (userData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('token', data.access_token);
        setCurrentPage('dashboard');
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    setCurrentPage('home');
  };

  // Components
  const Header = () => (
    <header className="bg-slate-900 text-white shadow-2xl border-b-2 border-orange-500">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🛢️</div>
              <h1 className="text-2xl font-bold cursor-pointer text-orange-300 hover:text-orange-200 transition-colors" onClick={() => setCurrentPage('home')}>
                Oil & Gas Finder
              </h1>
            </div>
            <nav className="hidden md:flex space-x-6">
              <button 
                onClick={() => navigateToPage('home')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'home' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Home
              </button>
              <button 
                onClick={() => navigateToPage('browse')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'browse' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Browse Traders
              </button>
              <button 
                onClick={() => navigateToPage('ai-analysis')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'ai-analysis' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Product Analysis
              </button>
              <button 
                onClick={() => navigateToPage('premium')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'premium' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Premium
              </button>
              <button 
                onClick={() => navigateToPage('demo')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'demo' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Revenue Demo
              </button>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-300">Welcome, {user.first_name}</span>
                <button 
                  onClick={() => setCurrentPage('dashboard')}
                  className="bg-orange-600 hover:bg-orange-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Dashboard
                </button>
                <button 
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setCurrentPage('login')}
                  className="hover:text-orange-300 font-semibold"
                >
                  Login
                </button>
                <button 
                  onClick={() => setCurrentPage('register')}
                  className="bg-orange-600 hover:bg-orange-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );

  const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e) => {
      e.preventDefault();
      handleLogin(email, password);
    };

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-4xl mb-4">🛢️</div>
            <h2 className="text-2xl font-bold text-gray-900">Login to Oil & Gas Finder</h2>
            <p className="text-gray-600 mt-2">Access global energy trading network</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-600 hover:bg-orange-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          <p className="text-center mt-4 text-gray-600">
            Don't have an account?{' '}
            <button 
              onClick={() => setCurrentPage('register')}
              className="text-orange-600 hover:text-orange-500 font-semibold"
            >
              Register here
            </button>
          </p>
        </div>
      </div>
    );
  };

  const RegisterPage = () => {
    const [formData, setFormData] = useState({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      company_name: '',
      phone: '',
      country: '',
      trading_role: 'both'
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      handleRegister(formData);
    };

    const handleChange = (e) => {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-4xl mb-4">🛢️</div>
            <h2 className="text-2xl font-bold text-gray-900">Join Oil & Gas Finder</h2>
            <p className="text-gray-600 mt-2">Connect with global energy markets</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
              <input
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <input
                type="text"
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-600 hover:bg-orange-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          <p className="text-center mt-4 text-gray-600">
            Already have an account?{' '}
            <button 
              onClick={() => setCurrentPage('login')}
              className="text-orange-600 hover:text-orange-500 font-semibold"
            >
              Login here
            </button>
          </p>
        </div>
      </div>
    );
  };

  const PremiumPage = () => {
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
      setSelectedTier(planId);
      setShowPaymentModal(true);
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

  const BrowsePage = () => (
    <div className="flex min-h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold text-center mb-12">Browse Oil & Gas Traders</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {listings.map((listing, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold">{listing.title}</h3>
                  {listing.is_featured && (
                    <span className="bg-orange-500 text-white px-2 py-1 rounded text-sm">Featured</span>
                  )}
                </div>
                <p className="text-gray-600 mb-2 font-semibold">{listing.product_type?.replace('_', ' ').toUpperCase()}</p>
                <p className="text-gray-600 mb-2">Quantity: {listing.quantity} {listing.unit}</p>
                <p className="text-gray-600 mb-2">Location: {listing.location}</p>
                <p className="text-gray-600 mb-4">Price: {listing.price_range}</p>
                <button 
                  onClick={() => {
                    setSelectedListing(listing);
                    setCurrentPage('trader-detail');
                  }}
                  className="bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-lg w-full font-semibold transition-colors"
                >
                  Connect with Trader
                </button>
              </div>
            ))}
          </div>
          
          {listings.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛢️</div>
              <p className="text-gray-600 mb-4">No listings found.</p>
              <button
                onClick={() => setCurrentPage('register')}
                className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold"
              >
                Create Account to Post
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right Sidebar for News */}
      <div className="w-80 bg-white shadow-lg p-6 overflow-y-auto">
        <NewsSidebar />
      </div>
    </div>
  );

  // Dashboard Page Component
  const DashboardPage = () => {
    const [activeTab, setActiveTab] = useState('listings');
    const [myListings, setMyListings] = useState([]);

    useEffect(() => {
      if (user && token) {
        fetchMyListings();
      }
    }, [user, token]);

    const fetchMyListings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/listings/my`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setMyListings(data.listings || []);
      } catch (error) {
        console.error('Error fetching my listings:', error);
      }
    };



    const handleDeleteListing = async (listingId) => {
      if (!window.confirm('Are you sure you want to delete this listing?')) {
        return;
      }
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/listings/${listingId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          alert('Listing deleted successfully!');
          fetchMyListings(); // Refresh the listings
        } else {
          alert('Failed to delete listing');
        }
      } catch (error) {
        console.error('Error deleting listing:', error);
        alert('Failed to delete listing');
      }
    };

    const handleEditListing = (listing) => {
      setEditingListing(listing);
      setCurrentPage('edit-listing');
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold mb-8">Trading Dashboard</h1>
            
            <div className="flex space-x-4 mb-8">
              <button
                onClick={() => setActiveTab('listings')}
                className={`px-4 py-2 rounded-lg font-semibold ${
                  activeTab === 'listings'
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                My Listings
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-4 py-2 rounded-lg font-semibold ${
                  activeTab === 'analytics'
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Analytics
              </button>
            </div>

            {activeTab === 'listings' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">My Trading Listings</h2>
                  <button
                    onClick={() => setCurrentPage('create-listing')}
                    className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold"
                  >
                    Create New Listing
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {myListings.map((listing, index) => (
                    <div key={index} className="bg-gray-50 p-6 rounded-lg">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-semibold text-lg">{listing.title}</h4>
                        <span className={`px-2 py-1 rounded text-sm font-semibold ${
                          listing.status === 'featured' 
                            ? 'bg-orange-500 text-white' 
                            : 'bg-green-500 text-white'
                        }`}>
                          {listing.status}
                        </span>
                      </div>
                      <p className="text-gray-600">{listing.product_type?.replace('_', ' ').toUpperCase()}</p>
                      <p className="text-gray-600">Quantity: {listing.quantity} {listing.unit}</p>
                      <p className="text-gray-600">Location: {listing.location}</p>
                      <p className="text-gray-600">Price: {listing.price_range}</p>
                      
                      {/* Action Buttons */}
                      <div className="flex space-x-2 mt-4">
                        <button
                          onClick={() => handleEditListing(listing)}
                          className="flex-1 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteListing(listing.listing_id)}
                          className="flex-1 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {myListings.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">📝</div>
                    <p className="text-gray-600 mb-4">You haven't created any listings yet.</p>
                    <button
                      onClick={() => setCurrentPage('create-listing')}
                      className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold"
                    >
                      Create Your First Listing
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && (
              <div>
                <h2 className="text-xl font-bold mb-6">Trading Analytics</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 p-6 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">{myListings.length}</div>
                    <div className="text-gray-600">Total Listings</div>
                  </div>
                  <div className="bg-green-50 p-6 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {myListings.filter(l => l.status === 'active').length}
                    </div>
                    <div className="text-gray-600">Active Listings</div>
                  </div>
                  <div className="bg-orange-50 p-6 rounded-lg text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {myListings.filter(l => l.status === 'featured').length}
                    </div>
                    <div className="text-gray-600">Featured Listings</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Create Listing Page Component
  const CreateListingPage = () => {
    const [formData, setFormData] = useState({
      title: '',
      listing_type: 'sell',
      product_type: 'crude_oil',
      quantity: '',
      unit: 'barrels',
      price_range: '',
      location: '',
      trading_hub: '',
      description: '',
      contact_person: user?.first_name + ' ' + user?.last_name || '',
      contact_email: user?.email || '',
      contact_phone: '',
      whatsapp_number: '',
      procedure_document: '',
      is_featured: false
    });
    
    const [uploadedFile, setUploadedFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleCreateListing = async (listingData) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/listings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(listingData)
        });

        if (response.ok) {
          alert('Listing created successfully!');
          setCurrentPage('dashboard');
        } else {
          const errorData = await response.json();
          alert('Failed to create listing: ' + (errorData.detail || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error creating listing:', error);
        alert('Failed to create listing');
      }
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      const listingData = {
        ...formData,
        quantity: parseFloat(formData.quantity)
      };
      handleCreateListing(listingData);
    };

    const handleChange = (e) => {
      const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
      setFormData({ ...formData, [e.target.name]: value });
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-8">Create Trading Listing</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Listing Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Product Type</label>
                  <select
                    name="product_type"
                    value={formData.product_type}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="crude_oil">Crude Oil</option>
                    <option value="gasoline">Gasoline</option>
                    <option value="diesel">Diesel</option>
                    <option value="jet_fuel">Jet Fuel</option>
                    <option value="natural_gas">Natural Gas</option>
                    <option value="lng">LNG</option>
                    <option value="lpg">LPG</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="barrels">Barrels</option>
                    <option value="tons">Tons</option>
                    <option value="gallons">Gallons</option>
                    <option value="liters">Liters</option>
                    <option value="cubic_meters">Cubic Meters</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
                  <input
                    type="text"
                    name="price_range"
                    value={formData.price_range}
                    onChange={handleChange}
                    placeholder="e.g., $80-85 per barrel"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="e.g., Texas, USA"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trading Hub</label>
                  <input
                    type="text"
                    name="trading_hub"
                    value={formData.trading_hub}
                    onChange={handleChange}
                    placeholder="e.g., Houston, TX"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Person</label>
                  <input
                    type="text"
                    name="contact_person"
                    value={formData.contact_person}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Phone</label>
                  <input
                    type="tel"
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  WhatsApp/Telegram Number
                  <span className="text-gray-500 text-xs ml-1">(Optional - for direct messaging)</span>
                </label>
                <input
                  type="tel"
                  name="whatsapp_number"
                  value={formData.whatsapp_number}
                  onChange={handleChange}
                  placeholder="+1-555-987-6543"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  WhatsApp/Telegram Number
                  <span className="text-gray-500 text-xs ml-1">(Optional - for direct messaging)</span>
                </label>
                <input
                  type="tel"
                  name="whatsapp_number"
                  value={formData.whatsapp_number}
                  onChange={handleChange}
                  placeholder="+1-555-987-6543"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleChange}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">
                  Make this a featured listing (+$10)
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setCurrentPage('dashboard')}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-3 px-6 rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-orange-600 hover:bg-orange-500 text-white py-3 px-6 rounded-lg font-semibold"
                >
                  Create Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Edit Listing Page Component
  const EditListingPage = () => {
    const [formData, setFormData] = useState({
      title: editingListing?.title || '',
      product_type: editingListing?.product_type || 'crude_oil',
      quantity: editingListing?.quantity || '',
      unit: editingListing?.unit || 'barrels',
      price_range: editingListing?.price_range || '',
      location: editingListing?.location || '',
      trading_hub: editingListing?.trading_hub || '',
      description: editingListing?.description || '',
      contact_person: editingListing?.contact_person || '',
      contact_email: editingListing?.contact_email || '',
      contact_phone: editingListing?.contact_phone || '',
      whatsapp_number: editingListing?.whatsapp_number || '',
      is_featured: editingListing?.is_featured || false
    });

    const handleUpdateListing = async (listingData) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/listings/${editingListing.listing_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(listingData)
        });

        if (response.ok) {
          alert('Listing updated successfully!');
          setCurrentPage('dashboard');
        } else {
          const errorData = await response.json();
          alert('Failed to update listing: ' + (errorData.detail || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error updating listing:', error);
        alert('Failed to update listing');
      }
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      const listingData = {
        ...formData,
        quantity: parseFloat(formData.quantity)
      };
      handleUpdateListing(listingData);
    };

    const handleChange = (e) => {
      const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
      setFormData({ ...formData, [e.target.name]: value });
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-8">Edit Trading Listing</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Listing Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Product Type</label>
                  <select
                    name="product_type"
                    value={formData.product_type}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="crude_oil">Crude Oil</option>
                    <option value="gasoline">Gasoline</option>
                    <option value="diesel">Diesel</option>
                    <option value="jet_fuel">Jet Fuel</option>
                    <option value="natural_gas">Natural Gas</option>
                    <option value="lng">LNG</option>
                    <option value="lpg">LPG</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="barrels">Barrels</option>
                    <option value="tons">Tons</option>
                    <option value="gallons">Gallons</option>
                    <option value="liters">Liters</option>
                    <option value="cubic_meters">Cubic Meters</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
                  <input
                    type="text"
                    name="price_range"
                    value={formData.price_range}
                    onChange={handleChange}
                    placeholder="e.g., $80-85 per barrel"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="e.g., Texas, USA"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trading Hub</label>
                  <input
                    type="text"
                    name="trading_hub"
                    value={formData.trading_hub}
                    onChange={handleChange}
                    placeholder="e.g., Houston, TX"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Person</label>
                  <input
                    type="text"
                    name="contact_person"
                    value={formData.contact_person}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Phone</label>
                  <input
                    type="tel"
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  WhatsApp/Telegram Number
                  <span className="text-gray-500 text-xs ml-1">(Optional - for direct messaging)</span>
                </label>
                <input
                  type="tel"
                  name="whatsapp_number"
                  value={formData.whatsapp_number}
                  onChange={handleChange}
                  placeholder="+1-555-987-6543"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleChange}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">
                  Make this a featured listing (+$10)
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setCurrentPage('dashboard')}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-3 px-6 rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-orange-600 hover:bg-orange-500 text-white py-3 px-6 rounded-lg font-semibold"
                >
                  Update Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Trader Detail Page Component
  const TraderDetailPage = () => {
    if (!selectedListing) {
      return (
        <div className="min-h-screen bg-gray-50 py-12">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-2xl font-bold mb-4">Listing not found</h2>
            <button
              onClick={() => setCurrentPage('browse')}
              className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg font-semibold"
            >
              Back to Browse
            </button>
          </div>
        </div>
      );
    }

    const handleContactTrader = () => {
      const subject = encodeURIComponent(`Interested in: ${selectedListing.title}`);
      const body = encodeURIComponent(
        `Hello ${selectedListing.contact_person},\n\n` +
        `I'm interested in your ${selectedListing.product_type.replace('_', ' ')} listing:\n\n` +
        `Title: ${selectedListing.title}\n` +
        `Quantity: ${selectedListing.quantity} ${selectedListing.unit}\n` +
        `Location: ${selectedListing.location}\n` +
        `Price: ${selectedListing.price_range}\n\n` +
        `Please contact me to discuss this opportunity.\n\n` +
        `Best regards`
      );
      
      const mailtoLink = `mailto:${selectedListing.contact_email}?subject=${subject}&body=${body}`;
      window.open(mailtoLink, '_blank');
    };

    const handleCallTrader = () => {
      if (selectedListing.contact_phone) {
        window.open(`tel:${selectedListing.contact_phone}`, '_self');
      }
    };

    const handleWhatsAppTrader = () => {
      // Use WhatsApp number if available, otherwise fall back to regular phone
      const phoneNumber = selectedListing.whatsapp_number || selectedListing.contact_phone;
      if (phoneNumber) {
        const message = encodeURIComponent(
          `Hello ${selectedListing.contact_person}, I'm interested in your ${selectedListing.product_type.replace('_', ' ')} listing: "${selectedListing.title}". ` +
          `Quantity: ${selectedListing.quantity} ${selectedListing.unit}, Location: ${selectedListing.location}, Price: ${selectedListing.price_range}. ` +
          `Please contact me to discuss this opportunity.`
        );
        
        // Remove any non-numeric characters from phone number for WhatsApp
        const cleanPhone = phoneNumber.replace(/[^0-9]/g, '');
        const whatsappUrl = `https://wa.me/${cleanPhone}?text=${message}`;
        window.open(whatsappUrl, '_blank');
      }
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            {/* Back Button */}
            <button
              onClick={() => setCurrentPage('browse')}
              className="mb-6 flex items-center text-orange-600 hover:text-orange-500 font-semibold"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
              Back to Browse
            </button>

            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white p-8">
                <div className="flex justify-between items-start">
                  <div>
                    <h1 className="text-3xl font-bold mb-2">{selectedListing.title}</h1>
                    <p className="text-orange-100 text-lg">{selectedListing.company_name}</p>
                  </div>
                  {selectedListing.is_featured && (
                    <span className="bg-yellow-500 text-yellow-900 px-3 py-1 rounded-full text-sm font-semibold">
                      Featured
                    </span>
                  )}
                </div>
              </div>

              {/* Content */}
              <div className="p-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Product Information */}
                  <div>
                    <h2 className="text-2xl font-bold mb-6 text-gray-900">Product Details</h2>
                    
                    <div className="space-y-4">
                      <div className="flex items-center">
                        <span className="w-24 text-gray-600 font-semibold">Product:</span>
                        <span className="text-lg text-gray-900">{selectedListing.product_type.replace('_', ' ').toUpperCase()}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <span className="w-24 text-gray-600 font-semibold">Quantity:</span>
                        <span className="text-lg text-gray-900">{selectedListing.quantity?.toLocaleString()} {selectedListing.unit}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <span className="w-24 text-gray-600 font-semibold">Price:</span>
                        <span className="text-lg text-green-600 font-bold">{selectedListing.price_range}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <span className="w-24 text-gray-600 font-semibold">Location:</span>
                        <span className="text-lg text-gray-900">{selectedListing.location}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <span className="w-24 text-gray-600 font-semibold">Hub:</span>
                        <span className="text-lg text-gray-900">{selectedListing.trading_hub}</span>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="mt-8">
                      <h3 className="text-xl font-bold mb-4 text-gray-900">Description</h3>
                      <p className="text-gray-700 leading-relaxed">{selectedListing.description}</p>
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div>
                    <h2 className="text-2xl font-bold mb-6 text-gray-900">Contact Information</h2>
                    
                    <div className="bg-gray-50 rounded-lg p-6 mb-6">
                      <div className="space-y-4">
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-gray-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          <span className="text-gray-900 font-semibold">{selectedListing.contact_person}</span>
                        </div>
                        
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-gray-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          <span className="text-gray-900">{selectedListing.contact_email}</span>
                        </div>
                        
                        {selectedListing.contact_phone && (
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <svg className="w-5 h-5 text-gray-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                              </svg>
                              <a 
                                href={`tel:${selectedListing.contact_phone}`}
                                className="text-gray-900 hover:text-orange-600 transition-colors font-semibold"
                              >
                                {selectedListing.contact_phone}
                              </a>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                📞 Call
                              </span>
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                💬 WhatsApp
                              </span>
                            </div>
                          </div>
                        )}
                        
                        {selectedListing.whatsapp_number && selectedListing.whatsapp_number !== selectedListing.contact_phone && (
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.787"/>
                              </svg>
                              <a 
                                href={`https://wa.me/${selectedListing.whatsapp_number.replace(/[^0-9]/g, '')}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-900 hover:text-green-600 transition-colors font-semibold"
                              >
                                {selectedListing.whatsapp_number}
                              </a>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                💬 WhatsApp/Telegram
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <button
                        onClick={handleContactTrader}
                        className="bg-orange-600 hover:bg-orange-500 text-white py-3 px-6 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
                      >
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        Send Email
                      </button>
                      
                      {selectedListing.contact_phone && (
                        <button
                          onClick={handleCallTrader}
                          className="bg-blue-600 hover:bg-blue-500 text-white py-3 px-6 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
                        >
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                          </svg>
                          Call Now
                        </button>
                      )}
                      
                      {(selectedListing.contact_phone || selectedListing.whatsapp_number) && (
                        <button
                          onClick={handleWhatsAppTrader}
                          className="bg-green-500 hover:bg-green-400 text-white py-3 px-6 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
                        >
                          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.787"/>
                          </svg>
                          WhatsApp
                        </button>
                      )}
                      
                      <button
                        onClick={() => setCurrentPage('browse')}
                        className={`bg-gray-600 hover:bg-gray-500 text-white py-2 px-6 rounded-lg font-semibold transition-colors ${
                          selectedListing.contact_phone ? 'md:col-span-1' : 'md:col-span-2'
                        }`}
                      >
                        Back to Browse
                      </button>
                    </div>

                    {/* Listing Info */}
                    <div className="mt-6 text-sm text-gray-500">
                      <p>Listed on: {new Date(selectedListing.created_at).toLocaleDateString()}</p>
                      <p>Status: <span className="capitalize font-semibold">{selectedListing.status}</span></p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'login':
        return <LoginPage />;
      case 'register':
        return <RegisterPage />;
      case 'dashboard':
        return <DashboardPage />;
      case 'create-listing':
        return <CreateListingPage />;
      case 'edit-listing':
        return <EditListingPage />;
      case 'premium':
        return <PremiumPage />;
      case 'browse':
        return <BrowsePage />;
      case 'trader-detail':
        return <TraderDetailPage />;
      case 'ai-analysis':
        return <AIAnalysisPage />;
      case 'demo':
        return <RevenueOptimizationDemo />;
      case 'terms':
        return <TermsOfService />;
      case 'privacy':
        return <PrivacyPolicy />;
      case 'disclaimer':
        return <Disclaimer />;
      default:
        return <EnhancedHomePage />;
    }
  };

  return (
    <div className="App">
      <DisclaimerBanner />
      <HeaderWarning />
      <NewsBar />
      <Header />
      {renderCurrentPage()}
      
      {/* Newsletter Signup Section */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              Get Weekly Energy Market Insights
            </h3>
            <p className="text-orange-100 mb-8 max-w-2xl mx-auto">
              Join 10,000+ energy professionals receiving exclusive market analysis, trading opportunities, and industry insights.
            </p>
            <LeadCaptureForm 
              formType="newsletter"
              title=""
              description=""
              buttonText="Subscribe to Market Insights"
              fields={['email']}
            />
          </div>
        </div>
      </div>
      
      <FooterDisclaimer />
    </div>
  );
}

export default App;