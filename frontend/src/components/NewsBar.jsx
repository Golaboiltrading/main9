import React, { useState, useEffect } from 'react';

export const NewsBar = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetchNews();
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % news.length);
    }, 5000); // Rotate news every 5 seconds
    
    return () => clearInterval(interval);
  }, [news.length]);

  const fetchNews = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/news/oil-gas`);
      const data = await response.json();
      setNews(data.articles || mockNews);
    } catch (error) {
      console.error('Error fetching news:', error);
      setNews(mockNews);
    } finally {
      setLoading(false);
    }
  };

  // Mock news data for immediate display
  const mockNews = [
    {
      title: "Oil Prices Rise 3% on Supply Concerns",
      summary: "Crude oil futures gained after reports of production cuts from major exporters...",
      source: "Energy News",
      time: "2 hours ago",
      category: "Market",
      sentiment: "positive"
    },
    {
      title: "Natural Gas Demand Surges in Winter Season",
      summary: "European gas prices hit seasonal highs as winter demand increases across the region...",
      source: "Gas Daily",
      time: "4 hours ago",
      category: "Natural Gas",
      sentiment: "positive"
    },
    {
      title: "New LNG Terminal Opens in Texas",
      summary: "Major infrastructure development boosts US export capacity by 15 million tons per year...",
      source: "LNG Journal",
      time: "6 hours ago",
      category: "Infrastructure",
      sentiment: "positive"
    },
    {
      title: "OPEC+ Meeting Scheduled for Next Week",
      summary: "Oil ministers to discuss production quotas amid changing market conditions...",
      source: "OPEC News",
      time: "8 hours ago",
      category: "Policy",
      sentiment: "neutral"
    },
    {
      title: "Renewable Energy Investment Hits Record High",
      summary: "Global investment in clean energy technologies reaches $2.8 trillion in 2024...",
      source: "Energy Transition",
      time: "1 day ago",
      category: "Renewables",
      sentiment: "positive"
    },
    {
      title: "Geopolitical Tensions Affect Oil Trade Routes",
      summary: "Shipping companies adjust routes as regional conflicts impact key maritime passages...",
      source: "Maritime Oil",
      time: "1 day ago",
      category: "Geopolitics",
      sentiment: "negative"
    }
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4">
        <h3 className="text-lg font-bold flex items-center">
          <span className="mr-2">📰</span>
          Industry News
        </h3>
      </div>

      {/* Current News Item */}
      <div className="p-4 border-b">
        {news.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getCategoryColor(news[currentIndex].category)}`}>
                {news[currentIndex].category}
              </span>
              <span className={`text-sm ${getSentimentColor(news[currentIndex].sentiment)}`}>
                {getSentimentIcon(news[currentIndex].sentiment)}
              </span>
            </div>
            
            <h4 className="font-semibold text-gray-900 text-sm leading-snug">
              {news[currentIndex].title}
            </h4>
            
            <p className="text-gray-600 text-xs leading-relaxed">
              {news[currentIndex].summary}
            </p>
            
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{news[currentIndex].source}</span>
              <span>{news[currentIndex].time}</span>
            </div>
          </div>
        )}
      </div>

      {/* News List */}
      <div className="max-h-96 overflow-y-auto">
        {news.slice(1, 6).map((item, index) => (
          <div 
            key={index}
            className="p-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => setCurrentIndex(index + 1)}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getCategoryColor(item.category)}`}>
                {item.category}
              </span>
              <span className="text-xs text-gray-500">{item.time}</span>
            </div>
            
            <h5 className="font-medium text-gray-900 text-sm leading-tight mb-1">
              {item.title}
            </h5>
            
            <p className="text-gray-600 text-xs leading-relaxed line-clamp-2">
              {item.summary}
            </p>
          </div>
        ))}
      </div>

      {/* Market Indicators */}
      <div className="bg-gray-50 p-4">
        <h4 className="font-semibold text-gray-900 text-sm mb-3">Market Indicators</h4>
        <div className="space-y-2">
          <MarketIndicator name="WTI Crude" value="$75.25" change="+1.2%" positive={true} />
          <MarketIndicator name="Brent Crude" value="$78.90" change="+0.8%" positive={true} />
          <MarketIndicator name="Natural Gas" value="$2.85" change="-0.5%" positive={false} />
          <MarketIndicator name="Gasoline" value="$2.15" change="+2.1%" positive={true} />
        </div>
      </div>

      {/* Footer */}
      <div className="bg-blue-50 p-3 text-center">
        <button className="text-blue-600 text-xs font-semibold hover:text-blue-800 transition-colors">
          View All News →
        </button>
      </div>
    </div>
  );
};

const MarketIndicator = ({ name, value, change, positive }) => (
  <div className="flex items-center justify-between text-xs">
    <span className="text-gray-700 font-medium">{name}</span>
    <div className="flex items-center space-x-2">
      <span className="font-semibold">{value}</span>
      <span className={`font-semibold ${positive ? 'text-green-600' : 'text-red-600'}`}>
        {change}
      </span>
    </div>
  </div>
);

const getCategoryColor = (category) => {
  const colors = {
    'Market': 'bg-blue-100 text-blue-800',
    'Natural Gas': 'bg-green-100 text-green-800',
    'Infrastructure': 'bg-purple-100 text-purple-800',
    'Policy': 'bg-yellow-100 text-yellow-800',
    'Renewables': 'bg-emerald-100 text-emerald-800',
    'Geopolitics': 'bg-red-100 text-red-800'
  };
  return colors[category] || 'bg-gray-100 text-gray-800';
};

const getSentimentColor = (sentiment) => {
  const colors = {
    'positive': 'text-green-600',
    'negative': 'text-red-600',
    'neutral': 'text-gray-600'
  };
  return colors[sentiment] || 'text-gray-600';
};

const getSentimentIcon = (sentiment) => {
  const icons = {
    'positive': '📈',
    'negative': '📉',
    'neutral': '📊'
  };
  return icons[sentiment] || '📊';
};

export default NewsBar;