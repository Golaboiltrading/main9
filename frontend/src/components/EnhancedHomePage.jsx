import React, { useState, useEffect } from 'react';

const EnhancedHomePage = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [stats, setStats] = useState({});

  const heroSlides = [
    {
      image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Global Oil Trading Hub",
      subtitle: "Connect with verified crude oil traders worldwide. Access WTI, Brent, and regional grades with real-time market data.",
      cta: "Start Trading Oil",
      overlay: "bg-gradient-to-r from-orange-900/80 to-red-900/80"
    },
    {
      image: "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Natural Gas & LNG Network",
      subtitle: "Trade natural gas, LNG, and pipeline gas with trusted partners. Access global LNG terminals and distribution networks.",
      cta: "Explore Gas Trading",
      overlay: "bg-gradient-to-r from-blue-900/80 to-indigo-900/80"
    },
    {
      image: "https://images.unsplash.com/photo-1518709268805-4e9042af2a73?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
      title: "Refinery & Terminal Operations",
      subtitle: "Connect refineries, storage terminals, and logistics providers. Secure supply chains for global energy distribution.",
      cta: "Join Network",
      overlay: "bg-gradient-to-r from-gray-900/80 to-slate-900/80"
    }
  ];

  const energyFeatures = [
    {
      icon: "🛢️",
      title: "Crude Oil Trading",
      description: "WTI, Brent, Dubai, Urals, and specialty grades. Direct refinery connections and spot market access.",
      background: "bg-gradient-to-br from-orange-600 to-red-700",
      metrics: "2.5M+ Barrels/Day"
    },
    {
      icon: "⛽",
      title: "Natural Gas & LNG", 
      description: "Pipeline gas, LNG cargoes, and storage solutions. Major terminal access and flexible contracts.",
      background: "bg-gradient-to-br from-blue-600 to-indigo-700",
      metrics: "50+ LNG Terminals"
    },
    {
      icon: "⚡",
      title: "Refined Products",
      description: "Gasoline, diesel, jet fuel, and specialty products. Refinery direct and trading desk connections.",
      background: "bg-gradient-to-br from-green-600 to-teal-700",
      metrics: "1M+ MT/Month"
    },
    {
      icon: "🏭",
      title: "Petrochemicals",
      description: "Ethylene, propylene, benzene, and chemical feedstocks. Direct producer and consumer links.",
      background: "bg-gradient-to-br from-purple-600 to-pink-700",
      metrics: "500+ Producers"
    },
    {
      icon: "🚢",
      title: "Maritime & Logistics",
      description: "Tanker chartering, storage solutions, and global logistics networks for energy commodities.",
      background: "bg-gradient-to-br from-slate-600 to-gray-800",
      metrics: "200+ Vessels"
    },
    {
      icon: "📊",
      title: "Market Intelligence",
      description: "Real-time pricing, market analysis, and trading signals from global energy markets.",
      background: "bg-gradient-to-br from-yellow-600 to-orange-700",
      metrics: "24/7 Analytics"
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
                  ENERGY COMMODITY TRADING
                </div>
                <h1 className="text-6xl md:text-8xl font-bold mb-8 leading-tight animate-fade-in-up">
                  {slide.title}
                </h1>
                <p className="text-xl md:text-2xl mb-10 text-gray-200 max-w-4xl mx-auto leading-relaxed animate-fade-in-up delay-300">
                  {slide.subtitle}
                </p>
                <div className="flex flex-col sm:flex-row gap-6 justify-center animate-fade-in-up delay-600">
                  <button className="bg-orange-600 hover:bg-orange-500 text-white px-10 py-4 rounded-lg text-xl font-bold transform hover:scale-105 transition-all duration-300 shadow-2xl">
                    {slide.cta}
                  </button>
                  <button className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-10 py-4 rounded-lg text-xl font-bold transform hover:scale-105 transition-all duration-300">
                    View Market Data
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

      {/* Energy Market Stats */}
      <section className="py-20 bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-orange-300">Global Energy Trading Network</h2>
            <p className="text-xl text-gray-300">Real-time market connectivity across major energy hubs</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 text-center">
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-orange-400 group-hover:text-orange-300">
                {stats.oil_gas_traders || '2,543'}+
              </div>
              <div className="text-blue-200 text-lg">Energy Traders</div>
              <div className="text-gray-400 text-sm mt-1">Verified Professionals</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-green-400 group-hover:text-green-300">
                $2.5B+
              </div>
              <div className="text-blue-200 text-lg">Daily Volume</div>
              <div className="text-gray-400 text-sm mt-1">Crude & Products</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-purple-400 group-hover:text-purple-300">
                156
              </div>
              <div className="text-blue-200 text-lg">Countries</div>
              <div className="text-gray-400 text-sm mt-1">Global Reach</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-yellow-400 group-hover:text-yellow-300">
                24/7
              </div>
              <div className="text-blue-200 text-lg">Trading Hours</div>
              <div className="text-gray-400 text-sm mt-1">Market Access</div>
            </div>
            <div className="group transform hover:scale-110 transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold mb-3 text-red-400 group-hover:text-red-300">
                85+
              </div>
              <div className="text-blue-200 text-lg">Refineries</div>
              <div className="text-gray-400 text-sm mt-1">Direct Access</div>
            </div>
          </div>
        </div>
      </section>

      {/* Energy Trading Features */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Complete Energy Trading Solution
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              From crude oil to refined products, natural gas to petrochemicals - access the world's largest 
              energy commodity trading network with real-time pricing and verified counterparties.
            </p>
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
                    <div className="text-sm font-semibold text-orange-200">VOLUME</div>
                    <div className="text-lg font-bold">{feature.metrics}</div>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-all duration-500 transform translate-y-4 group-hover:translate-y-0">
                    <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-lg font-semibold transition-all duration-300 border border-white/30">
                      Access Market →
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
              Live • Updated 30 sec ago
            </div>
          </div>
        </div>
      </section>

      {/* Industry CTA Section */}
      <section className="py-24 bg-gradient-to-r from-orange-600 via-red-600 to-orange-700 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-bold mb-8">
            Ready to Trade Energy?
          </h2>
          <p className="text-xl mb-12 max-w-3xl mx-auto leading-relaxed">
            Join the world's most trusted energy trading platform. Connect with refineries, 
            producers, and traders across oil, gas, and petrochemical markets.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button className="bg-white text-orange-600 px-10 py-5 rounded-lg text-xl font-bold hover:bg-gray-100 transform hover:scale-105 transition-all duration-300 shadow-2xl">
              Start Trading Now
            </button>
            <button className="border-3 border-white text-white px-10 py-5 rounded-lg text-xl font-bold hover:bg-white hover:text-orange-600 transform hover:scale-105 transition-all duration-300">
              Explore Premium
            </button>
          </div>
          <div className="mt-12 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold">$0</div>
              <div className="text-orange-200">Setup Fee</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">24/7</div>
              <div className="text-orange-200">Support</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">100%</div>
              <div className="text-orange-200">Verified</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default EnhancedHomePage;