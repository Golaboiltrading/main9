import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Real-time WebSocket connection for market data
const useWebSocketMarketData = () => {
  const [metrics, setMetrics] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8001/ws/market-data';
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        setConnectionStatus('Connected');
        console.log('WebSocket connected for market data');
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'MARKET_UPDATE') {
            setMetrics(prev => ({
              ...prev,
              [data.commodity]: {
                ...prev[data.commodity],
                ...data.metrics,
                timestamp: new Date().toISOString(),
                trend: calculateTrend(prev[data.commodity], data.metrics)
              }
            }));
          } else if (data.type === 'TRADING_ACTIVITY') {
            setMetrics(prev => ({
              ...prev,
              trading_activity: data.activity
            }));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.onclose = () => {
        setConnectionStatus('Disconnected');
        console.log('WebSocket disconnected, attempting to reconnect...');
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      websocket.onerror = (error) => {
        setConnectionStatus('Error');
        console.error('WebSocket error:', error);
      };

      setWs(websocket);
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const calculateTrend = (previous, current) => {
    if (!previous || !previous.price || !current.price) return 'neutral';
    const change = current.price - previous.price;
    return change > 0 ? 'up' : change < 0 ? 'down' : 'neutral';
  };

  return { metrics, connectionStatus };
};

// Market Trends Component
const MarketTrends = React.memo(({ data }) => {
  const chartData = useMemo(() => {
    const commodities = Object.keys(data);
    const prices = commodities.map(commodity => data[commodity]?.price || 0);
    const volumes = commodities.map(commodity => data[commodity]?.volume || 0);

    return {
      labels: commodities.map(c => c.replace('_', ' ').toUpperCase()),
      datasets: [
        {
          label: 'Price ($)',
          data: prices,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          yAxisID: 'y',
          tension: 0.4,
          fill: true,
        },
        {
          label: 'Volume (K)',
          data: volumes.map(v => v / 1000),
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          yAxisID: 'y1',
          tension: 0.4,
        },
      ],
    };
  }, [data]);

  const options = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      title: {
        display: true,
        text: 'Real-time Market Trends',
        font: { size: 16, weight: 'bold' }
      },
      legend: {
        position: 'top',
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Commodities'
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Price ($)'
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Volume (Thousands)'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <Line data={chartData} options={options} />
    </div>
  );
});

// Profit Calculator Component
const ProfitCalculator = React.memo(() => {
  const [calculation, setCalculation] = useState({
    commodity: 'crude_oil',
    quantity: 1000,
    buyPrice: 75.50,
    sellPrice: 76.00,
    currency: 'USD'
  });

  const profitMetrics = useMemo(() => {
    const { quantity, buyPrice, sellPrice } = calculation;
    const totalCost = quantity * buyPrice;
    const totalRevenue = quantity * sellPrice;
    const grossProfit = totalRevenue - totalCost;
    const profitMargin = totalCost > 0 ? (grossProfit / totalCost) * 100 : 0;
    const roi = totalCost > 0 ? (grossProfit / totalCost) * 100 : 0;

    return {
      totalCost,
      totalRevenue,
      grossProfit,
      profitMargin,
      roi
    };
  }, [calculation]);

  const handleInputChange = useCallback((field, value) => {
    setCalculation(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }));
  }, []);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Profit Calculator</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Commodity
          </label>
          <select
            value={calculation.commodity}
            onChange={(e) => setCalculation(prev => ({ ...prev, commodity: e.target.value }))}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="crude_oil">Crude Oil</option>
            <option value="natural_gas">Natural Gas</option>
            <option value="lng">LNG</option>
            <option value="gasoline">Gasoline</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Quantity (barrels)
          </label>
          <input
            type="number"
            value={calculation.quantity}
            onChange={(e) => handleInputChange('quantity', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Buy Price ($)
          </label>
          <input
            type="number"
            step="0.01"
            value={calculation.buyPrice}
            onChange={(e) => handleInputChange('buyPrice', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sell Price ($)
          </label>
          <input
            type="number"
            step="0.01"
            value={calculation.sellPrice}
            onChange={(e) => handleInputChange('sellPrice', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-semibold text-blue-800">Total Cost</h4>
          <p className="text-2xl font-bold text-blue-600">
            ${profitMetrics.totalCost.toLocaleString('en-US', { 
              minimumFractionDigits: 2, 
              maximumFractionDigits: 2 
            })}
          </p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800">Gross Profit</h4>
          <p className={`text-2xl font-bold ${
            profitMetrics.grossProfit >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            ${profitMetrics.grossProfit.toLocaleString('en-US', { 
              minimumFractionDigits: 2, 
              maximumFractionDigits: 2 
            })}
          </p>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <h4 className="font-semibold text-purple-800">ROI</h4>
          <p className={`text-2xl font-bold ${
            profitMetrics.roi >= 0 ? 'text-purple-600' : 'text-red-600'
          }`}>
            {profitMetrics.roi.toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  );
});

// Risk Analysis Component
const RiskAnalysis = React.memo(({ data }) => {
  const riskMetrics = useMemo(() => {
    const commodities = Object.keys(data);
    const volatilities = commodities.map(commodity => {
      const price = data[commodity]?.price || 0;
      const volume = data[commodity]?.volume || 0;
      // Simple volatility calculation based on price and volume
      return price > 0 ? (Math.abs(price - 75) / 75) * 100 + (volume < 1000 ? 20 : 0) : 0;
    });

    return {
      commodities: commodities.map(c => c.replace('_', ' ').toUpperCase()),
      volatilities,
      averageVolatility: volatilities.reduce((a, b) => a + b, 0) / volatilities.length || 0
    };
  }, [data]);

  const riskChartData = {
    labels: riskMetrics.commodities,
    datasets: [
      {
        label: 'Risk Level (%)',
        data: riskMetrics.volatilities,
        backgroundColor: riskMetrics.volatilities.map(vol => {
          if (vol < 10) return 'rgba(16, 185, 129, 0.8)'; // Low risk - green
          if (vol < 25) return 'rgba(245, 158, 11, 0.8)'; // Medium risk - yellow
          return 'rgba(239, 68, 68, 0.8)'; // High risk - red
        }),
        borderColor: riskMetrics.volatilities.map(vol => {
          if (vol < 10) return 'rgb(16, 185, 129)';
          if (vol < 25) return 'rgb(245, 158, 11)';
          return 'rgb(239, 68, 68)';
        }),
        borderWidth: 2,
      },
    ],
  };

  const riskOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Risk Analysis by Commodity',
        font: { size: 16, weight: 'bold' }
      },
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Risk Level (%)'
        }
      }
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">Risk Analysis</h3>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
              Low (&lt;10%)
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mr-1"></div>
              Medium (10-25%)
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-1"></div>
              High (&gt;25%)
            </div>
          </div>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-600">
            Average Portfolio Risk: 
            <span className={`ml-2 font-semibold ${
              riskMetrics.averageVolatility < 10 ? 'text-green-600' :
              riskMetrics.averageVolatility < 25 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {riskMetrics.averageVolatility.toFixed(1)}%
            </span>
          </p>
        </div>
      </div>
      
      <Bar data={riskChartData} options={riskOptions} />
    </div>
  );
});

// Main Trading Analytics Dashboard
const TradingAnalytics = React.memo(() => {
  const { metrics, connectionStatus } = useWebSocketMarketData();
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'trends', name: 'Market Trends', icon: '📈' },
    { id: 'calculator', name: 'Profit Calculator', icon: '💰' },
    { id: 'risk', name: 'Risk Analysis', icon: '⚠️' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Trading Analytics Dashboard</h1>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'Connected' ? 'bg-green-500' : 
                connectionStatus === 'Connecting...' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">{connectionStatus}</span>
            </div>
          </div>
          <p className="text-gray-600 mt-1">Real-time market data and trading insights</p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              <MarketTrends data={metrics} />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ProfitCalculator />
                <RiskAnalysis data={metrics} />
              </div>
            </>
          )}
          
          {activeTab === 'trends' && (
            <MarketTrends data={metrics} />
          )}
          
          {activeTab === 'calculator' && (
            <ProfitCalculator />
          )}
          
          {activeTab === 'risk' && (
            <RiskAnalysis data={metrics} />
          )}
        </div>
      </div>
    </div>
  );
});

export default TradingAnalytics;
export { MarketTrends, ProfitCalculator, RiskAnalysis };