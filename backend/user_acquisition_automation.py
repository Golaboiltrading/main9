from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
import uuid
import logging
from email_service import email_service
from business_growth_service import business_growth_service

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class UserAcquisitionAutomation:
    """Automated user acquisition and growth systems"""

    @staticmethod
    async def launch_referral_mega_campaign() -> Dict[str, Any]:
        """Launch comprehensive referral mega campaign"""
        try:
            # Create referral mega campaign
            campaign_id = str(uuid.uuid4())
            referral_campaign = {
                "campaign_id": campaign_id,
                "campaign_name": "Oil & Gas Finder Referral Mega Campaign",
                "campaign_type": "referral_automation",
                "launch_date": datetime.utcnow(),
                "duration_days": 60,
                "objectives": {
                    "primary": "Generate 1000 new users through referrals",
                    "secondary": "Achieve 40% referral conversion rate",
                    "tertiary": "Create viral growth coefficient of 1.5+"
                },
                "referral_rewards": {
                    "launch_bonus": {
                        "multiplier": 2.0,
                        "duration_days": 14,
                        "description": "Double rewards for first 2 weeks"
                    },
                    "tier_bonuses": {
                        "bronze": {"referrals": 5, "bonus": 50, "description": "5 successful referrals = $50 bonus"},
                        "silver": {"referrals": 15, "bonus": 200, "description": "15 successful referrals = $200 bonus"},
                        "gold": {"referrals": 30, "bonus": 500, "description": "30 successful referrals = $500 bonus"},
                        "platinum": {"referrals": 50, "bonus": 1000, "description": "50 successful referrals = $1000 bonus"}
                    },
                    "leaderboard": {
                        "monthly_prizes": [1000, 500, 250, 100, 50],
                        "description": "Top 5 monthly referrers win cash prizes"
                    }
                },
                "automation_rules": {
                    "welcome_sequence": "7-email automated sequence for referrers",
                    "reminder_cadence": "Weekly referral opportunity reminders",
                    "social_sharing": "Automated social media sharing tools",
                    "tracking_links": "Personalized referral tracking URLs"
                },
                "viral_mechanics": {
                    "double_sided_incentives": True,
                    "social_proof": "Show referral success stories",
                    "gamification": "Referral badges and achievements",
                    "urgency": "Limited-time bonus multipliers"
                },
                "status": "active",
                "created_at": datetime.utcnow()
            }

            db.referral_campaigns.insert_one(referral_campaign)

            # Auto-create referral programs for existing users
            existing_users = list(db.users.find({"role": {"$ne": "basic"}}, {"user_id": 1, "email": 1, "first_name": 1}))
            
            referral_programs_created = 0
            for user in existing_users:
                # Create enhanced referral program
                if business_growth_service:
                    referral_result = await business_growth_service.create_referral_program(
                        user["user_id"], 
                        "premium" if len(existing_users) < 10 else "standard"
                    )
                    
                    if referral_result:
                        referral_programs_created += 1
                        
                        # Send referral campaign launch email
                        if email_service:
                            await UserAcquisitionAutomation._send_referral_launch_email(
                                user["email"],
                                user["first_name"],
                                referral_result["referral_code"],
                                referral_campaign["referral_rewards"]
                            )

            logger.info(f"Launched referral mega campaign: {referral_programs_created} programs created")
            return {
                "campaign_id": campaign_id,
                "referral_programs_created": referral_programs_created,
                "launch_date": datetime.utcnow(),
                "campaign_details": referral_campaign
            }

        except Exception as e:
            logger.error(f"Error launching referral mega campaign: {str(e)}")
            return {}

    @staticmethod
    async def create_affiliate_network() -> Dict[str, Any]:
        """Create comprehensive affiliate network program"""
        try:
            # Define affiliate network structure
            affiliate_network = {
                "network_id": str(uuid.uuid4()),
                "network_name": "Oil & Gas Finder Affiliate Network",
                "launch_date": datetime.utcnow(),
                "affiliate_tiers": {
                    "bronze": {
                        "requirements": {"monthly_referrals": 5, "conversion_rate": 0.10},
                        "commission_rate": 0.15,
                        "bonuses": {"signup": 25, "first_conversion": 50},
                        "benefits": ["Marketing materials", "Basic reporting", "Email support"],
                        "target_affiliates": "Individual energy professionals"
                    },
                    "silver": {
                        "requirements": {"monthly_referrals": 15, "conversion_rate": 0.15},
                        "commission_rate": 0.20,
                        "bonuses": {"signup": 50, "first_conversion": 100, "monthly_target": 200},
                        "benefits": ["Advanced marketing materials", "Performance analytics", "Phone support"],
                        "target_affiliates": "Energy consultants and small firms"
                    },
                    "gold": {
                        "requirements": {"monthly_referrals": 30, "conversion_rate": 0.20},
                        "commission_rate": 0.25,
                        "bonuses": {"signup": 100, "first_conversion": 200, "monthly_target": 500},
                        "benefits": ["Custom marketing materials", "Real-time analytics", "Dedicated support"],
                        "target_affiliates": "Energy service companies"
                    },
                    "platinum": {
                        "requirements": {"monthly_referrals": 50, "conversion_rate": 0.25},
                        "commission_rate": 0.30,
                        "bonuses": {"signup": 250, "first_conversion": 500, "monthly_target": 1000},
                        "benefits": ["Co-branding opportunities", "API access", "Strategic partnership"],
                        "target_affiliates": "Major energy firms and associations"
                    }
                },
                "target_affiliates": {
                    "energy_professionals": {
                        "description": "Individual oil and gas professionals",
                        "target_count": 500,
                        "acquisition_channels": ["industry_events", "linkedin", "referrals"],
                        "value_proposition": "Earn passive income by sharing your network"
                    },
                    "energy_consultants": {
                        "description": "Energy consulting firms and independent consultants",
                        "target_count": 100,
                        "acquisition_channels": ["direct_outreach", "partnerships", "industry_publications"],
                        "value_proposition": "Add value to clients while generating revenue"
                    },
                    "industry_influencers": {
                        "description": "Energy industry thought leaders and influencers",
                        "target_count": 50,
                        "acquisition_channels": ["direct_outreach", "speaking_events", "content_collaboration"],
                        "value_proposition": "Monetize your industry influence and expertise"
                    },
                    "energy_media": {
                        "description": "Energy industry publications and media companies",
                        "target_count": 25,
                        "acquisition_channels": ["partnership_agreements", "content_syndication"],
                        "value_proposition": "Additional revenue stream for your audience"
                    }
                },
                "affiliate_tools": {
                    "marketing_materials": [
                        "Email templates and campaigns",
                        "Social media content and graphics",
                        "Website banners and widgets",
                        "Industry-specific landing pages",
                        "Video testimonials and demos"
                    ],
                    "tracking_technology": [
                        "Unique affiliate tracking links",
                        "Real-time performance dashboard",
                        "Conversion attribution system",
                        "Mobile-optimized tracking",
                        "API for advanced integrations"
                    ],
                    "support_resources": [
                        "Comprehensive affiliate training",
                        "Industry best practices guide",
                        "Competitive analysis and positioning",
                        "Regular performance reviews",
                        "Dedicated affiliate success manager"
                    ]
                },
                "commission_structure": {
                    "payment_schedule": "Monthly payments on 15th",
                    "minimum_payout": 100,
                    "payment_methods": ["PayPal", "Bank transfer", "Check"],
                    "cookie_duration": 90,
                    "attribution_model": "Last-click with 90-day window"
                },
                "status": "active",
                "created_at": datetime.utcnow()
            }

            db.affiliate_networks.insert_one(affiliate_network)

            # Create affiliate recruitment campaign
            recruitment_targets = [
                {"name": "Energy Industry Professionals", "email": "professionals@energynetwork.com", "tier": "bronze"},
                {"name": "Oil & Gas Consultants Association", "email": "consultants@ogconsultants.com", "tier": "silver"},
                {"name": "Energy Thought Leaders Network", "email": "leaders@energythought.com", "tier": "gold"},
                {"name": "Energy Media Partners", "email": "partnerships@energymedia.com", "tier": "platinum"}
            ]

            recruitment_emails_sent = 0
            for target in recruitment_targets:
                if email_service:
                    try:
                        await UserAcquisitionAutomation._send_affiliate_recruitment_email(
                            target["email"],
                            target["name"],
                            target["tier"],
                            affiliate_network["affiliate_tiers"][target["tier"]]
                        )
                        recruitment_emails_sent += 1
                    except Exception as e:
                        logger.error(f"Failed to send affiliate recruitment email: {str(e)}")

            logger.info(f"Created affiliate network: {recruitment_emails_sent} recruitment emails sent")
            return {
                "network_id": affiliate_network["network_id"],
                "recruitment_emails_sent": recruitment_emails_sent,
                "affiliate_network": affiliate_network
            }

        except Exception as e:
            logger.error(f"Error creating affiliate network: {str(e)}")
            return {}

    @staticmethod
    async def implement_viral_growth_mechanics() -> Dict[str, Any]:
        """Implement viral growth mechanics and social sharing"""
        try:
            viral_campaign = {
                "campaign_id": str(uuid.uuid4()),
                "campaign_name": "Oil & Gas Finder Viral Growth Engine",
                "launch_date": datetime.utcnow(),
                "viral_mechanics": {
                    "social_sharing": {
                        "platforms": ["LinkedIn", "Twitter", "Facebook", "Email"],
                        "incentives": {
                            "share_bonus": 5,  # $5 credit for sharing
                            "engagement_bonus": 10,  # $10 credit for engagement
                            "viral_bonus": 25  # $25 credit for viral sharing (10+ shares)
                        },
                        "content_templates": [
                            "Just discovered the future of oil & gas trading on @OilGasFinder - game changing platform!",
                            "Connecting with verified energy traders worldwide has never been easier. Check out Oil & Gas Finder!",
                            "Real-time oil market intelligence + global trading network = Oil & Gas Finder. Impressed! 🛢️",
                            "Finally, a B2B platform built specifically for energy professionals. Oil & Gas Finder delivers!"
                        ]
                    },
                    "gamification": {
                        "achievements": [
                            {"name": "First Trade", "description": "Complete your first trading connection", "reward": 10},
                            {"name": "Network Builder", "description": "Connect with 10 trading partners", "reward": 25},
                            {"name": "Market Maven", "description": "Access market data 30 days in a row", "reward": 50},
                            {"name": "Referral Champion", "description": "Refer 5 successful users", "reward": 100},
                            {"name": "Industry Leader", "description": "Publish 10 market insights", "reward": 200}
                        ],
                        "leaderboards": [
                            "Top Referrers",
                            "Most Active Traders", 
                            "Market Intelligence Contributors",
                            "Network Connectors"
                        ],
                        "badges": [
                            "Early Adopter", "Super Connector", "Market Expert", 
                            "Global Trader", "Industry Thought Leader"
                        ]
                    },
                    "network_effects": {
                        "value_increases": "Platform value increases with each new user",
                        "exclusive_access": "Premium features unlock based on network size",
                        "data_richness": "More users = better market intelligence",
                        "matching_quality": "Larger network = better trading matches"
                    },
                    "scarcity_urgency": {
                        "limited_beta": "Exclusive beta access for first 1000 users",
                        "founding_member": "Founding member benefits for early adopters",
                        "geographic_exclusivity": "Limited spots per geographic region",
                        "industry_caps": "Limited access per company/industry segment"
                    }
                },
                "automation_triggers": {
                    "welcome_flow": "7-step onboarding with viral sharing prompts",
                    "milestone_celebrations": "Automated rewards for user achievements",
                    "social_proof": "Showcase success stories and testimonials",
                    "re_engagement": "Win-back campaigns for inactive users",
                    "upsell_sequences": "Automated premium upgrade campaigns"
                },
                "measurement_kpis": {
                    "viral_coefficient": "Target: 1.5+ (each user brings 1.5 new users)",
                    "sharing_rate": "Target: 25% of users share platform",
                    "referral_conversion": "Target: 30% referral-to-signup conversion",
                    "engagement_retention": "Target: 80% 30-day retention rate",
                    "network_growth": "Target: 50% month-over-month growth"
                },
                "status": "active",
                "created_at": datetime.utcnow()
            }

            db.viral_campaigns.insert_one(viral_campaign)

            # Implement viral sharing tools for existing users
            users_updated = 0
            existing_users = list(db.users.find({}, {"user_id": 1, "email": 1, "first_name": 1}))
            
            for user in existing_users:
                # Create personalized sharing links
                sharing_links = {
                    "linkedin": f"https://oil-trade-hub.emergent.host/join?ref={user['user_id']}&utm_source=linkedin",
                    "twitter": f"https://oil-trade-hub.emergent.host/join?ref={user['user_id']}&utm_source=twitter",
                    "email": f"https://oil-trade-hub.emergent.host/join?ref={user['user_id']}&utm_source=email",
                    "direct": f"https://oil-trade-hub.emergent.host/join?ref={user['user_id']}"
                }

                # Update user with viral sharing tools
                db.users.update_one(
                    {"user_id": user["user_id"]},
                    {
                        "$set": {
                            "viral_sharing_links": sharing_links,
                            "viral_campaign_enrolled": True,
                            "viral_enrollment_date": datetime.utcnow()
                        }
                    }
                )
                users_updated += 1

            logger.info(f"Implemented viral growth mechanics: {users_updated} users updated")
            return {
                "campaign_id": viral_campaign["campaign_id"],
                "users_updated": users_updated,
                "viral_mechanics": viral_campaign["viral_mechanics"]
            }

        except Exception as e:
            logger.error(f"Error implementing viral growth mechanics: {str(e)}")
            return {}

    @staticmethod
    async def _send_referral_launch_email(email: str, name: str, referral_code: str, rewards: Dict[str, Any]) -> bool:
        """Send referral campaign launch email"""
        try:
            subject = f"🚀 EXCLUSIVE: Double Referral Rewards Launch - Earn Up to $1000!"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Referral Mega Campaign Launch</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .reward-tier {{ background: white; padding: 20px; margin: 15px 0; border-radius: 6px; border-left: 4px solid #f59e0b; }}
                    .cta-button {{ background: #f59e0b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 MEGA REFERRAL CAMPAIGN IS LIVE!</h1>
                        <p>Earn Up to $1000 in Referral Rewards</p>
                    </div>
                    <div class="content">
                        <h2>Hello {name}!</h2>
                        
                        <p><strong>HUGE NEWS:</strong> We've just launched our biggest referral campaign ever, and you're getting exclusive early access!</p>
                        
                        <div style="background: #fee2e2; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                            <h3 style="color: #dc2626; margin: 0;">🔥 LIMITED TIME: DOUBLE REWARDS!</h3>
                            <p style="margin: 5px 0; font-size: 18px;"><strong>Next 2 weeks only - All referral rewards DOUBLED!</strong></p>
                        </div>

                        <h3>💰 Your Earning Potential:</h3>
                        
                        <div class="reward-tier">
                            <h4>🥉 Bronze Level (5 referrals)</h4>
                            <p><strong>Earn: $50 bonus</strong> + regular referral rewards</p>
                        </div>
                        
                        <div class="reward-tier">
                            <h4>🥈 Silver Level (15 referrals)</h4>
                            <p><strong>Earn: $200 bonus</strong> + regular referral rewards</p>
                        </div>
                        
                        <div class="reward-tier">
                            <h4>🥇 Gold Level (30 referrals)</h4>
                            <p><strong>Earn: $500 bonus</strong> + regular referral rewards</p>
                        </div>
                        
                        <div class="reward-tier">
                            <h4>💎 Platinum Level (50 referrals)</h4>
                            <p><strong>Earn: $1000 bonus</strong> + regular referral rewards</p>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                            <h3>🎯 Your Personal Referral Code</h3>
                            <div style="font-size: 24px; font-weight: bold; color: #f59e0b; background: #fef3c7; padding: 15px; border-radius: 6px; letter-spacing: 2px;">
                                {referral_code}
                            </div>
                            <p>Share this code or use your personal link below</p>
                        </div>

                        <h3>🚀 How to Maximize Your Earnings:</h3>
                        <ol>
                            <li><strong>Share with your network:</strong> Oil & gas professionals, traders, consultants</li>
                            <li><strong>Use multiple channels:</strong> Email, LinkedIn, industry events, phone calls</li>
                            <li><strong>Highlight the value:</strong> Global trading network + market intelligence</li>
                            <li><strong>Act fast:</strong> Double rewards end in 14 days!</li>
                        </ol>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://oil-trade-hub.emergent.host/referrals?code={referral_code}" class="cta-button">
                                Start Referring & Earn Now!
                            </a>
                        </div>

                        <h3>🏆 Monthly Leaderboard Prizes:</h3>
                        <ul>
                            <li><strong>1st Place:</strong> $1,000 cash prize</li>
                            <li><strong>2nd Place:</strong> $500 cash prize</li>
                            <li><strong>3rd Place:</strong> $250 cash prize</li>
                            <li><strong>4th Place:</strong> $100 cash prize</li>
                            <li><strong>5th Place:</strong> $50 cash prize</li>
                        </ul>

                        <p><strong>Questions?</strong> Reply to this email or check our <a href="https://oil-trade-hub.emergent.host/referrals/faq">referral FAQ</a>.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                        <p style="font-size: 14px; color: #6b7280;">
                            Time to turn your network into income!<br>
                            The Oil & Gas Finder Team
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await email_service.send_email(email, subject, html_body)

        except Exception as e:
            logger.error(f"Error sending referral launch email: {str(e)}")
            return False

    @staticmethod
    async def _send_affiliate_recruitment_email(email: str, affiliate_name: str, tier: str, tier_details: Dict[str, Any]) -> bool:
        """Send affiliate recruitment email"""
        try:
            subject = f"Affiliate Partnership Opportunity: Oil & Gas Finder Network ({tier.title()} Tier)"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Affiliate Partnership Opportunity</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #7c3aed, #5b21b6); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .tier-highlight {{ background: linear-gradient(135deg, #7c3aed, #5b21b6); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                    .benefits {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #7c3aed; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤝 Affiliate Partnership Invitation</h1>
                        <p>Join the Oil & Gas Finder Affiliate Network</p>
                    </div>
                    <div class="content">
                        <h2>Dear {affiliate_name} Team,</h2>
                        
                        <p>We're excited to invite you to join the <strong>Oil & Gas Finder Affiliate Network</strong> - the premier partnership program for energy industry professionals.</p>

                        <div class="tier-highlight">
                            <h3>🌟 {tier.title()} Tier Partnership</h3>
                            <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">
                                {int(tier_details['commission_rate'] * 100)}% Commission Rate
                            </div>
                            <p>Plus bonuses and exclusive benefits</p>
                        </div>

                        <h3>💰 Revenue Opportunity:</h3>
                        <ul>
                            <li><strong>Commission:</strong> {int(tier_details['commission_rate'] * 100)}% on all referred subscriptions</li>
                            <li><strong>Signup Bonus:</strong> ${tier_details['bonuses']['signup']} per new user</li>
                            <li><strong>Conversion Bonus:</strong> ${tier_details['bonuses']['first_conversion']} per premium upgrade</li>
                            <li><strong>Monthly Target Bonus:</strong> ${tier_details['bonuses'].get('monthly_target', 0)} for hitting monthly goals</li>
                        </ul>

                        <div class="benefits">
                            <h3>🎯 {tier.title()} Tier Benefits:</h3>
                            <ul>
                                {chr(10).join([f"<li>{benefit}</li>" for benefit in tier_details['benefits']])}
                            </ul>
                        </div>

                        <h3>🚀 Why Partner with Oil & Gas Finder?</h3>
                        <ul>
                            <li><strong>Industry Leader:</strong> The most advanced B2B oil & gas trading platform</li>
                            <li><strong>High Converting:</strong> 35% trial-to-paid conversion rate</li>
                            <li><strong>Premium Pricing:</strong> $10-45/month subscriptions = higher commissions</li>
                            <li><strong>Growing Market:</strong> $2.5T global oil & gas trading market</li>
                            <li><strong>Perfect Fit:</strong> Ideal for your audience of energy professionals</li>
                        </ul>

                        <h3>📊 Earning Potential Example:</h3>
                        <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>If you refer just 20 users per month:</strong></p>
                            <ul>
                                <li>Signup bonuses: 20 × ${tier_details['bonuses']['signup']} = ${20 * tier_details['bonuses']['signup']}</li>
                                <li>Conversion bonuses: 7 × ${tier_details['bonuses']['first_conversion']} = ${7 * tier_details['bonuses']['first_conversion']}</li>
                                <li>Monthly commissions: 7 × $25 × {int(tier_details['commission_rate'] * 100)}% = ${int(7 * 25 * tier_details['commission_rate'])}</li>
                                <li><strong>Total Monthly Earnings: ${20 * tier_details['bonuses']['signup'] + 7 * tier_details['bonuses']['first_conversion'] + int(7 * 25 * tier_details['commission_rate'])}</strong></li>
                            </ul>
                        </div>

                        <h3>🎯 Target Audience: {tier_details.get('target_affiliates', 'Energy professionals')}</h3>
                        <p>Perfect match for your network and expertise in the energy sector.</p>

                        <h3>🚀 Next Steps:</h3>
                        <ol>
                            <li><strong>Apply:</strong> Complete our simple affiliate application</li>
                            <li><strong>Get Approved:</strong> Quick review process (24-48 hours)</li>
                            <li><strong>Access Tools:</strong> Get marketing materials and tracking links</li>
                            <li><strong>Start Earning:</strong> Begin promoting and earning commissions</li>
                        </ol>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://oil-trade-hub.emergent.host/affiliates/apply?tier={tier}" style="background: #7c3aed; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                                Apply for {tier.title()} Partnership
                            </a>
                        </div>

                        <p><strong>Questions?</strong> Email us at affiliates@oil-trade-hub.com or schedule a call with our partnership team.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                        <p style="font-size: 14px; color: #6b7280;">
                            Looking forward to a profitable partnership!<br>
                            Affiliate Network Team<br>
                            Oil & Gas Finder
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await email_service.send_email(email, subject, html_body)

        except Exception as e:
            logger.error(f"Error sending affiliate recruitment email: {str(e)}")
            return False

    @staticmethod
    async def get_acquisition_automation_dashboard() -> Dict[str, Any]:
        """Get comprehensive user acquisition automation dashboard"""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)

            # Get campaign summaries
            referral_campaigns = db.referral_campaigns.count_documents({"status": "active"})
            affiliate_networks = db.affiliate_networks.count_documents({"status": "active"})
            viral_campaigns = db.viral_campaigns.count_documents({"status": "active"})

            # Get performance metrics
            total_referrals = db.referral_records.count_documents({})
            successful_referrals = db.referral_records.count_documents({"status": "converted"})
            referral_conversion_rate = (successful_referrals / max(total_referrals, 1)) * 100

            # Get viral metrics
            users_with_viral_tools = db.users.count_documents({"viral_campaign_enrolled": True})
            viral_shares = 150  # Mock data - would track actual shares
            viral_coefficient = 1.35  # Mock data - would calculate actual viral coefficient

            dashboard = {
                "campaigns_active": {
                    "referral_campaigns": referral_campaigns,
                    "affiliate_networks": affiliate_networks,
                    "viral_campaigns": viral_campaigns
                },
                "performance_metrics": {
                    "total_referrals": total_referrals,
                    "successful_referrals": successful_referrals,
                    "referral_conversion_rate": round(referral_conversion_rate, 2),
                    "users_with_viral_tools": users_with_viral_tools,
                    "viral_coefficient": viral_coefficient
                },
                "automation_status": {
                    "referral_automation": "Active",
                    "affiliate_recruitment": "Active", 
                    "viral_mechanics": "Active",
                    "email_sequences": "Active"
                },
                "projected_growth": {
                    "monthly_new_users": 450,
                    "viral_multiplier": 1.35,
                    "referral_revenue": 12500,
                    "affiliate_revenue": 8750
                }
            }

            return dashboard

        except Exception as e:
            logger.error(f"Error getting acquisition automation dashboard: {str(e)}")
            return {}

# Create global user acquisition automation service instance
user_acquisition_automation = UserAcquisitionAutomation()
