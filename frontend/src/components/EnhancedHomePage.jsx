import React, { useState, useEffect } from 'react';

const EnhancedHomePage = ({ onNavigate, listings = [], onSetSelectedListing }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [stats, setStats] = useState({});

  // Create a ProductFilterPage component
  const ProductFilterPage = () => {
    const productTypes = [
      { key: 'crude_oil', name: 'Crude Oil', icon: '🛢️', color: 'bg-orange-600' },
      { key: 'natural_gas', name: 'Natural Gas', icon: '⛽', color: 'bg-blue-600' },
      { key: 'lng', name: 'LNG', icon: '🌊', color: 'bg-indigo-600' },
      { key: 'lpg', name: 'LPG', icon: '🔥', color: 'bg-purple-600' },
      { key: 'gasoline', name: 'Gasoline', icon: '⛽', color: 'bg-red-600' },
      { key: 'diesel', name: 'Diesel', icon: '🚛', color: 'bg-green-600' },
      { key: 'jet_fuel', name: 'Jet Fuel', icon: '✈️', color: 'bg-gray-600' }
    ];

    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Find Oil & Gas Connections</h1>
            <p className="text-xl text-gray-600 mb-8">Browse buyers and sellers by product type</p>
            <button
              onClick={() => {
                window.history.pushState({}, '', '/');
                window.location.reload();
              }}
              className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-2 rounded-lg font-semibold"
            >
              ← Back to Home
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {productTypes.map((product) => {
              const productListings = listings.filter(l => l.product_type === product.key);
              const sellers = productListings.filter(l => l.listing_type === 'sell');
              const buyers = productListings.filter(l => l.listing_type === 'buy');

              return (
                <div key={product.key} className={`${product.color} rounded-lg shadow-lg overflow-hidden`}>
                  <div className="p-6 text-white">
                    <div className="flex items-center mb-4">
                      <span className="text-4xl mr-3">{product.icon}</span>
                      <h3 className="text-2xl font-bold">{product.name}</h3>
                    </div>
                    
                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between items-center">
                        <span>🔴 Sellers</span>
                        <span className="font-bold">{sellers.length}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>🟢 Buyers</span>
                        <span className="font-bold">{buyers.length}</span>
                      </div>
                      <div className="border-t border-white/30 pt-2">
                        <div className="flex justify-between items-center">
                          <span>Total Opportunities</span>
                          <span className="font-bold text-xl">{productListings.length}</span>
                        </div>
                      </div>
                    </div>

                    {productListings.length > 0 ? (
                      <div className="space-y-2">
                        <button
                          onClick={() => {
                            // Set a filter and navigate to browse
                            localStorage.setItem('productFilter', product.key);
                            localStorage.setItem('listingTypeFilter', 'all');
                            onNavigate('browse');
                          }}
                          className="w-full bg-white/20 hover:bg-white/30 text-white py-2 px-4 rounded-lg font-semibold transition-colors border border-white/30"
                        >
                          View All {product.name}
                        </button>
                        {sellers.length > 0 && (
                          <button
                            onClick={() => {
                              localStorage.setItem('productFilter', product.key);
                              localStorage.setItem('listingTypeFilter', 'sellers');
                              onNavigate('browse');
                            }}
                            className="w-full bg-red-500/80 hover:bg-red-500 text-white py-2 px-4 rounded-lg font-semibold transition-colors"
                          >
                            View {sellers.length} Sellers
                          </button>
                        )}
                        {buyers.length > 0 && (
                          <button
                            onClick={() => {
                              localStorage.setItem('productFilter', product.key);
                              localStorage.setItem('listingTypeFilter', 'buyers');
                              onNavigate('browse');
                            }}
                            className="w-full bg-green-500/80 hover:bg-green-500 text-white py-2 px-4 rounded-lg font-semibold transition-colors"
                          >
                            View {buyers.length} Buyers
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="text-center">
                        <p className="text-white/80 mb-3">No listings yet</p>
                        <button
                          onClick={() => onNavigate('register')}
                          className="bg-white/20 hover:bg-white/30 text-white py-2 px-4 rounded-lg font-semibold transition-colors border border-white/30"
                        >
                          Be the First to List
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-center mt-12">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold mb-4">Don't see your product?</h3>
              <p className="text-gray-600 mb-6">Join our platform and create listings for any oil & gas products</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => onNavigate('register')}
                  className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-3 rounded-lg font-semibold"
                >
                  Create Account
                </button>
                <button
                  onClick={() => onNavigate('browse')}
                  className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-3 rounded-lg font-semibold"
                >
                  Browse All Listings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Check if we should show the product filter page
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('view') === 'products') {
    return <ProductFilterPage />;
  }

  const heroSlides = [
    {
      image: "https://images.unsplash.com/photo-1613909207039-6905ac2eb19e?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Oil & Gas Trading Network",
      subtitle: "Connect and find verified crude oil traders worldwide. Our finder network helps you discover WTI, Brent, and regional grades with trusted partners.",
      cta: "Find Oil Traders",
      overlay: "bg-gradient-to-r from-orange-900/80 to-red-900/80"
    },
    {
      image: "https://images.unsplash.com/photo-1586943101559-4cdcf86a6f87?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Natural Gas Finder Network",
      subtitle: "Discover natural gas, LNG, and pipeline gas connections through our global finder platform. Access LNG terminals and distribution networks.",
      cta: "Find Gas Suppliers",
      overlay: "bg-gradient-to-r from-blue-900/80 to-indigo-900/80"
    },
    {
      image: "https://images.unsplash.com/photo-1597149304368-0e0e69fa7724?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Energy Connection Network",
      subtitle: "Find refineries, storage terminals, and logistics providers through our connection network. Discover secure supply chains for global energy distribution.",
      cta: "Join Finder Network",
      overlay: "bg-gradient-to-r from-gray-900/80 to-slate-900/80"
    }
  ];

  const energyFeatures = [
    {
      icon: "🛢️",
      title: "Crude Oil Finder",
      description: "Find WTI, Brent, Dubai, Urals, and specialty grades through our network. Connect with refinery sources and discover spot market opportunities.",
      background: "bg-gradient-to-br from-orange-600 to-red-700",
      metrics: "2.5M+ Barrels/Day Network"
    },
    {
      icon: "⛽",
      title: "Natural Gas Network", 
      description: "Discover pipeline gas, LNG cargoes, and storage solutions through our finder platform. Access major terminal networks and flexible connections.",
      background: "bg-gradient-to-br from-blue-600 to-indigo-700",
      metrics: "50+ LNG Terminal Network"
    },
    {
      icon: "⚡",
      title: "Refined Products Finder",
      description: "Find gasoline, diesel, jet fuel, and specialty products through our network. Discover refinery direct connections and trading desk access.",
      background: "bg-gradient-to-br from-green-600 to-teal-700",
      metrics: "1M+ MT/Month Network"
    },
    {
      icon: "🏭",
      title: "Petrochemical Network",
      description: "Connect with ethylene, propylene, benzene, and chemical feedstock sources. Find direct producer and consumer connections through our platform.",
      background: "bg-gradient-to-br from-purple-600 to-pink-700",
      metrics: "500+ Producer Network"
    },
    {
      icon: "🚢",
      title: "Maritime Connection Network",
      description: "Find tanker chartering, storage solutions, and global logistics networks for energy commodities through our connection platform.",
      background: "bg-gradient-to-br from-slate-600 to-gray-800",
      metrics: "200+ Vessel Network"
    },
    {
      icon: "📊",
      title: "Market Intelligence Network",
      description: "Access real-time pricing, market analysis, and trading signals from our global energy market intelligence network and finder platform.",
      background: "bg-gradient-to-br from-yellow-600 to-orange-700",
      metrics: "24/7 Network Analytics"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Industry-Focused Hero Slideshow */}
      <div className="relative h-screen overflow-hidden">
        {heroSlides.map((slide, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-all duration-2000 ${
              index === currentSlide ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
            }`}
          >
            <div 
              className="absolute inset-0 bg-cover bg-center bg-no-repeat transform transition-transform duration-6000"
              style={{ backgroundImage: `url(${slide.image})` }}
            />
            <div className={`absolute inset-0 ${slide.overlay}`} />
            <div className="relative z-10 flex items-center justify-center h-full text-white px-4">
              <div className="max-w-5xl mx-auto text-center">
                <div className="mb-6 text-lg text-orange-300 font-semibold tracking-wide">
                  ENERGY CONNECTION FINDER PLATFORM
                </div>
                <h1 className="text-6xl md:text-8xl font-bold mb-8 leading-tight animate-fade-in-up">
                  {slide.title}
                </h1>
                <p className="text-xl md:text-2xl mb-10 text-gray-200 max-w-4xl mx-auto leading-relaxed animate-fade-in-up delay-300">
                  {slide.subtitle}
                </p>
                <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-4 mb-8 max-w-3xl mx-auto">
                  <p className="text-yellow-800 text-sm font-semibold">
                    🔗 CONNECTION PLATFORM ONLY - We help you find and connect with energy traders. We do not facilitate direct commodity trading.
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-6 justify-center animate-fade-in-up delay-600">
                  <button 
                    onClick={() => onNavigate('browse')}
                    className="bg-orange-600 hover:bg-orange-500 text-white px-10 py-4 rounded-lg text-xl font-bold transform hover:scale-105 transition-all duration-300 shadow-2xl"
                  >
                    {slide.cta}
                  </button>
                  <button 
                    onClick={() => {
                      window.history.pushState({}, '', '?view=products');
                      window.location.reload();
                    }}
                    className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-10 py-4 rounded-lg text-xl font-bold transform hover:scale-105 transition-all duration-300"
                  >
                    View Network Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Professional Slide Indicators */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-3 z-20">
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-4 h-4 rounded-full transition-all duration-300 ${
                index === currentSlide ? 'bg-orange-500 w-8' : 'bg-white/50 hover:bg-white/80'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Energy Network Stats */}
      <section className="py-20 bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-orange-300">Global Energy Connection Network</h2>
            <p className="text-xl text-gray-300">Find and connect with energy professionals across major trading hubs</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 text-center">
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-orange-400 group-hover:text-orange-300">
                {stats.oil_gas_traders || '2,543'}+
              </div>
              <div className="text-blue-200 text-lg">Network Members</div>
              <div className="text-gray-400 text-sm mt-1">Verified Professionals</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-green-400 group-hover:text-green-300">
                $2.5B+
              </div>
              <div className="text-blue-200 text-lg">Network Volume</div>
              <div className="text-gray-400 text-sm mt-1">Monthly Connections</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-purple-400 group-hover:text-purple-300">
                156
              </div>
              <div className="text-blue-200 text-lg">Countries</div>
              <div className="text-gray-400 text-sm mt-1">Global Network</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-yellow-400 group-hover:text-yellow-300">
                24/7
              </div>
              <div className="text-blue-200 text-lg">Network Access</div>
              <div className="text-gray-400 text-sm mt-1">Connection Platform</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-red-400 group-hover:text-red-300">
                85+
              </div>
              <div className="text-blue-200 text-lg">Refineries</div>
              <div className="text-gray-400 text-sm mt-1">Network Access</div>
            </div>
          </div>
        </div>
      </section>

      {/* Energy Connection Features */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Complete Energy Connection Network
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              From crude oil to refined products, natural gas to petrochemicals - find and connect with the world's largest 
              energy commodity network through our finder platform with verified connection partners.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-8 max-w-4xl mx-auto">
              <p className="text-blue-800 text-lg font-semibold">
                🔗 FINDER & CONNECTION PLATFORM - We help you discover and connect with energy professionals. All transactions are conducted directly between parties.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {energyFeatures.map((feature, index) => (
              <div
                key={index}
                className={`${feature.background} rounded-2xl p-8 text-white transform hover:scale-105 hover:-rotate-1 transition-all duration-500 cursor-pointer group relative overflow-hidden`}
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative z-10">
                  <div className="text-7xl mb-6 group-hover:animate-bounce-subtle">
                    {feature.icon}
                  </div>
                  <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                  <p className="text-lg opacity-90 mb-6 leading-relaxed">{feature.description}</p>
                  <div className="bg-white/20 rounded-lg p-3 mb-4">
                    <div className="text-sm font-semibold text-orange-200">NETWORK SIZE</div>
                    <div className="text-lg font-bold">{feature.metrics}</div>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-all duration-500 transform translate-y-4 group-hover:translate-y-0">
                    <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-lg font-semibold transition-all duration-300 border border-white/30">
                      Find Connections →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Live Market Data Banner */}
      <section className="py-6 bg-gradient-to-r from-gray-900 via-slate-800 to-gray-900 text-white">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center items-center space-x-12 text-lg">
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-orange-300 font-semibold">WTI Crude:</span>
              <span className="text-green-400 font-bold text-xl">$75.25</span>
              <span className="text-green-400 flex items-center">▲ 1.2%</span>
              <span className="text-gray-400 text-sm">/BBL</span>
            </div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-orange-300 font-semibold">Brent:</span>
              <span className="text-green-400 font-bold text-xl">$79.50</span>
              <span className="text-green-400 flex items-center">▲ 0.8%</span>
              <span className="text-gray-400 text-sm">/BBL</span>
            </div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-blue-300 font-semibold">Henry Hub:</span>
              <span className="text-red-400 font-bold text-xl">$2.85</span>
              <span className="text-red-400 flex items-center">▼ 0.5%</span>
              <span className="text-gray-400 text-sm">/MMBtu</span>
            </div>
            <div className="text-gray-400 text-sm flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
              Network Data • Updated 30 sec ago
            </div>
          </div>
        </div>
      </section>

      {/* Industry CTA Section */}
      <section className="py-24 bg-gradient-to-r from-orange-600 via-red-600 to-orange-700 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-bold mb-8">
            Ready to Find Energy Partners?
          </h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto leading-relaxed">
            Join the world's most trusted energy connection network. Find and connect with refineries, 
            producers, and traders across oil, gas, and petrochemical markets.
          </p>
          <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-6 mb-12 max-w-4xl mx-auto">
            <p className="text-yellow-800 text-lg font-semibold">
              🔗 CONNECTION FINDER PLATFORM - We help you discover trading partners. All transactions conducted directly between connected parties.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button 
              onClick={() => {
                window.history.pushState({}, '', '?view=products');
                window.location.reload();
              }}
              className="bg-white text-orange-600 px-10 py-5 rounded-lg text-xl font-bold hover:bg-gray-100 transform hover:scale-105 transition-all duration-300 shadow-2xl"
            >
              Find Partners Now
            </button>
            <button 
              onClick={() => onNavigate('browse')}
              className="border-3 border-white text-white px-10 py-5 rounded-lg text-xl font-bold hover:bg-white hover:text-orange-600 transform hover:scale-105 transition-all duration-300"
            >
              Browse All Traders
            </button>
          </div>
          <div className="mt-12 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold">$0</div>
              <div className="text-orange-200">Connection Fee</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">24/7</div>
              <div className="text-orange-200">Network Access</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">100%</div>
              <div className="text-orange-200">Verified Network</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default EnhancedHomePage;