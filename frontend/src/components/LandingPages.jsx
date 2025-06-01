import React, { useState, useEffect } from 'react';
import { SEO, LocalBusinessSchema, BreadcrumbSchema } from './SEO';

// Location-based Landing Page Component
export const LocationLandingPage = ({ location }) => {
  const [locationData, setLocationData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLocationData();
  }, [location]);

  const fetchLocationData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/locations/${location}`);
      const data = await response.json();
      setLocationData(data.location);
      setMarketData(data.market_data);
    } catch (error) {
      console.error('Error fetching location data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  const locationName = location.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <div className="bg-white">
      <SEO 
        title={`Oil & Gas Trading in ${locationName} | Market Hub`}
        description={`Connect with oil and gas traders in ${locationName}. Access local market data, trading opportunities, and verified buyers and sellers.`}
        keywords={`${location} oil trading, ${location} gas market, ${location} energy trading, petroleum ${location}`}
        url={`/locations/${location}`}
        location={locationName}
      />
      
      <LocalBusinessSchema 
        location={locationName}
        address={locationData?.address}
        phone={locationData?.phone}
        services={["Oil Trading", "Gas Trading", "Market Data", "Trading Connections"]}
      />
      
      <BreadcrumbSchema items={[
        { name: "Home", url: "/" },
        { name: "Locations", url: "/locations" },
        { name: locationName, url: `/locations/${location}` }
      ]} />

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              Oil & Gas Trading in {locationName}
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-8">
              Connect with verified buyers and sellers in {locationName}'s energy market. 
              Access real-time pricing, market insights, and trading opportunities.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => window.location.href = '/register'}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
              >
                Start Trading
              </button>
              <button 
                onClick={() => window.location.href = '/browse'}
                className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors"
              >
                Browse Traders
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Market Data Section */}
      {marketData && (
        <div className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                {locationName} Market Overview
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Real-time market data and insights for {locationName}'s oil and gas trading hub.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="bg-white p-6 rounded-lg shadow-md text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  ${marketData.crude_oil_price}
                </div>
                <div className="text-gray-600">Crude Oil Price</div>
                <div className="text-sm text-green-600 mt-1">
                  +{marketData.crude_oil_change}%
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  ${marketData.natural_gas_price}
                </div>
                <div className="text-gray-600">Natural Gas Price</div>
                <div className="text-sm text-red-600 mt-1">
                  {marketData.natural_gas_change}%
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {marketData.active_traders}
                </div>
                <div className="text-gray-600">Active Traders</div>
                <div className="text-sm text-blue-600 mt-1">
                  +{marketData.new_traders_today} today
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {marketData.daily_volume}
                </div>
                <div className="text-gray-600">Daily Volume (BBL)</div>
                <div className="text-sm text-green-600 mt-1">
                  +{marketData.volume_change}%
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Location Benefits */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Trade in {locationName}?
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Strategic Location</h3>
              <p className="text-gray-600">
                {locationName} serves as a major hub for global oil and gas trading with excellent infrastructure.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Verified Traders</h3>
              <p className="text-gray-600">
                All traders in {locationName} are thoroughly verified for secure and reliable transactions.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Local Expertise</h3>
              <p className="text-gray-600">
                Access local market knowledge and regulations specific to {locationName}'s trading environment.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Trade in {locationName}?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join the leading oil and gas trading platform and connect with verified traders in {locationName}.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/register'}
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
            >
              Create Free Account
            </button>
            <button 
              onClick={() => window.location.href = '/premium'}
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors"
            >
              View Premium Features
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Product-specific Landing Page Component
export const ProductLandingPage = ({ productType }) => {
  const [productData, setProductData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProductData();
  }, [productType]);

  const fetchProductData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products/${productType}`);
      const data = await response.json();
      setProductData(data);
    } catch (error) {
      console.error('Error fetching product data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  const productName = productType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <div className="bg-white">
      <SEO 
        title={`${productName} Trading Platform | Global Market Access`}
        description={`Trade ${productName.toLowerCase()} with verified buyers and sellers worldwide. Real-time pricing, market data, and secure trading connections.`}
        keywords={`${productType} trading, ${productType} market, ${productType} prices, ${productName} buyers, ${productName} sellers`}
        url={`/products/${productType}`}
        productType={productName}
      />
      
      <BreadcrumbSchema items={[
        { name: "Home", url: "/" },
        { name: "Products", url: "/products" },
        { name: productName, url: `/products/${productType}` }
      ]} />

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-900 to-blue-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold mb-6">
                {productName} Trading Platform
              </h1>
              <p className="text-xl text-gray-300 mb-8">
                Connect with verified {productName.toLowerCase()} traders worldwide. 
                Access real-time market data, competitive pricing, and secure trading opportunities.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => window.location.href = '/register'}
                  className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors"
                >
                  Start Trading
                </button>
                <button 
                  onClick={() => window.location.href = `/products/${productType}#pricing`}
                  className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-gray-900 transition-colors"
                >
                  View Live Prices
                </button>
              </div>
            </div>
            <div className="lg:text-right">
              <img 
                src={`/images/products/${productType}-hero.jpg`} 
                alt={`${productName} trading`}
                className="w-full h-80 object-cover rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Market Data Section */}
      {productData && (
        <div className="py-16 bg-gray-50" id="pricing">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                {productName} Market Data
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Real-time pricing and market insights for {productName.toLowerCase()} trading.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white p-8 rounded-lg shadow-md text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  ${productData.current_price}
                </div>
                <div className="text-gray-600 text-lg mb-2">Current Price</div>
                <div className="text-sm text-green-600">
                  +{productData.price_change}% (24h)
                </div>
              </div>
              
              <div className="bg-white p-8 rounded-lg shadow-md text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {productData.daily_volume}
                </div>
                <div className="text-gray-600 text-lg mb-2">Daily Volume</div>
                <div className="text-sm text-blue-600">
                  +{productData.volume_change}% vs yesterday
                </div>
              </div>
              
              <div className="bg-white p-8 rounded-lg shadow-md text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">
                  {productData.active_listings}
                </div>
                <div className="text-gray-600 text-lg mb-2">Active Listings</div>
                <div className="text-sm text-green-600">
                  {productData.new_listings} new today
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Our {productName} Trading Platform?
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-time Pricing</h3>
              <p className="text-gray-600">
                Access live {productName.toLowerCase()} prices from global markets and make informed trading decisions.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Verified Traders</h3>
              <p className="text-gray-600">
                All {productName.toLowerCase()} traders are thoroughly verified for secure and reliable transactions.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Global Network</h3>
              <p className="text-gray-600">
                Connect with {productName.toLowerCase()} buyers and sellers from over 50 countries worldwide.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start Trading {productName} Today
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of energy professionals trading {productName.toLowerCase()} on our secure platform.
          </p>
          <button 
            onClick={() => window.location.href = '/register'}
            className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
          >
            Create Free Account
          </button>
        </div>
      </div>
    </div>
  );
};