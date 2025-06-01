import React, { useState, useEffect } from 'react';

const EnhancedHomePage = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [stats, setStats] = useState({});

  const heroSlides = [
    {
      image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Global Oil & Gas Trading Platform",
      subtitle: "Connect with verified traders worldwide. Real-time market data and secure trading connections.",
      cta: "Start Trading Now"
    },
    {
      image: "https://images.unsplash.com/photo-1518709268805-4e9042af2a73?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Premium Market Intelligence",
      subtitle: "Access exclusive market reports, price forecasts, and trading opportunities from industry experts.",
      cta: "Explore Premium"
    },
    {
      image: "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Secure Trading Network",
      subtitle: "All traders verified. All transactions secure. Trade with confidence on the world's most trusted platform.",
      cta: "Join Network"
    }
  ];

  const features = [
    {
      icon: "🛢️",
      title: "Oil Trading",
      description: "Access global crude oil markets with real-time pricing and verified sellers",
      background: "bg-gradient-to-br from-orange-500 to-red-600"
    },
    {
      icon: "⛽",
      title: "Gas Trading", 
      description: "Trade natural gas, LNG, and refined products with trusted partners worldwide",
      background: "bg-gradient-to-br from-blue-500 to-indigo-600"
    },
    {
      icon: "🚢",
      title: "Logistics Support",
      description: "Complete shipping and logistics solutions for global energy commodity trading",
      background: "bg-gradient-to-br from-green-500 to-teal-600"
    },
    {
      icon: "📊",
      title: "Market Intelligence",
      description: "Advanced analytics and market insights to make informed trading decisions",
      background: "bg-gradient-to-br from-purple-500 to-pink-600"
    },
    {
      icon: "🔒",
      title: "Secure Platform",
      description: "Bank-level security with verified traders and encrypted communications",
      background: "bg-gradient-to-br from-gray-700 to-gray-900"
    },
    {
      icon: "🌍",
      title: "Global Network",
      description: "Connect with traders from 50+ countries across all major energy markets",
      background: "bg-gradient-to-br from-yellow-500 to-orange-600"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 5000);
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
      {/* Cinematic Hero Slideshow */}
      <div className="relative h-screen overflow-hidden">
        {heroSlides.map((slide, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              index === currentSlide ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <div 
              className="absolute inset-0 bg-cover bg-center bg-no-repeat"
              style={{ backgroundImage: `url(${slide.image})` }}
            />
            <div className="absolute inset-0 bg-black bg-opacity-50" />
            <div className="relative z-10 flex items-center justify-center h-full text-white text-center px-4">
              <div className="max-w-4xl mx-auto">
                <h1 className="text-6xl md:text-7xl font-bold mb-6 animate-fade-in-up">
                  {slide.title}
                </h1>
                <p className="text-xl md:text-2xl mb-8 text-gray-200 animate-fade-in-up delay-300">
                  {slide.subtitle}
                </p>
                <button className="bg-orange-500 hover:bg-orange-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transform hover:scale-105 transition-all duration-300 animate-fade-in-up delay-600">
                  {slide.cta}
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {/* Slide Indicators */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2 z-20">
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                index === currentSlide ? 'bg-white' : 'bg-white bg-opacity-50'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Animated Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-900 to-blue-800 text-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 text-center">
            <div className="transform hover:scale-105 transition-transform duration-300">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-orange-400">
                {stats.oil_gas_traders || '2,543'}+
              </div>
              <div className="text-blue-200">Verified Traders</div>
            </div>
            <div className="transform hover:scale-105 transition-transform duration-300">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-green-400">
                {stats.active_oil_listings || '1,876'}+
              </div>
              <div className="text-blue-200">Active Listings</div>
            </div>
            <div className="transform hover:scale-105 transition-transform duration-300">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-purple-400">
                {stats.successful_connections || '4,231'}+
              </div>
              <div className="text-blue-200">Successful Deals</div>
            </div>
            <div className="transform hover:scale-105 transition-transform duration-300">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-yellow-400">
                {stats.premium_finders || '567'}+
              </div>
              <div className="text-blue-200">Premium Members</div>
            </div>
            <div className="transform hover:scale-105 transition-transform duration-300">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-red-400">
                50+
              </div>
              <div className="text-blue-200">Countries</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards with Hover Effects */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Complete Trading Solution
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to succeed in global oil & gas trading, from market intelligence to secure transactions.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`${feature.background} rounded-2xl p-8 text-white transform hover:scale-105 hover:rotate-1 transition-all duration-300 cursor-pointer group`}
              >
                <div className="text-6xl mb-4 group-hover:animate-bounce">
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                <p className="text-lg opacity-90">{feature.description}</p>
                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <button className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg font-semibold transition-all duration-300">
                    Learn More →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Market Indicators Banner */}
      <section className="py-4 bg-gray-900 text-white">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center items-center space-x-8 text-sm">
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">WTI Crude:</span>
              <span className="text-green-400 font-bold">$75.25</span>
              <span className="text-green-400">▲ 1.2%</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">Brent:</span>
              <span className="text-green-400 font-bold">$79.50</span>
              <span className="text-green-400">▲ 0.8%</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">Natural Gas:</span>
              <span className="text-red-400 font-bold">$2.85</span>
              <span className="text-red-400">▼ 0.5%</span>
            </div>
            <div className="text-gray-400 text-xs">
              Live • Updated 5 mins ago
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-orange-500 to-red-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Start Trading?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of energy professionals already trading on our secure platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-orange-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transform hover:scale-105 transition-all duration-300">
              Create Free Account
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-orange-600 transform hover:scale-105 transition-all duration-300">
              Explore Premium
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default EnhancedHomePage;