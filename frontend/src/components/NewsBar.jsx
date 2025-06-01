import React, { useState, useEffect } from 'react';

const NewsBar = () => {
  const [news, setNews] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [marketData, setMarketData] = useState({});

  // Sample news data with sentiment analysis
  const sampleNews = [
    {
      id: 1,
      title: "Oil Prices Rise on Supply Concerns",
      category: "Market",
      sentiment: "positive",
      timestamp: "2 hours ago",
      impact: "high"
    },
    {
      id: 2,
      title: "New LNG Terminal Opens in Gulf Coast",
      category: "Infrastructure", 
      sentiment: "positive",
      timestamp: "4 hours ago",
      impact: "medium"
    },
    {
      id: 3,
      title: "OPEC+ Considers Production Cuts",
      category: "Policy",
      sentiment: "neutral",
      timestamp: "6 hours ago",
      impact: "high"
    },
    {
      id: 4,
      title: "Natural Gas Demand Surges in Asia",
      category: "Market",
      sentiment: "positive", 
      timestamp: "8 hours ago",
      impact: "medium"
    },
    {
      id: 5,
      title: "Crude Oil Inventories Fall Sharply",
      category: "Market",
      sentiment: "positive",
      timestamp: "10 hours ago", 
      impact: "high"
    }
  ];

  useEffect(() => {
    // Simulate fetching news data
    setNews(sampleNews);
    
    // Simulate fetching market data
    setMarketData({
      wti: { price: 75.25, change: 1.2 },
      brent: { price: 79.50, change: 0.8 },
      naturalGas: { price: 2.85, change: -0.5 },
      lastUpdate: new Date().toLocaleTimeString()
    });

    // Auto-rotate news every 5 seconds
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % sampleNews.length);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '📈';
      case 'negative': return '📉';
      default: return '📊';
    }
  };

  const getImpactBadge = (impact) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800', 
      low: 'bg-green-100 text-green-800'
    };
    return `px-2 py-1 rounded-full text-xs font-semibold ${colors[impact]}`;
  };

  return (
    <div className="bg-gray-900 text-white">
      {/* Market Indicators Bar */}
      <div className="border-b border-gray-700 py-2">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-between items-center text-sm">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">WTI:</span>
                <span className="font-bold">${marketData.wti?.price}</span>
                <span className={marketData.wti?.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {marketData.wti?.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.wti?.change)}%
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">Brent:</span>
                <span className="font-bold">${marketData.brent?.price}</span>
                <span className={marketData.brent?.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {marketData.brent?.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.brent?.change)}%
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">Natural Gas:</span>
                <span className="font-bold">${marketData.naturalGas?.price}</span>
                <span className={marketData.naturalGas?.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {marketData.naturalGas?.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.naturalGas?.change)}%
                </span>
              </div>
            </div>
            <div className="text-gray-400 text-xs">
              Live • Updated {marketData.lastUpdate}
            </div>
          </div>
        </div>
      </div>

      {/* News Ticker */}
      <div className="py-3">
        <div className="container mx-auto px-4">
          <div className="flex items-center">
            <div className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-bold mr-4">
              BREAKING
            </div>
            <div className="flex-1 overflow-hidden">
              {news.length > 0 && (
                <div className="flex items-center animate-fade-in-out">
                  <span className="mr-2">
                    {getSentimentIcon(news[currentIndex]?.sentiment)}
                  </span>
                  <span className="font-semibold mr-2">
                    {news[currentIndex]?.title}
                  </span>
                  <span className={`mr-2 ${getImpactBadge(news[currentIndex]?.impact)}`}>
                    {news[currentIndex]?.impact?.toUpperCase()}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {news[currentIndex]?.timestamp}
                  </span>
                </div>
              )}
            </div>
            <button className="bg-blue-600 hover:bg-blue-500 px-4 py-1 rounded text-sm font-semibold transition-colors">
              View All News
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sidebar News Component
export const NewsSidebar = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [news, setNews] = useState([]);

  const categories = ['all', 'market', 'infrastructure', 'policy', 'technology'];
  
  const sampleNews = [
    {
      id: 1,
      title: "Oil Prices Surge on Middle East Tensions",
      excerpt: "Crude oil futures jumped 3% as geopolitical concerns mount in the region affecting major supply routes.",
      category: "market",
      sentiment: "positive",
      timestamp: "1 hour ago",
      image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop"
    },
    {
      id: 2,
      title: "New LNG Export Terminal Approved",
      excerpt: "Major energy company receives approval for $12 billion LNG export facility on the Gulf Coast.",
      category: "infrastructure", 
      sentiment: "positive",
      timestamp: "3 hours ago",
      image: "https://images.unsplash.com/photo-1518709268805-4e9042af2a73?w=300&h=200&fit=crop"
    },
    {
      id: 3,
      title: "OPEC+ Meeting Results in Production Freeze",
      excerpt: "Oil cartel maintains current production levels despite pressure from consuming nations.",
      category: "policy",
      sentiment: "neutral", 
      timestamp: "5 hours ago",
      image: "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=300&h=200&fit=crop"
    },
    {
      id: 4,
      title: "AI-Powered Trading Platform Launched",
      excerpt: "Revolutionary AI system promises to transform oil and gas commodity trading with predictive analytics.",
      category: "technology",
      sentiment: "positive",
      timestamp: "7 hours ago", 
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=300&h=200&fit=crop"
    },
    {
      id: 5,
      title: "Natural Gas Demand Peaks in Europe",
      excerpt: "European gas demand reaches record highs as winter approaches and supply concerns persist.",
      category: "market",
      sentiment: "positive",
      timestamp: "9 hours ago",
      image: "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=300&h=200&fit=crop"
    }
  ];

  useEffect(() => {
    setNews(sampleNews);
  }, []);

  const filteredNews = selectedCategory === 'all' 
    ? news 
    : news.filter(item => item.category === selectedCategory);

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return <span className="text-green-500">📈</span>;
      case 'negative': return <span className="text-red-500">📉</span>;
      default: return <span className="text-yellow-500">📊</span>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Industry News</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-500">Live</span>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>

      {/* News List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {filteredNews.map((article) => (
          <div key={article.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex space-x-3">
              <img 
                src={article.image} 
                alt={article.title}
                className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500 uppercase tracking-wide">
                    {article.category}
                  </span>
                  {getSentimentIcon(article.sentiment)}
                </div>
                <h3 className="text-sm font-semibold text-gray-900 leading-tight mb-1">
                  {article.title}
                </h3>
                <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                  {article.excerpt}
                </p>
                <div className="text-xs text-gray-400">
                  {article.timestamp}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View More Button */}
      <div className="mt-4 text-center">
        <button className="text-blue-600 hover:text-blue-500 text-sm font-medium">
          View All Industry News →
        </button>
      </div>
    </div>
  );
};

export default NewsBar;