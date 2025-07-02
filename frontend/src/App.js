import React, { useState, useEffect } from 'react';
// Removed duplicate React import
import { Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom';
import './App.css';

import { AuthProvider } from './context/AuthContext'; // ADDED AuthProvider

// Import Page Components
import HomePage from './pages/HomePage';
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

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL; // This might move to an API service later

import { AuthProvider, useAuth } from './context/AuthContext'; // ADDED useAuth here as well

function AppContent() {
  // App-specific state (non-auth)
  const [stats, setStats] = useState({});
  const [marketData, setMarketData] = useState({});
  const [listings, setListings] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState('');

  const navigate = useNavigate(); // Still useful for non-auth navigation if any from AppContent
  const location = useLocation(); // Still useful for Header's active link styling

  // This useEffect fetches general app data.
  // If these fetches require a token, they should ideally be moved to a service
  // that can access the token from AuthContext, or this component
  // could use useAuth() to get the token.
  // For now, assuming they are public or will be adapted.
  useEffect(() => {
    fetchStats();
    fetchMarketData();
    fetchListings();
  }, []); // Re-evaluate dependencies if these fetches depend on auth token. For now, assume public or tokenless.

  // REMOVE: fetchUserProfile, it's in AuthProvider
  // const fetchUserProfile = async () => { ... };

  const fetchStats = async () => { // Keep as is if public
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

  // REMOVE: handleLogin, handleRegister, handleLogout - they are in AuthProvider
  // const handleLogin = async (email, password) => { ... };
  // const handleRegister = async (userData) => { ... };
  // const handleLogout = () => { ... };

  // DashboardPage will now use useAuth to get user information
  const DashboardPage = () => {
    const { user } = useAuth(); // Consume auth context
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold">My Dashboard</h1>
        <p>Welcome to your dashboard, {user?.first_name || 'User'}!</p>
        {/* More dashboard content here */}
      </div>
    );
  };

  // ProtectedRoute component (can be moved to a separate file later)
  const ProtectedRoute = ({ children }) => {
    const { user, isAuthLoading } = useAuth();
    const location = useLocation();

    if (isAuthLoading) {
      return <div>Loading session...</div>; // Or a spinner component
    }

    if (!user) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return children;
  };


  return (
    <div className="App">
      <DisclaimerBanner />
      <HeaderWarning />
      <NewsBar />
      <HeaderComponent /> {/* User and logout are now from context within HeaderComponent */}

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} /> {/* Props removed, will use context */}
        <Route path="/register" element={<RegisterPage />} /> {/* Props removed, will use context */}
        {/* PremiumPage will get user from context. Other props remain for now. */}
        <Route path="/premium" element={<PremiumPage setSelectedTier={setSelectedTier} setShowPaymentModal={setShowPaymentModal} />} />
        <Route path="/browse" element={<BrowsePage listings={listings} />} />
        <Route path="/ai-analysis" element={<AIAnalysisPage />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/disclaimer" element={<Disclaimer />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
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