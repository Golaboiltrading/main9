import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL; // Ensure this is accessible

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(localStorage.getItem('token')); // Renamed to avoid conflict
  const [loading, setLoading] = useState(false); // For auth operations like login/register
  const [isAuthLoading, setIsAuthLoading] = useState(true); // For initial token validation / profile fetch
  const navigate = useNavigate();

  useEffect(() => {
    const currentToken = localStorage.getItem('token');
    if (currentToken) {
      setTokenState(currentToken); // Sync with localStorage if it changes elsewhere (though unlikely for this app)
      // Fetch user profile if token exists
      const fetchUserProfile = async () => {
        setIsAuthLoading(true);
        try {
          const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
          });
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Token might be invalid or expired
            localStorage.removeItem('token');
            setTokenState(null);
            setUser(null);
          }
        } catch (error) {
          console.error('Error fetching profile:', error);
          localStorage.removeItem('token'); // Clear token on error too
          setTokenState(null);
          setUser(null);
        } finally {
          setIsAuthLoading(false);
        }
      };
      fetchUserProfile();
    } else {
      setIsAuthLoading(false); // No token, so not loading auth state
    }
  }, [token]); // Re-run if token changes (e.g. after login)

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setTokenState(data.access_token);
        setUser(data.user); // User data is set directly
        navigate('/dashboard');
      } else {
        // Consider throwing an error or returning a more specific error message
        alert('Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setTokenState(data.access_token);
        setUser(data.user); // User data is set directly
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setTokenState(null);
    setUser(null);
    navigate('/');
  };

  // The value provided to consuming components
  const value = {
    user,
    token,
    loading,
    isAuthLoading,
    login,
    register,
    logout,
    // No longer need to expose setters directly if auth functions handle state
  };

  return (
    <AuthContext.Provider value={value}>
      {!isAuthLoading ? children : <div>Loading authentication...</div>} {/* Show loading or children */}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
