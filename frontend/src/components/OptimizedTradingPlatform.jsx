import React, { lazy, Suspense, useMemo, useCallback, useState, useEffect } from 'react';
import { FixedSizeList as List } from 'react-window';

// Performance-optimized Loading Spinner
const LoadingSpinner = React.memo(() => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    <span className="ml-3 text-lg">Loading...</span>
  </div>
));

// Optimized Trade Item Component with memoization
const TradeItem = React.memo(({ trade, onSelect }) => {
  const handleClick = useCallback(() => {
    onSelect(trade.id);
  }, [trade.id, onSelect]);

  const priceColor = useMemo(() => {
    return trade.price_change > 0 ? 'text-green-600' : 'text-red-600';
  }, [trade.price_change]);

  return (
    <div 
      className="border rounded-lg p-4 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={handleClick}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-lg">{trade.title}</h3>
          <p className="text-gray-600">{trade.commodity} • {trade.quantity} {trade.unit}</p>
          <p className="text-sm text-gray-500">{trade.location}</p>
        </div>
        <div className="text-right">
          <p className={`font-bold ${priceColor}`}>${trade.price}</p>
          <p className="text-xs text-gray-500">{trade.trading_hub}</p>
        </div>
      </div>
    </div>
  );
});

// Virtualized Trade List for Large Datasets
const VirtualizedTradeList = React.memo(({ trades, onTradeSelect, height = 600 }) => {
  const Row = useCallback(({ index, style }) => (
    <div style={style} className="px-2 py-1">
      <TradeItem 
        trade={trades[index]} 
        onSelect={onTradeSelect}
      />
    </div>
  ), [trades, onTradeSelect]);

  if (!trades || trades.length === 0) {
    return <div className="text-center py-8">No trades available</div>;
  }

  return (
    <List
      height={height}
      itemCount={trades.length}
      itemSize={120}
      width="100%"
      className="border rounded-lg"
    >
      {Row}
    </List>
  );
});

// Optimized Market Analysis Component
const MarketAnalysis = React.memo(({ trades, filters }) => {
  // Memoized expensive calculations
  const filteredTrades = useMemo(() => {
    if (!trades || !filters) return [];
    
    return trades.filter(trade => {
      const matchesCommodity = !filters.commodity || trade.commodity === filters.commodity;
      const matchesLocation = !filters.location || trade.location.toLowerCase().includes(filters.location.toLowerCase());
      const matchesDateRange = !filters.startDate || new Date(trade.date) >= new Date(filters.startDate);
      const matchesPriceRange = (!filters.minPrice || trade.price >= filters.minPrice) &&
                               (!filters.maxPrice || trade.price <= filters.maxPrice);
      
      return matchesCommodity && matchesLocation && matchesDateRange && matchesPriceRange;
    });
  }, [trades, filters]);

  const marketStats = useMemo(() => {
    if (!filteredTrades.length) return { avgPrice: 0, totalVolume: 0, tradeCount: 0 };
    
    const totalPrice = filteredTrades.reduce((sum, trade) => sum + trade.price, 0);
    const totalVolume = filteredTrades.reduce((sum, trade) => sum + trade.quantity, 0);
    
    return {
      avgPrice: totalPrice / filteredTrades.length,
      totalVolume,
      tradeCount: filteredTrades.length
    };
  }, [filteredTrades]);

  return (
    <div className="space-y-6">
      {/* Market Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-800">Average Price</h3>
          <p className="text-2xl font-bold text-blue-600">
            ${marketStats.avgPrice.toFixed(2)}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="font-semibold text-green-800">Total Volume</h3>
          <p className="text-2xl font-bold text-green-600">
            {marketStats.totalVolume.toLocaleString()}
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="font-semibold text-purple-800">Active Trades</h3>
          <p className="text-2xl font-bold text-purple-600">
            {marketStats.tradeCount}
          </p>
        </div>
      </div>

      {/* Virtualized Trade List */}
      <VirtualizedTradeList 
        trades={filteredTrades}
        onTradeSelect={(id) => console.log('Selected trade:', id)}
      />
    </div>
  );
});

// Optimized Filter Component with debounced input
const TradeFilters = React.memo(({ filters, onFilterChange }) => {
  const [localFilters, setLocalFilters] = useState(filters);

  // Debounced filter update
  useEffect(() => {
    const timer = setTimeout(() => {
      onFilterChange(localFilters);
    }, 300);

    return () => clearTimeout(timer);
  }, [localFilters, onFilterChange]);

  const handleInputChange = useCallback((field, value) => {
    setLocalFilters(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleCommodityChange = useCallback((e) => {
    handleInputChange('commodity', e.target.value);
  }, [handleInputChange]);

  const handleLocationChange = useCallback((e) => {
    handleInputChange('location', e.target.value);
  }, [handleInputChange]);

  const handlePriceChange = useCallback((field) => (e) => {
    const value = parseFloat(e.target.value) || 0;
    handleInputChange(field, value);
  }, [handleInputChange]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
      <h3 className="text-lg font-semibold mb-4">Filter Trades</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Commodity</label>
          <select
            value={localFilters.commodity || ''}
            onChange={handleCommodityChange}
            className="w-full p-2 border rounded-md"
          >
            <option value="">All Commodities</option>
            <option value="crude_oil">Crude Oil</option>
            <option value="natural_gas">Natural Gas</option>
            <option value="lng">LNG</option>
            <option value="gasoline">Gasoline</option>
            <option value="diesel">Diesel</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Location</label>
          <input
            type="text"
            value={localFilters.location || ''}
            onChange={handleLocationChange}
            placeholder="Enter location"
            className="w-full p-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Min Price ($)</label>
          <input
            type="number"
            value={localFilters.minPrice || ''}
            onChange={handlePriceChange('minPrice')}
            placeholder="0"
            className="w-full p-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Max Price ($)</label>
          <input
            type="number"
            value={localFilters.maxPrice || ''}
            onChange={handlePriceChange('maxPrice')}
            placeholder="No limit"
            className="w-full p-2 border rounded-md"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => {
            setLocalFilters({});
            onFilterChange({});
          }}
          className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
});

// Main optimized trading platform component
const OptimizedTradingPlatform = React.memo(() => {
  const [trades, setTrades] = useState([]);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch trades with error handling
  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setTrades(data.listings || []);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch trades:', err);
        setError('Failed to load trading data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, []);

  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Oil & Gas Trading Platform
        </h1>
        <p className="text-gray-600">
          Connect with traders worldwide for oil and gas commodities
        </p>
      </div>

      <TradeFilters 
        filters={filters} 
        onFilterChange={handleFilterChange} 
      />

      <MarketAnalysis 
        trades={trades} 
        filters={filters} 
      />
    </div>
  );
});

// Export performance-optimized components
export {
  OptimizedTradingPlatform,
  VirtualizedTradeList,
  MarketAnalysis,
  TradeFilters,
  LoadingSpinner
};

export default OptimizedTradingPlatform;