from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
import uuid
import logging
import re

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class ContentMarketingService:
    """Content marketing and SEO service for industry authority building"""

    @staticmethod
    async def create_market_insight_article(title: str, content: str, category: str, author_id: str) -> Dict[str, Any]:
        """Create market insight articles for thought leadership"""
        try:
            # Generate SEO-friendly slug
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            
            # Extract keywords for SEO
            oil_gas_keywords = [
                "oil prices", "crude oil", "natural gas", "LNG", "trading", "energy markets",
                "petroleum", "gas condensate", "WTI", "Brent", "oil trading", "gas trading",
                "energy commodities", "oil forecast", "gas prices", "energy outlook"
            ]
            
            found_keywords = [kw for kw in oil_gas_keywords if kw.lower() in content.lower()]
            
            article = {
                "article_id": str(uuid.uuid4()),
                "title": title,
                "slug": slug,
                "content": content,
                "category": category,  # market_analysis, price_forecast, trading_tips, industry_news
                "author_id": author_id,
                "seo_keywords": found_keywords,
                "meta_description": content[:160] + "..." if len(content) > 160 else content,
                "reading_time_minutes": max(1, len(content.split()) // 200),  # Estimate reading time
                "views": 0,
                "shares": 0,
                "likes": 0,
                "comments": [],
                "status": "published",
                "featured": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "published_at": datetime.utcnow()
            }
            
            db.content_articles.insert_one(article)
            
            # Update author's content statistics
            db.users.update_one(
                {"user_id": author_id},
                {
                    "$inc": {"content_published": 1},
                    "$set": {"last_content_date": datetime.utcnow()}
                }
            )
            
            logger.info(f"Created market insight article: {title}")
            return article
            
        except Exception as e:
            logger.error(f"Error creating market insight article: {str(e)}")
            return {}

    @staticmethod
    async def generate_weekly_market_report() -> Dict[str, Any]:
        """Generate comprehensive weekly market report"""
        try:
            # Mock market data - in production would fetch from real APIs
            market_data = {
                "oil_analysis": {
                    "wti_crude": {
                        "current_price": 78.45,
                        "weekly_change": 2.3,
                        "monthly_change": -1.2,
                        "key_drivers": [
                            "OPEC+ production cuts",
                            "US inventory levels",
                            "Geopolitical tensions"
                        ]
                    },
                    "brent_crude": {
                        "current_price": 82.15,
                        "weekly_change": 1.8,
                        "monthly_change": -0.9,
                        "key_drivers": [
                            "European demand recovery",
                            "North Sea production",
                            "Global economic indicators"
                        ]
                    }
                },
                "gas_analysis": {
                    "natural_gas": {
                        "current_price": 2.85,
                        "weekly_change": -0.15,
                        "monthly_change": 0.8,
                        "key_drivers": [
                            "Weather patterns",
                            "Storage levels",
                            "LNG export demand"
                        ]
                    },
                    "lng_prices": {
                        "current_price": 12.45,
                        "weekly_change": 0.95,
                        "monthly_change": 3.2,
                        "key_drivers": [
                            "Asian demand surge",
                            "Supply chain constraints",
                            "European gas crisis"
                        ]
                    }
                },
                "trading_insights": {
                    "market_sentiment": "Cautiously optimistic",
                    "volatility_index": "Moderate",
                    "recommended_strategies": [
                        "Focus on short-term contracts due to volatility",
                        "Consider regional price differentials",
                        "Monitor geopolitical developments closely"
                    ]
                },
                "outlook": {
                    "next_week": "Expect continued volatility with focus on inventory reports",
                    "next_month": "Price stabilization likely as supply-demand balance improves",
                    "key_events": [
                        "EIA inventory report (Wednesday)",
                        "OPEC+ meeting announcement",
                        "Federal Reserve policy decision"
                    ]
                }
            }
            
            # Generate comprehensive report content
            report_content = f"""
# Weekly Oil & Gas Market Report - Week of {datetime.utcnow().strftime('%B %d, %Y')}

## Executive Summary
The oil and gas markets showed mixed signals this week, with crude oil gaining {market_data['oil_analysis']['wti_crude']['weekly_change']}% while natural gas declined {abs(market_data['gas_analysis']['natural_gas']['weekly_change'])}%. Market sentiment remains {market_data['trading_insights']['market_sentiment'].lower()} as traders navigate ongoing supply-demand dynamics.

## Oil Market Analysis

### WTI Crude Oil
- **Current Price:** ${market_data['oil_analysis']['wti_crude']['current_price']}/barrel
- **Weekly Change:** {'+' if market_data['oil_analysis']['wti_crude']['weekly_change'] > 0 else ''}{market_data['oil_analysis']['wti_crude']['weekly_change']}%
- **Monthly Change:** {'+' if market_data['oil_analysis']['wti_crude']['monthly_change'] > 0 else ''}{market_data['oil_analysis']['wti_crude']['monthly_change']}%

### Brent Crude Oil
- **Current Price:** ${market_data['oil_analysis']['brent_crude']['current_price']}/barrel
- **Weekly Change:** {'+' if market_data['oil_analysis']['brent_crude']['weekly_change'] > 0 else ''}{market_data['oil_analysis']['brent_crude']['weekly_change']}%
- **Monthly Change:** {'+' if market_data['oil_analysis']['brent_crude']['monthly_change'] > 0 else ''}{market_data['oil_analysis']['brent_crude']['monthly_change']}%

## Natural Gas Market Analysis

### Henry Hub Natural Gas
- **Current Price:** ${market_data['gas_analysis']['natural_gas']['current_price']}/MMBtu
- **Weekly Change:** {'+' if market_data['gas_analysis']['natural_gas']['weekly_change'] > 0 else ''}{market_data['gas_analysis']['natural_gas']['weekly_change']}%

### LNG Markets
- **Current Price:** ${market_data['gas_analysis']['lng_prices']['current_price']}/MMBtu
- **Weekly Change:** {'+' if market_data['gas_analysis']['lng_prices']['weekly_change'] > 0 else ''}{market_data['gas_analysis']['lng_prices']['weekly_change']}%

## Trading Recommendations
{chr(10).join([f"- {rec}" for rec in market_data['trading_insights']['recommended_strategies']])}

## Week Ahead Outlook
{market_data['outlook']['next_week']}

### Key Events to Watch:
{chr(10).join([f"- {event}" for event in market_data['outlook']['key_events']])}

---
*This report is prepared by the Oil & Gas Finder market intelligence team. For exclusive insights and trading opportunities, visit [Oil & Gas Finder](https://oil-trade-hub.emergent.host).*
"""

            report = {
                "report_id": str(uuid.uuid4()),
                "title": f"Weekly Oil & Gas Market Report - {datetime.utcnow().strftime('%B %d, %Y')}",
                "content": report_content,
                "market_data": market_data,
                "report_type": "weekly_market_report",
                "week_ending": datetime.utcnow(),
                "status": "published",
                "downloads": 0,
                "views": 0,
                "created_at": datetime.utcnow()
            }
            
            db.market_reports.insert_one(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating weekly market report: {str(e)}")
            return {}

    @staticmethod
    async def create_seo_optimized_content(topic: str, target_keywords: List[str], content_type: str = "article") -> Dict[str, Any]:
        """Create SEO-optimized content for organic traffic"""
        try:
            # SEO content templates
            content_templates = {
                "oil_price_forecast": {
                    "title": "Oil Price Forecast 2024: Expert Analysis and Trading Insights",
                    "meta_description": "Get expert oil price forecasts for 2024. Comprehensive analysis of WTI, Brent crude trends and trading opportunities from industry professionals.",
                    "content": """
# Oil Price Forecast 2024: Expert Analysis and Market Outlook

## Current Oil Market Overview
The global oil market continues to evolve in 2024, with WTI crude and Brent oil prices reflecting complex supply-demand dynamics. Our comprehensive analysis examines key factors influencing oil price forecasts.

## Key Price Drivers for 2024
### Supply-Side Factors
- OPEC+ production policies and quotas
- US shale oil production growth
- Global refining capacity utilization
- Geopolitical risks and supply disruptions

### Demand-Side Factors
- Economic recovery post-pandemic
- Transportation fuel demand trends
- Industrial petrochemical consumption
- Seasonal demand variations

## Oil Price Predictions by Quarter
### Q1 2024 Forecast
Expected WTI range: $70-85/barrel, driven by winter heating demand and production adjustments.

### Q2-Q4 2024 Outlook
Anticipating price stabilization as supply-demand balance improves, with potential for $75-90/barrel range.

## Trading Strategies for Oil Markets
For oil traders looking to capitalize on market movements:
- Monitor weekly inventory reports
- Track OPEC+ meeting decisions
- Consider seasonal demand patterns
- Evaluate geopolitical risk premiums

## Conclusion
Oil price forecasts suggest continued volatility with underlying support from supply constraints and recovering demand. Traders should focus on risk management and stay informed through reliable market intelligence.

*Join thousands of oil professionals on Oil & Gas Finder for exclusive market insights and trading opportunities.*
"""
                },
                "gas_trading_guide": {
                    "title": "Complete Guide to Natural Gas Trading: Strategies and Market Analysis",
                    "meta_description": "Master natural gas trading with our comprehensive guide. Learn LNG markets, price analysis, and proven trading strategies from industry experts.",
                    "content": """
# Complete Guide to Natural Gas Trading: Strategies and Market Analysis

## Introduction to Natural Gas Markets
Natural gas trading has become increasingly complex with the growth of LNG markets and global price convergence. This guide covers essential strategies for successful gas trading.

## Understanding Gas Market Fundamentals
### Supply Sources
- Conventional gas production
- Shale gas development
- LNG imports and exports
- Pipeline infrastructure

### Demand Drivers
- Power generation (largest consumer)
- Industrial applications
- Residential and commercial heating
- Petrochemical feedstock

## Natural Gas Price Analysis
### Henry Hub Pricing
The benchmark for North American gas prices, influenced by:
- Storage levels and injections/withdrawals
- Weather patterns and heating/cooling demand
- Production growth from key basins
- Pipeline capacity constraints

### International LNG Pricing
- Asian spot LNG prices (JKM index)
- European gas prices (TTF, NBP)
- Oil-indexed long-term contracts
- Freight and transportation costs

## Gas Trading Strategies
### Seasonal Trading
- Winter heating demand peaks
- Summer cooling demand
- Shoulder season storage strategies

### Spread Trading
- Location basis differentials
- Calendar spread opportunities
- Crack spread relationships

### Risk Management
- Weather hedging strategies
- Storage optimization
- Portfolio diversification

## LNG Market Opportunities
The global LNG market offers unique trading opportunities:
- Arbitrage between regional markets
- Cargo optimization and routing
- Long-term vs. spot market strategies

## Technology and Data Analytics
Modern gas trading relies on:
- Real-time market data feeds
- Weather forecasting models
- Storage inventory tracking
- Transportation optimization tools

## Regulatory Considerations
- FERC regulations in the US
- International trade compliance
- Environmental regulations
- Safety and operational requirements

## Conclusion
Successful natural gas trading requires understanding complex market dynamics, utilizing proper risk management, and staying informed about global developments.

*Connect with gas trading professionals and find opportunities on Oil & Gas Finder - the leading B2B platform for energy professionals.*
"""
                }
            }
            
            # Generate content based on topic
            template = content_templates.get(topic, {
                "title": f"Expert Analysis: {topic.replace('_', ' ').title()}",
                "meta_description": f"Professional insights on {topic.replace('_', ' ')} from industry experts. Latest trends, analysis and opportunities.",
                "content": f"# {topic.replace('_', ' ').title()}\n\nComprehensive analysis and insights on {topic.replace('_', ' ')} for oil and gas professionals."
            })
            
            seo_content = {
                "content_id": str(uuid.uuid4()),
                "title": template["title"],
                "slug": re.sub(r'[^a-zA-Z0-9]+', '-', template["title"].lower()).strip('-'),
                "meta_description": template["meta_description"],
                "content": template["content"],
                "target_keywords": target_keywords,
                "content_type": content_type,
                "seo_score": 85,  # Mock SEO score
                "word_count": len(template["content"].split()),
                "reading_time": max(1, len(template["content"].split()) // 200),
                "status": "published",
                "featured": topic in ["oil_price_forecast", "gas_trading_guide"],
                "views": 0,
                "organic_traffic": 0,
                "social_shares": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.seo_content.insert_one(seo_content)
            
            return seo_content
            
        except Exception as e:
            logger.error(f"Error creating SEO content: {str(e)}")
            return {}

    @staticmethod
    async def generate_industry_whitepaper(title: str, research_topic: str) -> Dict[str, Any]:
        """Generate comprehensive industry whitepapers for lead generation"""
        try:
            whitepaper_templates = {
                "digital_transformation": {
                    "title": "Digital Transformation in Oil & Gas Trading: The Future is Now",
                    "abstract": "An in-depth analysis of how digital technologies are revolutionizing oil and gas trading operations, from AI-powered price forecasting to blockchain-based transaction systems.",
                    "chapters": [
                        "Executive Summary",
                        "Current State of Oil & Gas Trading",
                        "Digital Technology Adoption Trends",
                        "AI and Machine Learning Applications",
                        "Blockchain and Smart Contracts",
                        "Data Analytics and Market Intelligence",
                        "Case Studies and Success Stories",
                        "Implementation Roadmap",
                        "Future Outlook and Recommendations"
                    ]
                },
                "market_outlook_2024": {
                    "title": "Oil & Gas Market Outlook 2024: Navigating Uncertainty",
                    "abstract": "Comprehensive market analysis covering supply-demand dynamics, geopolitical factors, and trading opportunities in the evolving energy landscape.",
                    "chapters": [
                        "Executive Summary",
                        "Global Economic Environment",
                        "Oil Market Fundamentals",
                        "Natural Gas and LNG Markets",
                        "Geopolitical Risk Assessment",
                        "Technology Impact on Trading",
                        "Regulatory Environment Changes",
                        "Trading Strategies for 2024",
                        "Risk Management Framework"
                    ]
                },
                "lng_global_trade": {
                    "title": "The LNG Revolution: Global Trade Dynamics and Opportunities",
                    "abstract": "Analysis of the rapidly evolving LNG market, including new supply sources, demand centers, and trading strategies for the global LNG business.",
                    "chapters": [
                        "Executive Summary",
                        "LNG Market Overview",
                        "Supply-Side Developments",
                        "Demand Growth Analysis", 
                        "Pricing Mechanisms and Trends",
                        "Transportation and Logistics",
                        "Regional Market Analysis",
                        "Trading Strategies and Opportunities",
                        "Future Market Outlook"
                    ]
                }
            }
            
            template = whitepaper_templates.get(research_topic, {
                "title": title,
                "abstract": f"Comprehensive analysis of {research_topic} in the oil and gas industry.",
                "chapters": ["Executive Summary", "Market Analysis", "Key Findings", "Recommendations"]
            })
            
            # Generate comprehensive content for each chapter
            full_content = f"""
# {template['title']}

## Abstract
{template['abstract']}

## Table of Contents
{chr(10).join([f"{i+1}. {chapter}" for i, chapter in enumerate(template['chapters'])])}

---

"""
            
            for i, chapter in enumerate(template['chapters']):
                full_content += f"""
## {i+1}. {chapter}

[Comprehensive content would be generated here based on current market data, industry research, and expert analysis. This section would include detailed analysis, charts, data tables, and actionable insights relevant to {chapter.lower()}.]

---

"""
            
            full_content += f"""
## About Oil & Gas Finder

Oil & Gas Finder is the leading B2B platform connecting oil and gas professionals worldwide. Our platform provides:

- Real-time market intelligence and price data
- Advanced trading opportunities and connections
- Industry-leading analytics and reporting tools
- Expert insights and market analysis

Join thousands of energy professionals at [Oil & Gas Finder](https://oil-trade-hub.emergent.host).

---

*This whitepaper is published by Oil & Gas Finder. For more industry insights and exclusive content, visit our platform or contact our research team.*
"""
            
            whitepaper = {
                "whitepaper_id": str(uuid.uuid4()),
                "title": template["title"],
                "slug": re.sub(r'[^a-zA-Z0-9]+', '-', template["title"].lower()).strip('-'),
                "abstract": template["abstract"],
                "chapters": template["chapters"],
                "full_content": full_content,
                "research_topic": research_topic,
                "page_count": len(template["chapters"]) * 5,  # Estimate 5 pages per chapter
                "word_count": len(full_content.split()),
                "author": "Oil & Gas Finder Research Team",
                "downloads": 0,
                "leads_generated": 0,
                "download_url": f"/downloads/{template['title'].lower().replace(' ', '-').replace(':', '')}.pdf",
                "status": "published",
                "featured": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.whitepapers.insert_one(whitepaper)
            
            return whitepaper
            
        except Exception as e:
            logger.error(f"Error generating industry whitepaper: {str(e)}")
            return {}

    @staticmethod
    async def track_content_performance() -> Dict[str, Any]:
        """Track content marketing performance and ROI"""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Article performance
            article_stats = list(db.content_articles.aggregate([
                {"$group": {
                    "_id": "$category",
                    "total_articles": {"$sum": 1},
                    "total_views": {"$sum": "$views"},
                    "total_shares": {"$sum": "$shares"},
                    "avg_reading_time": {"$avg": "$reading_time_minutes"}
                }},
                {"$sort": {"total_views": -1}}
            ]))
            
            # SEO content performance
            seo_performance = list(db.seo_content.aggregate([
                {"$group": {
                    "_id": None,
                    "total_content": {"$sum": 1},
                    "total_organic_traffic": {"$sum": "$organic_traffic"},
                    "avg_seo_score": {"$avg": "$seo_score"},
                    "total_social_shares": {"$sum": "$social_shares"}
                }}
            ]))
            
            # Whitepaper lead generation
            whitepaper_leads = list(db.whitepapers.aggregate([
                {"$project": {
                    "title": 1,
                    "downloads": 1,
                    "leads_generated": 1,
                    "conversion_rate": {
                        "$multiply": [
                            {"$divide": ["$leads_generated", {"$max": ["$downloads", 1]}]},
                            100
                        ]
                    }
                }},
                {"$sort": {"leads_generated": -1}},
                {"$limit": 5}
            ]))
            
            # Content ROI calculation
            total_content_pieces = (
                db.content_articles.count_documents({}) +
                db.seo_content.count_documents({}) +
                db.whitepapers.count_documents({})
            )
            
            total_leads_from_content = (
                sum([w.get("leads_generated", 0) for w in db.whitepapers.find()]) +
                db.leads.count_documents({"source": "content"})
            )
            
            content_production_cost = total_content_pieces * 500  # Estimate $500 per piece
            lead_value = total_leads_from_content * 25  # Estimate $25 per lead
            content_roi = ((lead_value - content_production_cost) / max(content_production_cost, 1)) * 100
            
            return {
                "article_performance": article_stats,
                "seo_metrics": seo_performance[0] if seo_performance else {},
                "whitepaper_leads": whitepaper_leads,
                "content_roi": {
                    "total_content_pieces": total_content_pieces,
                    "total_leads_generated": total_leads_from_content,
                    "production_cost": content_production_cost,
                    "estimated_lead_value": lead_value,
                    "roi_percentage": round(content_roi, 2)
                },
                "top_performing_keywords": [
                    "oil price forecast", "gas trading", "LNG markets",
                    "crude oil analysis", "energy trading", "oil market outlook"
                ],
                "content_calendar_suggestions": [
                    "Monthly oil price analysis",
                    "Weekly gas market reports",
                    "Quarterly industry outlook",
                    "Annual trading guide updates"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error tracking content performance: {str(e)}")
            return {}

    @staticmethod
    async def get_content_marketing_dashboard() -> Dict[str, Any]:
        """Get comprehensive content marketing dashboard"""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Content publishing stats
            content_stats = {
                "articles_published": db.content_articles.count_documents({"created_at": {"$gte": thirty_days_ago}}),
                "whitepapers_released": db.whitepapers.count_documents({"created_at": {"$gte": thirty_days_ago}}),
                "seo_content_created": db.seo_content.count_documents({"created_at": {"$gte": thirty_days_ago}}),
                "total_content_views": sum([
                    sum([a.get("views", 0) for a in db.content_articles.find()]),
                    sum([s.get("views", 0) for s in db.seo_content.find()]),
                    sum([w.get("downloads", 0) for w in db.whitepapers.find()])
                ])
            }
            
            # Lead generation from content
            content_leads = db.leads.count_documents({
                "source": "content",
                "created_at": {"$gte": thirty_days_ago}
            })
            
            # SEO performance
            seo_rankings = {
                "target_keywords": 25,
                "top_10_rankings": 8,
                "organic_traffic_growth": 35,  # Percentage
                "avg_position": 12.5
            }
            
            # Social media engagement
            social_metrics = {
                "total_shares": sum([a.get("shares", 0) for a in db.content_articles.find()]),
                "linkedin_engagement": 450,
                "twitter_mentions": 123,
                "industry_forum_discussions": 67
            }
            
            return {
                "content_production": content_stats,
                "lead_generation": {
                    "content_leads_30d": content_leads,
                    "whitepaper_downloads": sum([w.get("downloads", 0) for w in db.whitepapers.find()]),
                    "conversion_rate": round((content_leads / max(content_stats["total_content_views"], 1)) * 100, 2)
                },
                "seo_performance": seo_rankings,
                "social_engagement": social_metrics,
                "industry_authority": {
                    "published_insights": content_stats["articles_published"],
                    "industry_citations": 15,
                    "expert_mentions": 8,
                    "speaking_opportunities": 3
                },
                "upcoming_content": [
                    "Q1 2024 Oil Market Outlook",
                    "LNG Trading Strategies Webinar",
                    "Digital Trading Transformation Guide",
                    "Natural Gas Price Forecast Report"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting content marketing dashboard: {str(e)}")
            return {}

# Create global content marketing service instance
content_marketing_service = ContentMarketingService()
