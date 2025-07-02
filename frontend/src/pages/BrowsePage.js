import React from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link
// Assuming NewsSidebar is in components/NewsBar as per App.js
import { NewsSidebar } from '../components/NewsBar';

// This component needs 'listings' from App.js as props.
// And navigate for the "Create Account to Post" button.
const BrowsePage = ({ listings }) => {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold text-center mb-12">Browse Oil & Gas Traders</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {listings && listings.map((listing, index) => ( // Added listings && to prevent error if undefined
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
                {/* TODO: Connect with Trader button functionality */}
                <button className="bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-lg w-full font-semibold transition-colors">
                  Connect with Trader
                </button>
              </div>
            ))}
          </div>

          {listings && listings.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛢️</div>
              <p className="text-gray-600 mb-4">No listings found.</p>
              <button
                onClick={() => navigate('/register')}
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

export default BrowsePage;
