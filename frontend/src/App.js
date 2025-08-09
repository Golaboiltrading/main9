import React, { useState, useEffect } from 'react';
import './App.css';
import { LeadCaptureForm } from './components/Analytics';
import { DisclaimerBanner, FooterDisclaimer, HeaderWarning } from './components/DisclaimerBanner';
import { TermsOfService, PrivacyPolicy, Disclaimer } from './components/LegalPages';
import EnhancedHomePage from './components/EnhancedHomePage';
import NewsBar, { NewsSidebar } from './components/NewsBar';
import AIAnalysisPage from './components/AIAnalysisPage';
import PayPalButton from './PayPalButton';


const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || window.location.origin;

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
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
    const urlParams = new URLSearchParams(window.location.search);
    
    if (path === '/browse') setCurrentPage('browse');
    else if (path === '/premium') setCurrentPage('premium');
    else if (path === '/register') setCurrentPage('register');
    else if (path === '/login') setCurrentPage('login');
    else if (path === '/ai-analysis') setCurrentPage('ai-analysis');
    else if (path === '/reset-password' || urlParams.get('token')) setCurrentPage('reset-password');
    else setCurrentPage('home');
  }, []);

  // Update page and URL
  const navigateToPage = (page) => {
    setCurrentPage(page);
    window.history.pushState({}, '', `/${page === 'home' ? '' : page}`);
  };

  // Initialize app
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken) {
      setToken(savedToken);
      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (e) {
          console.error('Error parsing saved user data:', e);
        }
      }
      fetchUserProfile();
    }
    fetchStats();
    fetchMarketData();
    fetchListings();
  }, []);

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
        localStorage.setItem('user', JSON.stringify(data.user)); // Store user data
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
        localStorage.setItem('user', JSON.stringify(data.user)); // Store user data
        setCurrentPage('dashboard');
      } else {
        let errorMessage = 'Registration failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || `Server error: ${response.status}`;
        } catch (e) {
          errorMessage = `Server error: ${response.status} - ${response.statusText}`;
        }
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Network error: Unable to connect to server. Please check your internet connection and try again.');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user'); // Clear user data
    setCurrentPage('home');
  };

  // Components
  const Header = () => (
    <header className="bg-slate-900 text-white shadow-2xl border-b-2 border-orange-500">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-slate-900 to-slate-800 px-4 py-2 rounded-lg flex items-center space-x-3 border-2 border-orange-500 shadow-lg">
                <div className="text-orange-500 text-2xl font-bold">⛽</div>
                <h1 className="text-xl font-bold cursor-pointer text-white hover:text-orange-300 transition-colors" onClick={() => setCurrentPage('home')}>
                  Oil & Gas Finder
                </h1>
              </div>
            </div>
            <nav className="hidden md:flex space-x-6">
              <a 
                href="https://t.me/OilandGasFinder"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:opacity-80 transition-opacity flex items-center"
              >
                <img 
                  src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg"
                  alt="Telegram"
                  className="w-8 h-8"
                />
              </a>
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
                onClick={() => navigateToPage('find-connections')}
                className={`hover:text-orange-300 font-semibold ${currentPage === 'find-connections' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Find Connections
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
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-300">Welcome, {user.first_name}</span>
                {user.role === 'admin' || user.role === 'super_admin' ? (
                  <button 
                    onClick={() => setCurrentPage('admin')}
                    className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                  >
                    Admin Panel
                  </button>
                ) : null}
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
            <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-4 border border-orange-400">
              <div className="text-orange-400 text-xl">🏭</div>
              <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
            </div>
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
          
          <div className="text-center mt-4">
            <button 
              onClick={() => setCurrentPage('forgot-password')}
              className="text-orange-600 hover:text-orange-500 font-semibold text-sm"
            >
              Forgot your password?
            </button>
          </div>
          
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

  const ForgotPasswordPage = () => {
    const [email, setEmail] = useState('');
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [localLoading, setLocalLoading] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setLocalLoading(true);
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        
        if (response.ok) {
          setLocalLoading(false);
          setIsSubmitted(true);
          return; // Exit early to prevent further execution
        } else {
          const errorData = await response.json();
          alert(errorData.detail || 'Failed to send reset email');
        }
      } catch (error) {
        console.error('Forgot password error:', error);
        alert('Network error. Please try again.');
      }
      setLocalLoading(false);
    };

    if (isSubmitted) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-6 border border-orange-400">
                <div className="text-orange-400 text-xl">🏭</div>
                <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
              </div>
              <div className="text-green-600 text-5xl mb-4">✓</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Check Your Email</h2>
              <p className="text-gray-600 mb-6">
                We've sent a password reset link to <strong>{email}</strong>
              </p>
              <p className="text-sm text-gray-500 mb-6">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <button
                onClick={() => setCurrentPage('login')}
                className="w-full bg-gray-600 hover:bg-gray-500 text-white py-2 rounded-lg font-semibold"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-4 border border-orange-400">
              <div className="text-orange-400 text-xl">🏭</div>
              <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Reset Your Password</h2>
            <p className="text-gray-600 mt-2">Enter your email address and we'll send you a link to reset your password</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Enter your email address"
                required
              />
            </div>
            <button
              type="submit"
              disabled={localLoading}
              className="w-full bg-orange-600 hover:bg-orange-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {localLoading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
          <p className="text-center mt-6 text-gray-600">
            Remember your password?{' '}
            <button 
              onClick={() => setCurrentPage('login')}
              className="text-orange-600 hover:text-orange-500 font-semibold"
            >
              Back to Login
            </button>
          </p>
        </div>
      </div>
    );
  };

  const ResetPasswordPage = () => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');
      
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      
      if (password.length < 6) {
        setError('Password must be at least 6 characters');
        return;
      }
      
      setLoading(true);
      
      try {
        // Get token from URL params
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (!token) {
          setError('Invalid reset link');
          setLoading(false);
          return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token, new_password: password })
        });
        
        if (response.ok) {
          setIsSubmitted(true);
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Failed to reset password');
        }
      } catch (error) {
        console.error('Reset password error:', error);
        setError('Network error. Please try again.');
      }
      setLoading(false);
    };

    if (isSubmitted) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-6 border border-orange-400">
                <div className="text-orange-400 text-xl">🏭</div>
                <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
              </div>
              <div className="text-green-600 text-5xl mb-4">✓</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Password Reset Successful</h2>
              <p className="text-gray-600 mb-6">
                Your password has been successfully reset. You can now login with your new password.
              </p>
              <button
                onClick={() => setCurrentPage('login')}
                className="w-full bg-orange-600 hover:bg-orange-500 text-white py-2 rounded-lg font-semibold"
              >
                Go to Login
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-4 border border-orange-400">
              <div className="text-orange-400 text-xl">🏭</div>
              <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Set New Password</h2>
            <p className="text-gray-600 mt-2">Enter your new password below</p>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Enter new password"
                required
                minLength="6"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Confirm new password"
                required
                minLength="6"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-600 hover:bg-orange-500 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
          <p className="text-center mt-6 text-gray-600">
            <button 
              onClick={() => setCurrentPage('login')}
              className="text-orange-600 hover:text-orange-500 font-semibold"
            >
              Back to Login
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
            <div className="bg-slate-800 px-4 py-3 rounded-lg inline-flex items-center space-x-2 mb-4 border border-orange-400">
              <div className="text-orange-400 text-xl">🏭</div>
              <span className="text-lg font-bold text-orange-400">Oil & Gas Finder</span>
            </div>
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
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="+1234567890"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Trading Role</label>
                <select
                  name="trading_role"
                  value={formData.trading_role}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                >
                  <option value="">Select Role</option>
                  <option value="buyer">Buyer</option>
                  <option value="seller">Seller</option>
                  <option value="both">Both</option>
                </select>
              </div>
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

          {/* Telegram Community */}
          <div className="max-w-md mx-auto mb-12">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Join Our Trading Community</h3>
              <p className="text-blue-600 mb-4">Connect with other oil & gas traders, get market updates, and share opportunities.</p>
              <a 
                href="https://t.me/OilandGasFinder"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-3 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                <img 
                  src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg"
                  alt="Telegram"
                  className="w-6 h-6"
                />
                <span>Join Community</span>
              </a>
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

  const BrowsePage = () => {
    const [filter, setFilter] = useState('all');
    const [productFilter, setProductFilter] = useState('all');
    
    // Read filters from localStorage on mount
    useEffect(() => {
      const savedListingTypeFilter = localStorage.getItem('listingTypeFilter');
      const savedProductFilter = localStorage.getItem('productFilter');
      
      if (savedListingTypeFilter) {
        setFilter(savedListingTypeFilter);
        // Clear the filter from localStorage after using it
        localStorage.removeItem('listingTypeFilter');
      }
      
      if (savedProductFilter) {
        setProductFilter(savedProductFilter);
        // Clear the filter from localStorage after using it
        localStorage.removeItem('productFilter');
      }
    }, []);
    
    // Filter listings based on current filters
    const filteredListings = listings.filter(listing => {
      // Filter by listing type (buy/sell)
      let typeMatch = true;
      if (filter === 'buyers') typeMatch = listing.listing_type === 'buy';
      if (filter === 'sellers') typeMatch = listing.listing_type === 'sell';
      
      // Filter by product type
      let productMatch = true;
      if (productFilter !== 'all') {
        productMatch = listing.product_type === productFilter;
      }
      
      return typeMatch && productMatch;
    });

    return (
      <div className="flex min-h-screen bg-gray-50">
        {/* Main Content */}
        <div className="flex-1 py-12">
          <div className="container mx-auto px-4">
            <h1 className="text-4xl font-bold text-center mb-8">Browse Oil & Gas Traders</h1>
            
            {/* Filter Buttons */}
            <div className="flex justify-center mb-8">
              <div className="bg-white rounded-lg shadow-md p-2 flex space-x-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                    filter === 'all'
                      ? 'bg-orange-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Traders ({listings.length})
                </button>
                <button
                  onClick={() => setFilter('sellers')}
                  className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                    filter === 'sellers'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  🔴 Sellers ({listings.filter(l => l.listing_type === 'sell').length})
                </button>
                <button
                  onClick={() => setFilter('buyers')}
                  className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                    filter === 'buyers'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  🟢 Buyers ({listings.filter(l => l.listing_type === 'buy').length})
                </button>
              </div>
            </div>

            {/* Current Filter Display */}
            <div className="text-center mb-6">
              <p className="text-gray-600">
                {filter === 'all' && `Showing all ${filteredListings.length} trading opportunities`}
                {filter === 'sellers' && `Showing ${filteredListings.length} sellers offering products`}
                {filter === 'buyers' && `Showing ${filteredListings.length} buyers seeking products`}
                {productFilter !== 'all' && (
                  <span className="ml-2 font-semibold">
                    for {productFilter.replace('_', ' ').toUpperCase()}
                  </span>
                )}
              </p>
              
              {/* Product Filter Badge */}
              {productFilter !== 'all' && (
                <div className="mt-2 flex justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
                    🛢️ {productFilter.replace('_', ' ').toUpperCase()}
                    <button
                      onClick={() => setProductFilter('all')}
                      className="ml-2 text-orange-600 hover:text-orange-800"
                    >
                      ✕
                    </button>
                  </span>
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredListings.map((listing, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-bold">{listing.title}</h3>
                      <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-bold ${
                        listing.listing_type === 'sell' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {listing.listing_type === 'sell' ? '🔴 SELLING' : '🟢 BUYING'}
                      </span>
                    </div>
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
            
            {filteredListings.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">
                  {filter === 'sellers' ? '🔴' : filter === 'buyers' ? '🟢' : '🛢️'}
                </div>
                <p className="text-gray-600 mb-4">
                  {filter === 'sellers' && 'No sellers found.'}
                  {filter === 'buyers' && 'No buyers found.'}
                  {filter === 'all' && 'No listings found.'}
                </p>
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
};

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

    const handleFileUpload = async (file) => {
      if (!file) return null;
      
      setUploading(true);
      try {
        const fileFormData = new FormData();
        fileFormData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/upload/procedure`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: fileFormData
        });
        
        if (response.ok) {
          const result = await response.json();
          setUploadedFile(result);
          return result.file_path;
        } else {
          const error = await response.json();
          alert('File upload failed: ' + (error.detail || 'Unknown error'));
          return null;
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('File upload failed');
        return null;
      } finally {
        setUploading(false);
      }
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

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      let procedureFilePath = formData.procedure_document;
      
      // Upload file if selected
      const fileInput = e.target.querySelector('input[type="file"]');
      if (fileInput && fileInput.files[0]) {
        procedureFilePath = await handleFileUpload(fileInput.files[0]);
        if (!procedureFilePath) {
          return; // File upload failed
        }
      }
      
      const listingData = {
        ...formData,
        quantity: parseFloat(formData.quantity),
        procedure_document: procedureFilePath
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Listing Type</label>
                <select
                  name="listing_type"
                  value={formData.listing_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                >
                  <option value="sell">🔴 Selling - I have this product to sell</option>
                  <option value="buy">🟢 Buying - I want to purchase this product</option>
                </select>
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
                  Procedure Document Upload
                  <span className="text-gray-500 text-xs ml-1">(Optional - PDF only, max 10MB)</span>
                </label>
                <div className="space-y-3">
                  <input
                    type="file"
                    accept=".pdf"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                  {uploading && (
                    <div className="flex items-center text-blue-600">
                      <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Uploading PDF...
                    </div>
                  )}
                  {uploadedFile && (
                    <div className="flex items-center text-green-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                      File uploaded: {uploadedFile.filename}
                    </div>
                  )}
                </div>
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
      listing_type: editingListing?.listing_type || 'sell',
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
      procedure_document: editingListing?.procedure_document || '',
      is_featured: editingListing?.is_featured || false
    });

    const [uploadedFile, setUploadedFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleFileUpload = async (file) => {
      if (!file) return null;
      
      setUploading(true);
      try {
        const fileFormData = new FormData();
        fileFormData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/upload/procedure`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: fileFormData
        });
        
        if (response.ok) {
          const result = await response.json();
          setUploadedFile(result);
          return result.file_path;
        } else {
          const error = await response.json();
          alert('File upload failed: ' + (error.detail || 'Unknown error'));
          return null;
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('File upload failed');
        return null;
      } finally {
        setUploading(false);
      }
    };

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

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      let procedureFilePath = formData.procedure_document;
      
      // Upload file if selected
      const fileInput = e.target.querySelector('input[type="file"]');
      if (fileInput && fileInput.files[0]) {
        procedureFilePath = await handleFileUpload(fileInput.files[0]);
        if (!procedureFilePath) {
          return; // File upload failed
        }
      }
      
      const listingData = {
        ...formData,
        quantity: parseFloat(formData.quantity),
        procedure_document: procedureFilePath
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Update Procedure Document
                  <span className="text-gray-500 text-xs ml-1">(Optional - PDF only, max 10MB)</span>
                </label>
                <div className="space-y-3">
                  {formData.procedure_document && (
                    <div className="flex items-center text-blue-600 bg-blue-50 p-3 rounded-lg">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      Current document uploaded
                    </div>
                  )}
                  <input
                    type="file"
                    accept=".pdf"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                  <p className="text-xs text-gray-500">Upload a new PDF to replace the current document</p>
                </div>
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
                        <span className="w-24 text-gray-600 font-semibold">Type:</span>
                        <span className={`text-lg font-bold ${
                          selectedListing.listing_type === 'sell' ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {selectedListing.listing_type === 'sell' ? '🔴 SELLING' : '🟢 BUYING'}
                        </span>
                      </div>
                      
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

                    {/* Procedure Document */}
                    {selectedListing.procedure_document && (
                      <div className="mt-8">
                        <h3 className="text-xl font-bold mb-4 text-gray-900">Procedure Document</h3>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <div className="flex items-center">
                            <svg className="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                            <div className="flex-1">
                              <p className="text-gray-900 font-semibold">Trading Procedure PDF</p>
                              <p className="text-gray-600 text-sm">Download detailed trading procedures and documentation</p>
                            </div>
                            <a
                              href={`${API_BASE_URL}/api/download/procedure/${selectedListing.procedure_document}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                            >
                              📥 Download PDF
                            </a>
                          </div>
                        </div>
                      </div>
                    )}
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

  const EmailConfigStatus = () => {
    const [emailConfig, setEmailConfig] = useState(null);
    const [testResult, setTestResult] = useState('');

    const fetchEmailConfig = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/email-config`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setEmailConfig(data);
        }
      } catch (error) {
        console.error('Email config error:', error);
      }
    };

    const testEmailConfig = async () => {
      setTestResult('Sending test email...');
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/test-email`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setTestResult(`✅ ${data.message}`);
        } else {
          const error = await response.json();
          setTestResult(`❌ ${error.detail || 'Test failed'}`);
        }
      } catch (error) {
        setTestResult('❌ Network error during test');
      }
    };

    useEffect(() => {
      fetchEmailConfig();
    }, []);

    if (!emailConfig) {
      return <div className="text-sm text-gray-600">Loading email config...</div>;
    }

    return (
      <div className="space-y-3">
        <div className={`flex items-center space-x-2 ${emailConfig.configured ? 'text-green-600' : 'text-red-600'}`}>
          <span className="text-lg">{emailConfig.configured ? '✅' : '❌'}</span>
          <span className="font-semibold">
            {emailConfig.configured ? 'Email Configured' : 'Email NOT Configured'}
          </span>
        </div>
        
        <div className="text-sm space-y-1">
          <p><strong>SMTP Server:</strong> {emailConfig.smtp_server}:{emailConfig.smtp_port}</p>
          <p><strong>From Email:</strong> {emailConfig.from_email}</p>
          <p><strong>Username:</strong> {emailConfig.smtp_username}</p>
          <p><strong>Password:</strong> {emailConfig.smtp_password}</p>
        </div>

        {emailConfig.configured ? (
          <div>
            <button
              onClick={testEmailConfig}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded text-sm"
            >
              Send Test Email
            </button>
            {testResult && (
              <p className="text-xs mt-2 p-2 bg-gray-100 rounded">{testResult}</p>
            )}
          </div>
        ) : (
          <div className="text-xs text-red-600">
            <p><strong>Required Environment Variables:</strong></p>
            <p>• SMTP_USERNAME</p>
            <p>• SMTP_PASSWORD</p>
            <p>• SMTP_SERVER (optional)</p>
            <p>• FROM_EMAIL (optional)</p>
          </div>
        )}
      </div>
    );
  };

  const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [adminStats, setAdminStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [totalUsers, setTotalUsers] = useState(0);
    const [searchTerm, setSearchTerm] = useState('');
    const [roleFilter, setRoleFilter] = useState('');
    const [currentPage, setCurrentUsersPage] = useState(0);
    const [adminLoading, setAdminLoading] = useState(false);

    // Fetch admin statistics
    const fetchAdminStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setAdminStats(data);
        } else {
          alert('Failed to fetch admin statistics');
        }
      } catch (error) {
        console.error('Admin stats error:', error);
        alert('Network error fetching statistics');
      }
    };

    // Fetch users for management
    const fetchUsers = async (page = 0) => {
      setAdminLoading(true);
      try {
        const params = new URLSearchParams({
          skip: (page * 50).toString(),
          limit: '50'
        });
        
        if (searchTerm) params.append('search', searchTerm);
        if (roleFilter) params.append('role', roleFilter);
        
        const response = await fetch(`${API_BASE_URL}/api/admin/users?${params}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setUsers(data.users);
          setTotalUsers(data.total_count);
        } else {
          alert('Failed to fetch users');
        }
      } catch (error) {
        console.error('Fetch users error:', error);
        alert('Network error fetching users');
      }
      setAdminLoading(false);
    };

    // Manage user action (activate, deactivate, etc.)
    const handleUserAction = async (userId, action) => {
      if (!confirm(`Are you sure you want to ${action} this user?`)) return;
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ user_id: userId, action })
        });
        
        if (response.ok) {
          alert(`User ${action} successful`);
          fetchUsers(currentPage);
        } else {
          const error = await response.json();
          alert(error.detail || `Failed to ${action} user`);
        }
      } catch (error) {
        console.error('User action error:', error);
        alert('Network error');
      }
    };

    // Export data
    const handleExport = async (type) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/export/${type}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${type}_export.csv`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          alert(`Failed to export ${type}`);
        }
      } catch (error) {
        console.error('Export error:', error);
        alert('Network error during export');
      }
    };

    useEffect(() => {
      if (activeTab === 'dashboard') {
        fetchAdminStats();
      } else if (activeTab === 'users') {
        fetchUsers(0);
      }
    }, [activeTab]);

    useEffect(() => {
      fetchUsers(currentPage);
    }, [searchTerm, roleFilter, currentPage]);

    // Check if user is admin
    if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
            <p className="text-gray-600 mb-4">You need admin privileges to access this page.</p>
            <button
              onClick={() => setCurrentPage('home')}
              className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-2 rounded-lg"
            >
              Back to Home
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Admin Header */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-gray-600">Oil & Gas Finder Management Panel</p>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={() => handleExport('users')}
                  className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg"
                >
                  Export Users
                </button>
                <button
                  onClick={() => handleExport('listings')}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg"
                >
                  Export Listings
                </button>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm mb-8">
            <div className="border-b border-gray-200">
              <nav className="flex">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'dashboard'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'users'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  User Management
                </button>
                <button
                  onClick={() => setActiveTab('reports')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'reports'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Reports
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'dashboard' && (
                <div>
                  <h2 className="text-xl font-bold mb-6">Platform Statistics</h2>
                  
                  {adminStats ? (
                    <>
                      {/* Key Metrics */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-blue-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold text-blue-900">Total Users</h3>
                          <p className="text-3xl font-bold text-blue-600">{adminStats.basic_stats.total_users}</p>
                        </div>
                        <div className="bg-green-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold text-green-900">Active Listings</h3>
                          <p className="text-3xl font-bold text-green-600">{adminStats.basic_stats.active_listings}</p>
                        </div>
                        <div className="bg-purple-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold text-purple-900">Premium Users</h3>
                          <p className="text-3xl font-bold text-purple-600">{adminStats.basic_stats.premium_users}</p>
                        </div>
                        <div className="bg-orange-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold text-orange-900">Today's Signups</h3>
                          <p className="text-3xl font-bold text-orange-600">{adminStats.basic_stats.registrations_today}</p>
                        </div>
                      </div>

                      {/* Charts Section */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* User Roles */}
                        <div className="bg-gray-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold mb-4">User Roles Distribution</h3>
                          {adminStats.user_roles.map((role, index) => (
                            <div key={index} className="flex justify-between items-center mb-2">
                              <span className="capitalize">{role._id}</span>
                              <span className="font-bold">{role.count}</span>
                            </div>
                          ))}
                        </div>

                        {/* Product Types */}
                        <div className="bg-gray-50 p-6 rounded-lg">
                          <h3 className="text-lg font-semibold mb-4">Popular Products</h3>
                          {adminStats.product_stats.slice(0, 5).map((product, index) => (
                            <div key={index} className="flex justify-between items-center mb-2">
                              <span className="capitalize">{product._id?.replace('_', ' ')}</span>
                              <span className="font-bold">{product.count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto"></div>
                      <p className="mt-2 text-gray-600">Loading statistics...</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'users' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">User Management</h2>
                    <p className="text-gray-600">Total: {totalUsers} users</p>
                  </div>

                  {/* Search and Filter */}
                  <div className="flex gap-4 mb-6">
                    <input
                      type="text"
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                    <select
                      value={roleFilter}
                      onChange={(e) => setRoleFilter(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      <option value="">All Roles</option>
                      <option value="basic">Basic</option>
                      <option value="premium">Premium</option>
                      <option value="enterprise">Enterprise</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>

                  {/* Users Table */}
                  {adminLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto"></div>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="min-w-full bg-white border border-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trading Role</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {users.map((user) => (
                            <tr key={user.user_id}>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">
                                    {user.first_name} {user.last_name}
                                  </div>
                                  <div className="text-sm text-gray-500">{user.email}</div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {user.company_name}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                  user.role === 'premium' ? 'bg-purple-100 text-purple-800' :
                                  user.role === 'enterprise' ? 'bg-blue-100 text-blue-800' :
                                  user.role === 'admin' ? 'bg-red-100 text-red-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {user.role}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                                {user.trading_role}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {new Date(user.created_at).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <div className="flex space-x-2">
                                  {user.status !== 'inactive' ? (
                                    <button
                                      onClick={() => handleUserAction(user.user_id, 'deactivate')}
                                      className="text-red-600 hover:text-red-900"
                                    >
                                      Deactivate
                                    </button>
                                  ) : (
                                    <button
                                      onClick={() => handleUserAction(user.user_id, 'activate')}
                                      className="text-green-600 hover:text-green-900"
                                    >
                                      Activate
                                    </button>
                                  )}
                                  {user.role === 'basic' && user.role !== 'super_admin' && (
                                    <button
                                      onClick={() => handleUserAction(user.user_id, 'promote')}
                                      className="text-blue-600 hover:text-blue-900"
                                    >
                                      Promote
                                    </button>
                                  )}
                                  {user.role === 'admin' && user.role !== 'super_admin' && (
                                    <button
                                      onClick={() => handleUserAction(user.user_id, 'demote')}
                                      className="text-orange-600 hover:text-orange-900"
                                    >
                                      Demote
                                    </button>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'reports' && (
                <div>
                  <h2 className="text-xl font-bold mb-6">Data Reports & Configuration</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Export Options</h3>
                      <div className="space-y-3">
                        <button
                          onClick={() => handleExport('users')}
                          className="w-full bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg"
                        >
                          Export All Users (CSV)
                        </button>
                        <button
                          onClick={() => handleExport('listings')}
                          className="w-full bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg"
                        >
                          Export All Listings (CSV)
                        </button>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
                      {adminStats && (
                        <div className="space-y-2">
                          <p>This Month's Registrations: <strong>{adminStats.basic_stats.registrations_this_month}</strong></p>
                          <p>Total Listings: <strong>{adminStats.basic_stats.total_listings}</strong></p>
                          <p>Premium Conversion Rate: <strong>
                            {((adminStats.basic_stats.premium_users / adminStats.basic_stats.total_users) * 100).toFixed(1)}%
                          </strong></p>
                        </div>
                      )}
                    </div>

                    <div className="bg-yellow-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Email Configuration</h3>
                      <EmailConfigStatus />
                    </div>
                  </div>
                </div>
              )}
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
      case 'forgot-password':
        return <ForgotPasswordPage />;
      case 'reset-password':
        return <ResetPasswordPage />;
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
      case 'terms':
        return <TermsOfService />;
      case 'privacy':
        return <PrivacyPolicy />;
      case 'disclaimer':
        return <Disclaimer />;
      case 'find-connections':
        return <EnhancedHomePage 
          onNavigate={navigateToPage}
          listings={listings}
          onSetSelectedListing={setSelectedListing}
          showProductFilter={true}
        />;
      case 'admin':
        return <AdminDashboard />;
      default:
        return <EnhancedHomePage 
          onNavigate={navigateToPage}
          listings={listings}
          onSetSelectedListing={setSelectedListing}
        />;
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