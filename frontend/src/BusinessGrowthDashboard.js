import React, { useState, useEffect } from 'react';

const BusinessGrowthDashboard = ({ token, API_BASE_URL }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [acquisitionData, setAcquisitionData] = useState({});
  const [contentData, setContentData] = useState({});
  const [conversionMetrics, setConversionMetrics] = useState({});
  const [marketIntelligence, setMarketIntelligence] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBusinessData();
    fetchMarketIntelligence();
  }, []);

  const fetchBusinessData = async () => {
    setLoading(true);
    try {
      // Fetch user acquisition dashboard
      const acquisitionResponse = await fetch(`${API_BASE_URL}/api/acquisition/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (acquisitionResponse.ok) {
        const data = await acquisitionResponse.json();
        setAcquisitionData(data);
      }

      // Fetch content marketing dashboard
      const contentResponse = await fetch(`${API_BASE_URL}/api/content/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (contentResponse.ok) {
        const data = await contentResponse.json();
        setContentData(data);
      }

      // Fetch conversion metrics
      const metricsResponse = await fetch(`${API_BASE_URL}/api/referrals/metrics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (metricsResponse.ok) {
        const data = await metricsResponse.json();
        setConversionMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching business data:', error);
    }
    setLoading(false);
  };

  const fetchMarketIntelligence = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/market-intelligence`);
      if (response.ok) {
        const data = await response.json();
        setMarketIntelligence(data);
      }
    } catch (error) {
      console.error('Error fetching market intelligence:', error);
    }
  };

  const createReferralProgram = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/referrals/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ referral_type: 'standard' })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Referral program created! Your code: ${data.referral_code}`);
        fetchBusinessData();
      }
    } catch (error) {
      console.error('Error creating referral program:', error);
    }
  };

  const OverviewTab = () => (
    <div>
      <h3 className="text-xl font-bold mb-6">Business Growth Overview</h3>
      
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-blue-900">Monthly Revenue</h4>
          <div className="text-3xl font-bold text-blue-600 mt-2">$12,450</div>
          <div className="text-sm text-green-600 mt-1">+23% from last month</div>
        </div>
        
        <div className="bg-green-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-green-900">Active Users</h4>
          <div className="text-3xl font-bold text-green-600 mt-2">{acquisitionData.conversion_funnel?.trial_signups || 0}</div>
          <div className="text-sm text-green-600 mt-1">+{acquisitionData.growth_projections?.weekly_signups || 0} this week</div>
        </div>
        
        <div className="bg-purple-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-purple-900">Conversion Rate</h4>
          <div className="text-3xl font-bold text-purple-600 mt-2">{conversionMetrics.lead_metrics?.conversion_rate || 0}%</div>
          <div className="text-sm text-purple-600 mt-1">Industry leading</div>
        </div>
        
        <div className="bg-orange-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-orange-900">Premium Users</h4>
          <div className="text-3xl font-bold text-orange-600 mt-2">{acquisitionData.conversion_funnel?.paid_conversions || 0}</div>
          <div className="text-sm text-orange-600 mt-1">35% of total users</div>
        </div>
      </div>

      {/* Market Intelligence */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <h4 className="text-lg font-semibold mb-4">📊 Market Intelligence</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">Oil Markets</h5>
            {marketIntelligence.market_overview?.oil_markets && Object.entries(marketIntelligence.market_overview.oil_markets).map(([market, data]) => (
              <div key={market} className="flex justify-between py-1">
                <span className="capitalize">{market.replace('_', ' ')}</span>
                <span className={`font-semibold ${data.trend === 'bullish' ? 'text-green-600' : data.trend === 'bearish' ? 'text-red-600' : 'text-gray-600'}`}>
                  ${data.price}
                </span>
              </div>
            ))}
          </div>
          
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">Trading Opportunities</h5>
            {marketIntelligence.trading_opportunities?.slice(0, 2).map((opp, index) => (
              <div key={index} className="mb-3 p-3 bg-gray-50 rounded">
                <div className="font-semibold text-sm">{opp.market}</div>
                <div className="text-xs text-gray-600">{opp.opportunity}</div>
                <div className="text-xs text-blue-600">Confidence: {opp.confidence}</div>
              </div>
            ))}
          </div>
          
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">Key Events This Week</h5>
            {marketIntelligence.weekly_outlook?.key_events?.slice(0, 3).map((event, index) => (
              <div key={index} className="text-sm text-gray-600 py-1">• {event}</div>
            ))}
          </div>
        </div>
      </div>

      {/* Growth Projections */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-lg font-semibold mb-4">📈 Growth Projections</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="font-semibold text-gray-700 mb-3">User Acquisition Forecast</h5>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>This Month Target:</span>
                <span className="font-semibold">{acquisitionData.growth_projections?.projected_monthly || 0} users</span>
              </div>
              <div className="flex justify-between">
                <span>Current Progress:</span>
                <span className="font-semibold text-green-600">67%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{width: '67%'}}></div>
              </div>
            </div>
          </div>
          
          <div>
            <h5 className="font-semibold text-gray-700 mb-3">Revenue Forecast</h5>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Monthly Target:</span>
                <span className="font-semibold">$15,000</span>
              </div>
              <div className="flex justify-between">
                <span>Current Progress:</span>
                <span className="font-semibold text-blue-600">83%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{width: '83%'}}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const AcquisitionTab = () => (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">User Acquisition</h3>
        <button
          onClick={createReferralProgram}
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg"
        >
          Create Referral Program
        </button>
      </div>

      {/* Acquisition Funnel */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <h4 className="text-lg font-semibold mb-4">Conversion Funnel</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{acquisitionData.conversion_funnel?.website_visitors || 0}</div>
            <div className="text-sm text-blue-900">Website Visitors</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{acquisitionData.conversion_funnel?.leads_generated || 0}</div>
            <div className="text-sm text-green-900">Leads Generated</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{acquisitionData.conversion_funnel?.trial_signups || 0}</div>
            <div className="text-sm text-purple-900">Trial Signups</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{acquisitionData.conversion_funnel?.paid_conversions || 0}</div>
            <div className="text-sm text-orange-900">Paid Conversions</div>
          </div>
        </div>
      </div>

      {/* Traffic Sources */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold mb-4">Traffic Sources</h4>
          {acquisitionData.traffic_sources?.map((source, index) => (
            <div key={index} className="flex justify-between items-center py-3 border-b last:border-b-0">
              <div>
                <div className="font-semibold capitalize">{source._id || 'Direct'}</div>
                <div className="text-sm text-gray-600">{source.conversions} conversions</div>
              </div>
              <div className="text-right">
                <div className="font-bold">{source.leads}</div>
                <div className="text-sm text-gray-600">leads</div>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold mb-4">Top Referrers</h4>
          {acquisitionData.top_referrers?.map((referrer, index) => (
            <div key={index} className="flex justify-between items-center py-3 border-b last:border-b-0">
              <div>
                <div className="font-semibold">{referrer.company_name || 'Anonymous'}</div>
                <div className="text-sm text-gray-600">Code: {referrer.referral_code}</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-green-600">${referrer.total_rewards_earned || 0}</div>
                <div className="text-sm text-gray-600">{referrer.successful_conversions} conversions</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ContentMarketingTab = () => (
    <div>
      <h3 className="text-xl font-bold mb-6">Content Marketing</h3>

      {/* Content Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-blue-900">Articles Published</h4>
          <div className="text-3xl font-bold text-blue-600 mt-2">{contentData.content_production?.articles_published || 0}</div>
          <div className="text-sm text-blue-600 mt-1">This month</div>
        </div>
        
        <div className="bg-green-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-green-900">Total Views</h4>
          <div className="text-3xl font-bold text-green-600 mt-2">{contentData.content_production?.total_content_views || 0}</div>
          <div className="text-sm text-green-600 mt-1">All content</div>
        </div>
        
        <div className="bg-purple-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-purple-900">Leads Generated</h4>
          <div className="text-3xl font-bold text-purple-600 mt-2">{contentData.lead_generation?.content_leads_30d || 0}</div>
          <div className="text-sm text-purple-600 mt-1">From content</div>
        </div>
        
        <div className="bg-orange-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-orange-900">Conversion Rate</h4>
          <div className="text-3xl font-bold text-orange-600 mt-2">{contentData.lead_generation?.conversion_rate || 0}%</div>
          <div className="text-sm text-orange-600 mt-1">Content to leads</div>
        </div>
      </div>

      {/* SEO Performance */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <h4 className="text-lg font-semibold mb-4">SEO Performance</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{contentData.seo_performance?.target_keywords || 0}</div>
            <div className="text-sm text-gray-600">Target Keywords</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{contentData.seo_performance?.top_10_rankings || 0}</div>
            <div className="text-sm text-gray-600">Top 10 Rankings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{contentData.seo_performance?.organic_traffic_growth || 0}%</div>
            <div className="text-sm text-gray-600">Traffic Growth</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{contentData.seo_performance?.avg_position || 0}</div>
            <div className="text-sm text-gray-600">Avg Position</div>
          </div>
        </div>
      </div>

      {/* Upcoming Content Calendar */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-lg font-semibold mb-4">📅 Upcoming Content</h4>
        <div className="space-y-3">
          {contentData.upcoming_content?.map((content, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <div className="font-semibold">{content}</div>
                <div className="text-sm text-gray-600">Scheduled for publication</div>
              </div>
              <span className="text-sm text-blue-600 font-semibold">Coming Soon</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const AnalyticsTab = () => (
    <div>
      <h3 className="text-xl font-bold mb-6">Business Analytics</h3>

      {/* ROI Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-green-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-green-900">Customer LTV</h4>
          <div className="text-3xl font-bold text-green-600 mt-2">${conversionMetrics.acquisition_metrics?.customer_lifetime_value || 0}</div>
          <div className="text-sm text-green-600 mt-1">Average lifetime value</div>
        </div>
        
        <div className="bg-blue-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-blue-900">Acquisition Cost</h4>
          <div className="text-3xl font-bold text-blue-600 mt-2">${conversionMetrics.acquisition_metrics?.customer_acquisition_cost || 0}</div>
          <div className="text-sm text-blue-600 mt-1">Cost per customer</div>
        </div>
        
        <div className="bg-purple-50 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-purple-900">LTV:CAC Ratio</h4>
          <div className="text-3xl font-bold text-purple-600 mt-2">{conversionMetrics.acquisition_metrics?.ltv_cac_ratio || 0}:1</div>
          <div className="text-sm text-purple-600 mt-1">{conversionMetrics.roi_analysis?.marketing_efficiency || 'Good'} efficiency</div>
        </div>
      </div>

      {/* Business Intelligence */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-lg font-semibold mb-4">📊 Business Intelligence</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="font-semibold text-gray-700 mb-3">Growth Metrics</h5>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Monthly Growth Rate:</span>
                <span className="font-semibold text-green-600">+23%</span>
              </div>
              <div className="flex justify-between">
                <span>User Retention Rate:</span>
                <span className="font-semibold text-blue-600">85%</span>
              </div>
              <div className="flex justify-between">
                <span>Premium Conversion:</span>
                <span className="font-semibold text-purple-600">35%</span>
              </div>
            </div>
          </div>
          
          <div>
            <h5 className="font-semibold text-gray-700 mb-3">Market Position</h5>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Market Share:</span>
                <span className="font-semibold text-orange-600">12%</span>
              </div>
              <div className="flex justify-between">
                <span>Brand Authority:</span>
                <span className="font-semibold text-green-600">High</span>
              </div>
              <div className="flex justify-between">
                <span>Industry Ranking:</span>
                <span className="font-semibold text-blue-600">#3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">🚀 Business Growth Dashboard</h1>
        
        <div className="bg-white rounded-lg shadow-lg">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('acquisition')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'acquisition'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                User Acquisition
              </button>
              <button
                onClick={() => setActiveTab('content')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'content'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Content Marketing
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'analytics'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Analytics
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'acquisition' && <AcquisitionTab />}
            {activeTab === 'content' && <ContentMarketingTab />}
            {activeTab === 'analytics' && <AnalyticsTab />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessGrowthDashboard;