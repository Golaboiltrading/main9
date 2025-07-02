import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link

// This component will need 'handleLogin' and 'loading' state from App.js as props.
const LoginPage = ({ handleLogin, loading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  // const navigate = useNavigate(); // No longer needed if using Link and App.js navigate

  const handleSubmit = (e) => {
    e.preventDefault();
    handleLogin(email, password); // handleLogin in App.js will use navigate
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
          {/* Use Link for navigation */}
          <Link
            to="/register"
            className="text-orange-600 hover:text-orange-500 font-semibold"
          >
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
