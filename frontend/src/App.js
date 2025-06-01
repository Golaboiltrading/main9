import React, { useState, useEffect } from 'react';
import './App.css';
import { DisclaimerBanner, FooterDisclaimer, HeaderWarning } from './components/DisclaimerBanner';
import { TermsOfService, PrivacyPolicy, Disclaimer } from './components/LegalPages';
import { BlogSystem, BlogPost } from './components/BlogSystem';
import { LocationLandingPage, ProductLandingPage } from './components/LandingPages';
import { LeadCaptureForm, useAnalytics } from './components/Analytics';
import EnhancedHomePage from './components/EnhancedHomePage';
import NewsBar from './components/NewsBar';
import AIAnalysisPage from './components/AIAnalysisPage';
import PayPalButton from './PayPalButton';
import BusinessGrowthDashboard from './BusinessGrowthDashboard';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [marketData, setMarketData] = useState({});
  const [listings, setListings] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentType, setPaymentType] = useState(''); // 'subscription' or 'featured'
  const [selectedTier, setSelectedTier] = useState('');

  // Analytics hook
  const analytics = useAnalytics();

  // URL routing
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/terms') setCurrentPage('terms');
    else if (path === '/privacy') setCurrentPage('privacy');
    else if (path === '/disclaimer') setCurrentPage('disclaimer');
    else if (path === '/blog') setCurrentPage('blog');
    else if (path.startsWith('/blog/')) setCurrentPage('blog-post');
    else if (path.startsWith('/locations/')) setCurrentPage('location');
    else if (path.startsWith('/products/')) setCurrentPage('product');
    else if (path === '/browse') setCurrentPage('browse');
    else if (path === '/premium') setCurrentPage('premium');
    else if (path === '/register') setCurrentPage('register');
    else if (path === '/login') setCurrentPage('login');
    else setCurrentPage('home');
  }, []);

  // Update page and URL
  const navigateToPage = (page) => {
    setCurrentPage(page);
    window.history.pushState({}, '', `/${page === 'home' ? '' : page}`);
    analytics.trackPageView(`/${page === 'home' ? '' : page}`);
  };

  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchUserAnalytics();
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

  const fetchUserAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/user`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUserAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching user analytics:', error);
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
        fetchListings();
        setCurrentPage('dashboard');
      } else {
        alert('Failed to create listing');
      }
    } catch (error) {
      console.error('Error creating listing:', error);
      alert('Failed to create listing');
    }
  };

  const searchCompanies = async (query) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/search/companies?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data.companies || []);
    } catch (error) {
      console.error('Error searching companies:', error);
    }
  };

  // Components
  const Header = () => (
    <header className="bg-blue-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold cursor-pointer" onClick={() => setCurrentPage('home')}>
              🛢️ Oil & Gas Finder
            </h1>
            <nav className="hidden md:flex space-x-6">
              <button 
                onClick={() => navigateToPage('home')}
                className={`hover:text-blue-200 ${currentPage === 'home' ? 'text-blue-200' : ''}`}
              >
                Home
              </button>
              <button 
                onClick={() => navigateToPage('browse')}
                className={`hover:text-blue-200 ${currentPage === 'browse' ? 'text-blue-200' : ''}`}
              >
                Browse Traders
              </button>
              <button 
                onClick={() => navigateToPage('market')}
                className={`hover:text-blue-200 ${currentPage === 'market' ? 'text-blue-200' : ''}`}
              >
                Market Data
              </button>
              <button 
                onClick={() => navigateToPage('blog')}
                className={`hover:text-blue-200 ${currentPage === 'blog' ? 'text-blue-200' : ''}`}
              >
                Blog
              </button>
              {user && user.role === 'enterprise' && (
                <button 
                  onClick={() => navigateToPage('business-growth')}
                  className={`hover:text-blue-200 ${currentPage === 'business-growth' ? 'text-blue-200' : ''}`}
                >
                  Business Growth
                </button>
              )}
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm">Welcome, {user.first_name}</span>
                <button 
                  onClick={() => setCurrentPage('dashboard')}
                  className="bg-blue-700 hover:bg-blue-600 px-4 py-2 rounded-lg"
                >
                  Dashboard
                </button>
                <button 
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setCurrentPage('login')}
                  className="hover:text-blue-200"
                >
                  Login
                </button>
                <button 
                  onClick={() => setCurrentPage('register')}
                  className="bg-blue-700 hover:bg-blue-600 px-4 py-2 rounded-lg"
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

  const HomePage = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-900 to-blue-700 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Global Oil & Gas Trading Platform
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Connect with verified oil and gas traders worldwide. Find crude oil, natural gas, LNG, and refined products from trusted trading partners.
          </p>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={() => setCurrentPage('register')}
              className="bg-orange-500 hover:bg-orange-400 text-white px-8 py-3 rounded-lg text-lg font-semibold"
            >
              Start Trading
            </button>
            <button 
              onClick={() => setCurrentPage('browse')}
              className="bg-transparent border-2 border-white hover:bg-white hover:text-blue-900 px-8 py-3 rounded-lg text-lg font-semibold"
            >
              Browse Traders
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 text-center">
            <div className="bg-blue-50 p-6 rounded-lg">
              <div className="text-3xl font-bold text-blue-900">{stats.oil_gas_traders || 0}</div>
              <div className="text-gray-600 mt-2">Oil & Gas Traders</div>
            </div>
            <div className="bg-green-50 p-6 rounded-lg">
              <div className="text-3xl font-bold text-green-900">{stats.active_oil_listings || 0}</div>
              <div className="text-gray-600 mt-2">Active Oil Listings</div>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg">
              <div className="text-3xl font-bold text-purple-900">{stats.successful_connections || 0}</div>
              <div className="text-gray-600 mt-2">Successful Connections</div>
            </div>
            <div className="bg-orange-50 p-6 rounded-lg">
              <div className="text-3xl font-bold text-orange-900">{stats.premium_finders || 0}</div>
              <div className="text-gray-600 mt-2">Premium Finders</div>
            </div>
            <div className="bg-red-50 p-6 rounded-lg">
              <div className="text-3xl font-bold text-red-900">{stats.featured_opportunities || 0}</div>
              <div className="text-gray-600 mt-2">Featured Opportunities</div>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Trading Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-blue-900">Crude Oil</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• WTI Crude</li>
                <li>• Brent Crude</li>
                <li>• Dubai Crude</li>
                <li>• Regional Grades</li>
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-green-900">Refined Products</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• Gasoline</li>
                <li>• Diesel</li>
                <li>• Jet Fuel</li>
                <li>• Heating Oil</li>
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-purple-900">Natural Gas</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• Pipeline Gas</li>
                <li>• LNG</li>
                <li>• LPG</li>
                <li>• Gas Condensate</li>
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-orange-900">Trading Hubs</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• Houston, TX</li>
                <li>• Dubai, UAE</li>
                <li>• Singapore</li>
                <li>• London, UK</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Recent Listings */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Recent Trading Opportunities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {listings.slice(0, 6).map((listing, index) => (
              <div key={index} className="bg-gray-50 p-6 rounded-lg shadow">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold">{listing.title}</h3>
                  {listing.is_featured && (
                    <span className="bg-orange-500 text-white px-2 py-1 rounded text-sm">Featured</span>
                  )}
                </div>
                <p className="text-gray-600 mb-2">{listing.product_type.replace('_', ' ').toUpperCase()}</p>
                <p className="text-gray-600 mb-2">Quantity: {listing.quantity} {listing.unit}</p>
                <p className="text-gray-600 mb-2">Location: {listing.location}</p>
                <p className="text-gray-600 mb-4">Price: {listing.price_range}</p>
                <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg w-full">
                  View Details
                </button>
              </div>
            ))}
          </div>
          {listings.length === 0 && (
            <p className="text-center text-gray-600">No listings available yet. Be the first to post!</p>
          )}
        </div>
      </section>
    </div>
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
          <h2 className="text-2xl font-bold text-center mb-8">Login to Oil & Gas Finder</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          <p className="text-center mt-4 text-gray-600">
            Don't have an account?{' '}
            <button 
              onClick={() => setCurrentPage('register')}
              className="text-blue-600 hover:text-blue-500 font-semibold"
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
          <h2 className="text-2xl font-bold text-center mb-8">Join Oil & Gas Finder</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <input
                type="text"
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trading Role</label>
              <select
                name="trading_role"
                value={formData.trading_role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="buyer">Buyer</option>
                <option value="seller">Seller</option>
                <option value="both">Both</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          <p className="text-center mt-4 text-gray-600">
            Already have an account?{' '}
            <button 
              onClick={() => setCurrentPage('login')}
              className="text-blue-600 hover:text-blue-500 font-semibold"
            >
              Login here
            </button>
          </p>
        </div>
      </div>
    );
  };

  const DashboardPage = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [myListings, setMyListings] = useState([]);

    useEffect(() => {
      if (user) {
        fetchMyListings();
      }
    }, [user]);

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

    if (!user) return null;

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-8">Welcome back, {user.first_name}!</h1>
          
          <div className="bg-white rounded-lg shadow-lg">
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`py-4 px-2 border-b-2 font-medium text-sm ${
                    activeTab === 'overview' 
                      ? 'border-blue-500 text-blue-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('listings')}
                  className={`py-4 px-2 border-b-2 font-medium text-sm ${
                    activeTab === 'listings' 
                      ? 'border-blue-500 text-blue-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  My Listings
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`py-4 px-2 border-b-2 font-medium text-sm ${
                    activeTab === 'analytics' 
                      ? 'border-blue-500 text-blue-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Analytics
                </button>
                <button
                  onClick={() => setCurrentPage('create-listing')}
                  className="py-4 px-2 border-b-2 border-transparent text-gray-500 hover:text-gray-700 font-medium text-sm"
                >
                  Create Listing
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'overview' && (
                <div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-blue-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-blue-900">My Listings</h3>
                      <p className="text-3xl font-bold text-blue-600">{myListings.length}</p>
                    </div>
                    <div className="bg-green-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-green-900">Account Type</h3>
                      <p className="text-lg font-bold text-green-600 capitalize">{user.role}</p>
                    </div>
                    <div className="bg-purple-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-purple-900">Trading Role</h3>
                      <p className="text-lg font-bold text-purple-600 capitalize">{user.trading_role}</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">Account Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div><strong>Company:</strong> {user.company_name}</div>
                      <div><strong>Email:</strong> {user.email}</div>
                      <div><strong>Country:</strong> {user.country}</div>
                      <div><strong>Phone:</strong> {user.phone || 'Not provided'}</div>
                    </div>
                    
                    {user.role === 'basic' && (
                      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h4 className="text-lg font-semibold text-blue-900 mb-2">Upgrade to Premium</h4>
                        <p className="text-blue-700 mb-4">Unlock advanced features and grow your trading business</p>
                        <button
                          onClick={() => setCurrentPage('premium')}
                          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg"
                        >
                          View Premium Plans
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'listings' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-semibold">My Trading Listings</h3>
                    <button
                      onClick={() => setCurrentPage('create-listing')}
                      className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg"
                    >
                      Create New Listing
                    </button>
                  </div>

                  {myListings.length > 0 ? (
                    <div className="space-y-4">
                      {myListings.map((listing, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold text-lg">{listing.title}</h4>
                              <p className="text-gray-600">{listing.product_type.replace('_', ' ').toUpperCase()}</p>
                              <p className="text-gray-600">Quantity: {listing.quantity} {listing.unit}</p>
                              <p className="text-gray-600">Location: {listing.location}</p>
                              <p className="text-gray-600">Price: {listing.price_range}</p>
                            </div>
                            <div className="text-right">
                              <span className={`px-2 py-1 rounded text-sm ${
                                listing.status === 'featured' 
                                  ? 'bg-orange-100 text-orange-800' 
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {listing.status}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-600 mb-4">You haven't created any listings yet.</p>
                      <button
                        onClick={() => setCurrentPage('create-listing')}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg"
                      >
                        Create Your First Listing
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analytics' && (
                <div>
                  <h3 className="text-lg font-semibold mb-6">Your Trading Analytics</h3>
                  
                  {userAnalytics.listings && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                      <div className="bg-blue-50 p-6 rounded-lg">
                        <h4 className="text-lg font-semibold text-blue-900">Listing Performance</h4>
                        <div className="mt-4 space-y-2">
                          <div className="flex justify-between">
                            <span>Total Listings:</span>
                            <span className="font-bold">{userAnalytics.listings.total_listings}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Active:</span>
                            <span className="font-bold text-green-600">{userAnalytics.listings.active_listings}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Featured:</span>
                            <span className="font-bold text-orange-600">{userAnalytics.listings.featured_listings}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-green-50 p-6 rounded-lg">
                        <h4 className="text-lg font-semibold text-green-900">Connection Metrics</h4>
                        <div className="mt-4 space-y-2">
                          <div className="flex justify-between">
                            <span>Received:</span>
                            <span className="font-bold">{userAnalytics.connections?.connections_received || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Made:</span>
                            <span className="font-bold">{userAnalytics.connections?.connections_made || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Success Rate:</span>
                            <span className="font-bold text-green-600">{userAnalytics.connections?.connection_success_rate || 0}%</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-purple-50 p-6 rounded-lg">
                        <h4 className="text-lg font-semibold text-purple-900">Financial Summary</h4>
                        <div className="mt-4 space-y-2">
                          <div className="flex justify-between">
                            <span>Total Spent:</span>
                            <span className="font-bold">${userAnalytics.financial?.total_spent || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Subscription:</span>
                            <span className="font-bold capitalize">{userAnalytics.financial?.subscription_status || 'Basic'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Payments:</span>
                            <span className="font-bold">{userAnalytics.financial?.payment_history?.length || 0}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {userAnalytics.listings?.product_breakdown && (
                    <div className="bg-white p-6 rounded-lg border">
                      <h4 className="text-lg font-semibold mb-4">Product Distribution</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(userAnalytics.listings.product_breakdown).map(([product, count]) => (
                          <div key={product} className="text-center p-3 bg-gray-50 rounded">
                            <div className="text-2xl font-bold text-blue-600">{count}</div>
                            <div className="text-sm text-gray-600 capitalize">{product.replace('_', ' ')}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const PremiumPage = () => {
    const subscriptionPlans = [
      {
        id: 'premium_basic',
        name: 'Premium Basic',
        price: 10,
        features: [
          'Enhanced listing visibility',
          'Basic analytics dashboard',
          'Priority customer support',
          'Remove platform branding',
          'Up to 20 listings per month'
        ]
      },
      {
        id: 'premium_advanced',
        name: 'Premium Advanced',
        price: 25,
        popular: true,
        features: [
          'Everything in Premium Basic',
          'Advanced analytics & reporting',
          'Unlimited featured listings',
          'Market intelligence reports',
          'Connection recommendations',
          'Bulk listing management'
        ]
      },
      {
        id: 'enterprise',
        name: 'Enterprise',
        price: 45,
        features: [
          'Everything in Premium Advanced',
          'API access for integration',
          'Custom branding options',
          'Dedicated account manager',
          'Advanced market insights',
          'White-label solutions'
        ]
      }
    ];

    const handleSubscriptionSelect = (planId) => {
      setSelectedTier(planId);
      setPaymentType('subscription');
      setShowPaymentModal(true);
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Choose Your Premium Plan</h1>
            <p className="text-xl text-gray-600">Unlock advanced features and grow your oil & gas trading business</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {subscriptionPlans.map((plan) => (
              <div key={plan.id} className={`relative bg-white rounded-lg shadow-lg p-8 ${plan.popular ? 'ring-2 ring-blue-500' : ''}`}>
                {plan.popular && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">Most Popular</span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold text-blue-600 mb-2">${plan.price}</div>
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
                  className={`w-full py-3 px-6 rounded-lg font-semibold ${
                    plan.popular 
                      ? 'bg-blue-600 hover:bg-blue-500 text-white' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  {user?.role === 'basic' ? 'Upgrade Now' : 'Switch Plan'}
                </button>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">All plans include a 30-day money-back guarantee</p>
            <button
              onClick={() => setCurrentPage('dashboard')}
              className="text-blue-600 hover:text-blue-500 font-semibold"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Payment Modal Component
  const PaymentModal = () => {
    const [paymentStep, setPaymentStep] = useState('confirm'); // 'confirm', 'processing', 'success'

    const handlePaymentSuccess = (details) => {
      console.log('Payment successful:', details);
      setPaymentStep('success');
      // Refresh user data and close modal after delay
      setTimeout(() => {
        setShowPaymentModal(false);
        setPaymentStep('confirm');
        fetchUserProfile();
        fetchUserAnalytics();
      }, 3000);
    };

    const handlePaymentError = (error) => {
      console.error('Payment error:', error);
      alert('Payment failed. Please try again.');
      setPaymentStep('confirm');
    };

    const getPaymentAmount = () => {
      if (paymentType === 'subscription') {
        const prices = { premium_basic: 10, premium_advanced: 25, enterprise: 45 };
        return prices[selectedTier] || 0;
      }
      return paymentType === 'featured_premium' ? 10 : 5;
    };

    const getPaymentDescription = () => {
      if (paymentType === 'subscription') {
        return `${selectedTier.replace('_', ' ').toUpperCase()} Monthly Subscription`;
      }
      return paymentType === 'featured_premium' ? 'Premium Featured Listing' : 'Standard Featured Listing';
    };

    if (!showPaymentModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold">Complete Payment</h3>
            <button
              onClick={() => setShowPaymentModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          {paymentStep === 'confirm' && (
            <div>
              <div className="mb-6">
                <h4 className="font-semibold mb-2">Payment Details</h4>
                <p className="text-gray-600">{getPaymentDescription()}</p>
                <p className="text-2xl font-bold text-blue-600">${getPaymentAmount()}</p>
              </div>

              <div className="mb-6">
                <PayPalButton
                  amount={getPaymentAmount()}
                  description={getPaymentDescription()}
                  onSuccess={handlePaymentSuccess}
                  onError={handlePaymentError}
                  onCancel={() => setShowPaymentModal(false)}
                />
              </div>

              <button
                onClick={() => setShowPaymentModal(false)}
                className="w-full bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 rounded-lg"
              >
                Cancel
              </button>
            </div>
          )}

          {paymentStep === 'success' && (
            <div className="text-center">
              <div className="text-green-500 text-6xl mb-4">✓</div>
              <h4 className="text-xl font-bold mb-2">Payment Successful!</h4>
              <p className="text-gray-600">Your account has been upgraded. You will be redirected shortly.</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Create Listing Page Component
  const CreateListingPage = () => {
    const [formData, setFormData] = useState({
      title: '',
      product_type: 'crude_oil',
      quantity: '',
      unit: 'barrels',
      price_range: '',
      location: '',
      trading_hub: '',
      description: '',
      contact_person: user?.first_name + ' ' + user?.last_name || '',
      contact_email: user?.email || '',
      contact_phone: user?.phone || '',
      is_featured: false
    });

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
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="crude_oil">Crude Oil</option>
                    <option value="gasoline">Gasoline</option>
                    <option value="diesel">Diesel</option>
                    <option value="jet_fuel">Jet Fuel</option>
                    <option value="natural_gas">Natural Gas</option>
                    <option value="lng">LNG</option>
                    <option value="lpg">LPG</option>
                    <option value="gas_condensate">Gas Condensate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="barrels">Barrels</option>
                    <option value="metric_tons">Metric Tons</option>
                    <option value="gallons">Gallons</option>
                    <option value="cubic_meters">Cubic Meters</option>
                    <option value="mmbtu">MMBTU</option>
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    placeholder="e.g., $75-80/barrel"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trading Hub</label>
                  <select
                    name="trading_hub"
                    value={formData.trading_hub}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select Trading Hub</option>
                    <option value="Houston, TX">Houston, TX</option>
                    <option value="Dubai, UAE">Dubai, UAE</option>
                    <option value="Singapore">Singapore</option>
                    <option value="London, UK">London, UK</option>
                    <option value="Rotterdam, Netherlands">Rotterdam, Netherlands</option>
                    <option value="Cushing, OK">Cushing, OK</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                ></textarea>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Person</label>
                  <input
                    type="text"
                    name="contact_person"
                    value={formData.contact_person}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                  <input
                    type="email"
                    name="contact_email"
                    value={formData.contact_email}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Make this a featured listing (+$10)
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-semibold"
                >
                  Create Listing
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentPage('dashboard')}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-2 rounded-lg font-semibold"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  const BrowsePage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredListings, setFilteredListings] = useState(listings);

    useEffect(() => {
      setFilteredListings(listings);
    }, [listings]);

    const handleSearch = () => {
      if (searchQuery.trim()) {
        searchCompanies(searchQuery);
      } else {
        setFilteredListings(listings);
      }
    };

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-8">Browse Oil & Gas Traders</h1>
          
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search companies, products, or locations..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSearch}
                className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg"
              >
                Search
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredListings.map((listing, index) => (
              <div key={index} className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold">{listing.title}</h3>
                  {listing.is_featured && (
                    <span className="bg-orange-500 text-white px-2 py-1 rounded text-sm">Featured</span>
                  )}
                </div>
                <div className="space-y-2 text-gray-600">
                  <p><strong>Product:</strong> {listing.product_type.replace('_', ' ').toUpperCase()}</p>
                  <p><strong>Quantity:</strong> {listing.quantity} {listing.unit}</p>
                  <p><strong>Location:</strong> {listing.location}</p>
                  <p><strong>Trading Hub:</strong> {listing.trading_hub}</p>
                  <p><strong>Price:</strong> {listing.price_range}</p>
                  <p><strong>Company:</strong> {listing.company_name}</p>
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-500 mb-3">{listing.description}</p>
                  <button className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg">
                    Contact Trader
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredListings.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-600 text-lg">No listings found matching your search.</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const MarketDataPage = () => (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Market Data</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-6">Oil Prices</h2>
            {marketData.oil_prices && Object.entries(marketData.oil_prices).map(([key, data]) => (
              <div key={key} className="flex justify-between items-center py-3 border-b last:border-b-0">
                <span className="font-medium capitalize">{key.replace('_', ' ')}</span>
                <div className="text-right">
                  <div className="font-bold">${data.price}</div>
                  <div className={`text-sm ${data.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {data.change}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-6">Gas Prices</h2>
            {marketData.gas_prices && Object.entries(marketData.gas_prices).map(([key, data]) => (
              <div key={key} className="flex justify-between items-center py-3 border-b last:border-b-0">
                <span className="font-medium capitalize">{key.replace('_', ' ')}</span>
                <div className="text-right">
                  <div className="font-bold">${data.price}</div>
                  <div className={`text-sm ${data.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {data.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
          <h2 className="text-xl font-bold mb-6">Trading Hubs</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {marketData.trading_hubs && marketData.trading_hubs.map((hub, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg text-center">
                <span className="font-medium">{hub}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Render current page
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'login':
        return <LoginPage />;
      case 'register':
        return <RegisterPage />;
      case 'dashboard':
        return user ? <DashboardPage /> : <LoginPage />;
      case 'create-listing':
        return user ? <CreateListingPage /> : <LoginPage />;
      case 'browse':
        return <BrowsePage />;
      case 'market':
        return <MarketDataPage />;
      case 'premium':
        return user ? <PremiumPage /> : <LoginPage />;
      case 'business-growth':
        return user && user.role === 'enterprise' ? 
          <BusinessGrowthDashboard token={token} API_BASE_URL={API_BASE_URL} /> : 
          <LoginPage />;
      case 'terms':
        return <TermsOfService />;
      case 'privacy':
        return <PrivacyPolicy />;
      case 'disclaimer':
        return <Disclaimer />;
      case 'blog':
        return <BlogSystem />;
      case 'blog-post':
        const slug = window.location.pathname.split('/blog/')[1];
        return <BlogPost slug={slug} />;
      case 'location':
        const location = window.location.pathname.split('/locations/')[1];
        return <LocationLandingPage location={location} />;
      case 'product':
        const product = window.location.pathname.split('/products/')[1];
        return <ProductLandingPage productType={product} />;
      case 'ai-analysis':
        return <AIAnalysisPage />;
      default:
        return <EnhancedHomePage user={user} navigateToPage={navigateToPage} />;
    }
  };

  return (
    <div className="App">
      {/* Legal Disclaimer Banner (shows on first visit) */}
      <DisclaimerBanner />
      
      {/* Header Warning (persistent) */}
      <HeaderWarning />
      
      <Header />
      {renderCurrentPage()}
      
      {/* Footer Disclaimer (persistent) */}
      <FooterDisclaimer />
      
      <PaymentModal />
    </div>
  );
}

export default App;