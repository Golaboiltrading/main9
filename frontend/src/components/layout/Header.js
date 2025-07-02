import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Import useAuth

const Header = () => { // Remove user and handleLogout from props
  const { user, logout } = useAuth(); // Consume context
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="bg-slate-900 text-white shadow-2xl border-b-2 border-orange-500">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🛢️</div>
              {/* Use Link for home navigation */}
              <Link to="/" className="text-2xl font-bold cursor-pointer text-orange-300 hover:text-orange-200 transition-colors">
                Oil & Gas Finder
              </Link>
            </div>
            <nav className="hidden md:flex space-x-6">
              <Link
                to="/"
                className={`hover:text-orange-300 font-semibold ${location.pathname === '/' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Home
              </Link>
              <Link
                to="/browse"
                className={`hover:text-orange-300 font-semibold ${location.pathname === '/browse' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Browse Traders
              </Link>
              <Link
                to="/ai-analysis"
                className={`hover:text-orange-300 font-semibold ${location.pathname === '/ai-analysis' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Product Analysis
              </Link>
              <Link
                to="/premium"
                className={`hover:text-orange-300 font-semibold ${location.pathname === '/premium' ? 'text-orange-300 border-b-2 border-orange-300' : ''}`}
              >
                Premium
              </Link>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-300">Welcome, {user.first_name}</span>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="bg-orange-600 hover:bg-orange-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Dashboard
                </button>
                <button
                  onClick={logout} // Use logout from context
                  className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:text-orange-300 font-semibold"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-orange-600 hover:bg-orange-500 px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
