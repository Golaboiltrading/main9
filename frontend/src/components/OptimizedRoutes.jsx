import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Performance-optimized loading component
const LoadingFallback = ({ message = 'Loading...' }) => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    <span className="ml-3 text-lg">{message}</span>
  </div>
);

// Lazy-loaded components for code splitting
const Dashboard = lazy(() => import('./Dashboard'));
const MarketData = lazy(() => import('./MarketData'));
const TradingPlatform = lazy(() => import('./OptimizedTradingPlatform'));
const AIAnalysisPage = lazy(() => import('./AIAnalysisPage'));
const PremiumFeatures = lazy(() => import('./PremiumFeatures'));
const UserProfile = lazy(() => import('./UserProfile'));
const Analytics = lazy(() => import('./Analytics'));
const LegalPages = lazy(() => import('./LegalPages'));

// Enhanced router with performance optimization
const OptimizedRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback message="Loading page..." />}>
      <Routes>
        {/* Main Dashboard - Highest priority */}
        <Route 
          path="/dashboard" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading dashboard..." />}>
              <Dashboard />
            </Suspense>
          } 
        />
        
        {/* Market Data - High priority for trading */}
        <Route 
          path="/market" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading market data..." />}>
              <MarketData />
            </Suspense>
          } 
        />
        
        {/* Trading Platform - High priority */}
        <Route 
          path="/trade" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading trading platform..." />}>
              <TradingPlatform />
            </Suspense>
          } 
        />
        
        {/* AI Analysis - Medium priority */}
        <Route 
          path="/ai-analysis" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading AI analysis..." />}>
              <AIAnalysisPage />
            </Suspense>
          } 
        />
        
        {/* Premium Features - Medium priority */}
        <Route 
          path="/premium" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading premium features..." />}>
              <PremiumFeatures />
            </Suspense>
          } 
        />
        
        {/* User Profile - Low priority */}
        <Route 
          path="/profile" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading profile..." />}>
              <UserProfile />
            </Suspense>
          } 
        />
        
        {/* Analytics - Low priority */}
        <Route 
          path="/analytics" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading analytics..." />}>
              <Analytics />
            </Suspense>
          } 
        />
        
        {/* Legal Pages - Lowest priority */}
        <Route 
          path="/legal/*" 
          element={
            <Suspense fallback={<LoadingFallback message="Loading legal information..." />}>
              <LegalPages />
            </Suspense>
          } 
        />
      </Routes>
    </Suspense>
  );
};

export default OptimizedRoutes;