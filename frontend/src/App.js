import React, { useState, useEffect } from 'react';
import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom'; // Added Link
import './App.css';

// Import Page Components
import HomePage from './pages/HomePage'; // Assuming EnhancedHomePage is now HomePage
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PremiumPage from './pages/PremiumPage';
import BrowsePage from './pages/BrowsePage';
// AIAnalysisPage is already a component, TermsOfService etc. are also components
import AIAnalysisPage from './components/AIAnalysisPage';
import { TermsOfService, PrivacyPolicy, Disclaimer } from './components/LegalPages';

// Import Layout Components
import HeaderComponent from './components/layout/Header'; // Renamed to avoid conflict with Header const

// Import Other Components used directly in App layout
import { LeadCaptureForm } from './components/Analytics';
import { DisclaimerBanner, FooterDisclaimer, HeaderWarning } from './components/DisclaimerBanner';
import NewsBar from './components/NewsBar'; // NewsSidebar is used within BrowsePage

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  // const [currentPage, setCurrentPage] = useState('home'); // REMOVE: Handled by react-router
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [marketData, setMarketData] = useState({});
  const [listings, setListings] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState('');
  const navigate = useNavigate(); // ADD: For programmatic navigation
  const location = useLocation(); // ADD: To get current path for active link styling if needed

  // REMOVE: useEffect for manual path parsing
  // useEffect(() => {
  //   const path = window.location.pathname;
  //   if (path === '/browse') setCurrentPage('browse');
  //   else if (path === '/premium') setCurrentPage('premium');
  //   else if (path === '/register') setCurrentPage('register');
  //   else if (path === '/login') setCurrentPage('login');
  //   else if (path === '/ai-analysis') setCurrentPage('ai-analysis');
  //   else setCurrentPage('home');
  // }, []);

  // REMOVE: manual navigateToPage function
  // const navigateToPage = (page) => {
  //   setCurrentPage(page);
  //   window.history.pushState({}, '', `/${page === 'home' ? '' : page}`);
  // };

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
        // setCurrentPage('dashboard'); // REMOVE: Use navigate
        navigate('/dashboard'); // ADD: Programmatic navigation
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
        // setCurrentPage('dashboard'); // REMOVE: Use navigate
        navigate('/dashboard'); // ADD: Programmatic navigation
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
    // setCurrentPage('home'); // REMOVE: Use navigate
    navigate('/'); // ADD: Programmatic navigation to home
  };

  // The Header component definition has been moved to frontend/src/components/layout/Header.js
  // Inline page component definitions (LoginPage, RegisterPage, PremiumPage, BrowsePage)
  // have been moved to their respective files in frontend/src/pages/

  // A placeholder for a DashboardPage - this would need to be created
  const DashboardPage = () => (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold">My Dashboard</h1>
      <p>Welcome to your dashboard, {user?.first_name}!</p>
      {/* More dashboard content here */}
    </div>
  );

  return (
    <div className="App">
      <DisclaimerBanner />
      <HeaderWarning />
      <NewsBar />
      {/* Pass user and handleLogout to the imported HeaderComponent */}
      <HeaderComponent user={user} handleLogout={handleLogout} />

      <Routes>
        <Route path="/" element={<HomePage />} /> {/* Assuming EnhancedHomePage is now HomePage */}
        <Route path="/login" element={<LoginPage handleLogin={handleLogin} loading={loading} />} />
        <Route path="/register" element={<RegisterPage handleRegister={handleRegister} loading={loading} />} />
        <Route path="/premium" element={<PremiumPage user={user} setSelectedTier={setSelectedTier} setShowPaymentModal={setShowPaymentModal} />} />
        <Route path="/browse" element={<BrowsePage listings={listings} />} />
        <Route path="/ai-analysis" element={<AIAnalysisPage />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/disclaimer" element={<Disclaimer />} />
        <Route path="/dashboard" element={user ? <DashboardPage /> : <LoginPage handleLogin={handleLogin} loading={loading} />} /> {/* Protected Route Example */}
        {/* Add other routes as needed, e.g., for specific listing details, user profile, etc. */}
      </Routes>
      
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