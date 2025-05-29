from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
import uuid
import logging
from email_service import email_service

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class StrategicPartnershipsService:
    """Strategic partnerships and industry association management"""

    @staticmethod
    async def create_industry_partnership_program() -> Dict[str, Any]:
        """Create comprehensive industry partnership program"""
        try:
            # Define strategic partnerships
            partnership_targets = {
                "industry_associations": {
                    "tier_1": [
                        {
                            "name": "International Swaps and Derivatives Association (ISDA)",
                            "type": "Trade Association",
                            "focus": "Derivatives and risk management",
                            "members": "850+ global members",
                            "partnership_value": "Regulatory expertise, member access",
                            "contact": "partnerships@isda.org",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.0,
                            "benefits": ["Regulatory insights", "Member directory access", "Event partnerships"]
                        },
                        {
                            "name": "Independent Petroleum Association of America (IPAA)",
                            "type": "Industry Association",
                            "focus": "Oil and gas exploration and production",
                            "members": "5000+ independent producers",
                            "partnership_value": "Producer network, policy advocacy",
                            "contact": "partnerships@ipaa.org",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.0,
                            "benefits": ["Producer connections", "Market intelligence", "Policy updates"]
                        },
                        {
                            "name": "International Gas Union (IGU)",
                            "type": "Global Association",
                            "focus": "Natural gas industry worldwide",
                            "members": "160+ members from 90+ countries",
                            "partnership_value": "Global gas market access",
                            "contact": "partnerships@igu.org",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.0,
                            "benefits": ["Global network", "Technical expertise", "Market reports"]
                        }
                    ],
                    "tier_2": [
                        {
                            "name": "Energy Trading Institute (ETI)",
                            "type": "Educational Organization",
                            "focus": "Energy trading education and certification",
                            "members": "2500+ trading professionals",
                            "partnership_value": "Professional development, certification",
                            "contact": "partnerships@energytrading.org",
                            "partnership_tier": "affiliate",
                            "commission_rate": 0.15,
                            "benefits": ["Training partnerships", "Certification programs", "Member access"]
                        },
                        {
                            "name": "American Petroleum Institute (API)",
                            "type": "Industry Standards Organization",
                            "focus": "Oil and gas industry standards",
                            "members": "600+ corporate members",
                            "partnership_value": "Industry standards, technical expertise",
                            "contact": "partnerships@api.org",
                            "partnership_tier": "affiliate",
                            "commission_rate": 0.10,
                            "benefits": ["Standards access", "Technical resources", "Industry events"]
                        }
                    ]
                },
                "trading_firms": {
                    "tier_1": [
                        {
                            "name": "Vitol Group",
                            "type": "Energy Trading Company",
                            "focus": "Oil and gas trading worldwide",
                            "annual_volume": "7.5 million barrels/day",
                            "partnership_value": "Market liquidity, price discovery",
                            "contact": "partnerships@vitol.com",
                            "partnership_tier": "enterprise",
                            "commission_rate": 0.20,
                            "benefits": ["Volume discounts", "Premium features", "Direct API access"]
                        },
                        {
                            "name": "Glencore International",
                            "type": "Commodity Trading and Mining",
                            "focus": "Global energy and metals trading",
                            "annual_volume": "3.2 million barrels/day",
                            "partnership_value": "Diversified commodity exposure",
                            "contact": "partnerships@glencore.com",
                            "partnership_tier": "enterprise",
                            "commission_rate": 0.20,
                            "benefits": ["Cross-commodity trading", "Global network", "Risk management"]
                        },
                        {
                            "name": "Trafigura Group",
                            "type": "Physical Commodity Trading",
                            "focus": "Oil, gas, and metals trading",
                            "annual_volume": "6.1 million barrels/day",
                            "partnership_value": "Physical market expertise",
                            "contact": "partnerships@trafigura.com",
                            "partnership_tier": "enterprise",
                            "commission_rate": 0.20,
                            "benefits": ["Physical trading", "Storage solutions", "Logistics"]
                        }
                    ],
                    "tier_2": [
                        {
                            "name": "Koch Supply & Trading",
                            "type": "Integrated Energy Company",
                            "focus": "North American energy trading",
                            "annual_volume": "2.1 million barrels/day",
                            "partnership_value": "North American market expertise",
                            "contact": "partnerships@kochtrading.com",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.25,
                            "benefits": ["Regional expertise", "Refining integration", "Infrastructure access"]
                        },
                        {
                            "name": "Mercuria Energy Trading",
                            "type": "Energy Trading House",
                            "focus": "Global energy markets",
                            "annual_volume": "1.8 million barrels/day",
                            "partnership_value": "Flexible trading strategies",
                            "contact": "partnerships@mercuria.com",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.25,
                            "benefits": ["Trading flexibility", "Market making", "Price optimization"]
                        }
                    ]
                },
                "technology_partners": {
                    "tier_1": [
                        {
                            "name": "CME Group",
                            "type": "Financial Markets Company",
                            "focus": "Energy futures and derivatives",
                            "partnership_value": "Price discovery, risk management",
                            "contact": "partnerships@cmegroup.com",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.0,
                            "benefits": ["Market data", "Clearing services", "Risk management tools"]
                        },
                        {
                            "name": "Intercontinental Exchange (ICE)",
                            "type": "Exchange Operator",
                            "focus": "Energy and commodity markets",
                            "partnership_value": "Global exchange access",
                            "contact": "partnerships@ice.com",
                            "partnership_tier": "strategic",
                            "commission_rate": 0.0,
                            "benefits": ["Exchange connectivity", "Data feeds", "Clearing solutions"]
                        }
                    ],
                    "tier_2": [
                        {
                            "name": "Refinitiv (London Stock Exchange Group)",
                            "type": "Financial Data Provider",
                            "focus": "Energy market data and analytics",
                            "partnership_value": "Comprehensive market data",
                            "contact": "partnerships@refinitiv.com",
                            "partnership_tier": "affiliate",
                            "commission_rate": 0.15,
                            "benefits": ["Real-time data", "Analytics tools", "News feeds"]
                        },
                        {
                            "name": "S&P Global Platts",
                            "type": "Commodity Price Reporting Agency",
                            "focus": "Energy price assessments",
                            "partnership_value": "Authoritative price benchmarks",
                            "contact": "partnerships@spglobal.com",
                            "partnership_tier": "affiliate",
                            "commission_rate": 0.15,
                            "benefits": ["Price assessments", "Market analysis", "Research reports"]
                        }
                    ]
                }
            }

            # Create partnership program
            program_id = str(uuid.uuid4())
            partnership_program = {
                "program_id": program_id,
                "program_name": "Oil & Gas Finder Strategic Partnership Program",
                "launch_date": datetime.utcnow(),
                "partnership_targets": partnership_targets,
                "objectives": {
                    "primary": "Establish 10 strategic partnerships within 90 days",
                    "secondary": "Create 25 affiliate partnerships",
                    "tertiary": "Generate $500K annual partnership revenue"
                },
                "partnership_benefits": {
                    "for_partners": [
                        "Revenue sharing opportunities",
                        "Access to global trading network",
                        "Co-marketing and branding opportunities",
                        "Technical integration support",
                        "Exclusive partnership territories"
                    ],
                    "for_platform": [
                        "Expanded market reach",
                        "Industry credibility and validation",
                        "Additional revenue streams",
                        "Enhanced market intelligence",
                        "Regulatory and compliance expertise"
                    ]
                },
                "partnership_tiers": {
                    "strategic": {
                        "revenue_share": 0.30,
                        "minimum_commitment": 50000,
                        "benefits": ["Exclusive territories", "Co-branding", "Technical integration"],
                        "requirements": ["Minimum $1M annual revenue", "Industry reputation", "Technical capabilities"]
                    },
                    "enterprise": {
                        "revenue_share": 0.20,
                        "minimum_commitment": 25000,
                        "benefits": ["Volume discounts", "Priority support", "Custom features"],
                        "requirements": ["Minimum $500K annual revenue", "Trading volume", "Reference customers"]
                    },
                    "affiliate": {
                        "revenue_share": 0.15,
                        "minimum_commitment": 10000,
                        "benefits": ["Marketing support", "Training programs", "Lead sharing"],
                        "requirements": ["Industry presence", "Sales capability", "Customer base"]
                    }
                },
                "status": "active",
                "created_at": datetime.utcnow()
            }

            db.partnership_programs.insert_one(partnership_program)

            logger.info(f"Created strategic partnership program: {program_id}")
            return partnership_program

        except Exception as e:
            logger.error(f"Error creating partnership program: {str(e)}")
            return {}

    @staticmethod
    async def initiate_partnership_outreach(program_id: str, target_category: str = "all") -> Dict[str, Any]:
        """Initiate outreach to strategic partnership targets"""
        try:
            program = db.partnership_programs.find_one({"program_id": program_id})
            if not program:
                return {"success": False, "message": "Partnership program not found"}

            outreach_results = {
                "program_id": program_id,
                "outreach_date": datetime.utcnow(),
                "outreach_category": target_category,
                "contacts_attempted": 0,
                "emails_sent": 0,
                "responses_expected": 0,
                "partnerships_initiated": []
            }

            partnership_targets = program["partnership_targets"]
            
            # Select targets based on category
            if target_category == "all":
                categories_to_process = partnership_targets.keys()
            else:
                categories_to_process = [target_category] if target_category in partnership_targets else []

            for category in categories_to_process:
                category_data = partnership_targets[category]
                
                for tier, partners in category_data.items():
                    for partner in partners:
                        # Create partnership outreach record
                        partnership_id = str(uuid.uuid4())
                        partnership_record = {
                            "partnership_id": partnership_id,
                            "program_id": program_id,
                            "partner_name": partner["name"],
                            "partner_type": partner["type"],
                            "category": category,
                            "tier": tier,
                            "contact_email": partner["contact"],
                            "partnership_tier": partner["partnership_tier"],
                            "commission_rate": partner["commission_rate"],
                            "benefits": partner["benefits"],
                            "status": "outreach_initiated",
                            "outreach_date": datetime.utcnow(),
                            "created_at": datetime.utcnow()
                        }

                        db.partnership_records.insert_one(partnership_record)

                        # Send partnership outreach email
                        if email_service:
                            try:
                                success = await StrategicPartnershipsService._send_partnership_email(partner, partnership_id)
                                if success:
                                    outreach_results["emails_sent"] += 1
                                    outreach_results["partnerships_initiated"].append({
                                        "partner": partner["name"],
                                        "tier": partner["partnership_tier"],
                                        "category": category
                                    })
                            except Exception as e:
                                logger.error(f"Failed to send partnership email to {partner['name']}: {str(e)}")

                        outreach_results["contacts_attempted"] += 1

            outreach_results["responses_expected"] = int(outreach_results["emails_sent"] * 0.15)  # 15% response rate estimate

            # Store outreach results
            db.partnership_outreach.insert_one(outreach_results)

            logger.info(f"Initiated partnership outreach: {outreach_results['emails_sent']} emails sent")
            return outreach_results

        except Exception as e:
            logger.error(f"Error initiating partnership outreach: {str(e)}")
            return {"success": False, "message": str(e)}

    @staticmethod
    async def _send_partnership_email(partner: Dict[str, Any], partnership_id: str) -> bool:
        """Send partnership outreach email"""
        try:
            subject = f"Strategic Partnership Opportunity: {partner['name']} x Oil & Gas Finder"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Strategic Partnership Opportunity</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .value-prop {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #3b82f6; }}
                    .benefits {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Strategic Partnership Opportunity</h1>
                        <p>Oil & Gas Finder x {partner['name']}</p>
                    </div>
                    <div class="content">
                        <h2>Dear {partner['name']} Partnership Team,</h2>
                        
                        <p>I hope this message finds you well. I'm reaching out from <strong>Oil & Gas Finder</strong>, the leading B2B platform for oil and gas trading professionals worldwide.</p>
                        
                        <div class="value-prop">
                            <h3>🎯 Partnership Opportunity</h3>
                            <p>We've identified {partner['name']} as a strategic partner whose expertise in <strong>{partner.get('focus', 'energy markets')}</strong> aligns perfectly with our mission to revolutionize global energy trading.</p>
                            
                            <p><strong>Partnership Value:</strong> {partner.get('partnership_value', 'Mutual growth and market expansion')}</p>
                        </div>

                        <div class="benefits">
                            <h3>🤝 Partnership Benefits for {partner['name']}:</h3>
                            <ul>
                                {chr(10).join([f"<li><strong>{benefit}</strong></li>" for benefit in partner.get('benefits', [])])}
                                <li><strong>Revenue Sharing:</strong> {int(partner.get('commission_rate', 0) * 100)}% commission on referred business</li>
                                <li><strong>Co-marketing Opportunities:</strong> Joint marketing campaigns and industry events</li>
                                <li><strong>Exclusive Access:</strong> Priority access to our global trading network</li>
                            </ul>
                        </div>

                        <div class="value-prop">
                            <h3>📊 About Oil & Gas Finder</h3>
                            <ul>
                                <li><strong>Global Reach:</strong> Active in Houston, Dubai, Singapore, London</li>
                                <li><strong>Trading Network:</strong> 1000+ verified oil and gas professionals</li>
                                <li><strong>Market Intelligence:</strong> Real-time pricing and advanced analytics</li>
                                <li><strong>Technology:</strong> Enterprise-grade platform with API integration</li>
                            </ul>
                        </div>

                        <h3>🚀 Next Steps</h3>
                        <p>I'd love to schedule a brief call to discuss how we can create mutual value through a strategic partnership. Our partnership team can provide:</p>
                        <ul>
                            <li>Detailed partnership proposal and terms</li>
                            <li>Technical integration roadmap</li>
                            <li>Revenue projections and business case</li>
                            <li>Reference customers and case studies</li>
                        </ul>

                        <p><strong>Available for a call this week?</strong> Please reply with your availability, and I'll send a calendar link.</p>
                        
                        <p>Alternatively, you can learn more about our platform at <a href="https://oil-trade-hub.emergent.host">oil-trade-hub.emergent.host</a></p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                        <p>Looking forward to exploring this exciting opportunity together.</p>
                        
                        <p style="font-size: 14px; color: #6b7280;">
                            Best regards,<br>
                            Strategic Partnerships Team<br>
                            Oil & Gas Finder<br>
                            partnerships@oil-trade-hub.com<br>
                            <a href="https://oil-trade-hub.emergent.host">https://oil-trade-hub.emergent.host</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = await email_service.send_email(partner["contact"], subject, html_body)
            
            if success:
                # Track email sent
                db.partnership_records.update_one(
                    {"partnership_id": partnership_id},
                    {
                        "$set": {
                            "email_sent": True,
                            "email_sent_date": datetime.utcnow()
                        }
                    }
                )

            return success

        except Exception as e:
            logger.error(f"Error sending partnership email: {str(e)}")
            return False

    @staticmethod
    async def track_partnership_response(partnership_id: str, response_type: str, response_data: Dict[str, Any]) -> bool:
        """Track partnership responses and progress"""
        try:
            update_data = {
                "last_response_date": datetime.utcnow(),
                "response_type": response_type,
                "response_data": response_data
            }

            # Update status based on response type
            if response_type == "interested":
                update_data["status"] = "negotiation"
            elif response_type == "not_interested":
                update_data["status"] = "declined"
            elif response_type == "agreement_signed":
                update_data["status"] = "active_partner"
            elif response_type == "follow_up_needed":
                update_data["status"] = "follow_up"

            result = db.partnership_records.update_one(
                {"partnership_id": partnership_id},
                {"$set": update_data}
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error tracking partnership response: {str(e)}")
            return False

    @staticmethod
    async def get_partnership_dashboard() -> Dict[str, Any]:
        """Get comprehensive partnership dashboard"""
        try:
            # Get all partnership programs
            programs = list(db.partnership_programs.find({}, {"_id": 0}))
            
            # Get partnership records summary
            total_partnerships = db.partnership_records.count_documents({})
            active_partnerships = db.partnership_records.count_documents({"status": "active_partner"})
            pending_partnerships = db.partnership_records.count_documents({"status": "negotiation"})
            
            # Get partnerships by category
            partnerships_by_category = list(db.partnership_records.aggregate([
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "active": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "active_partner"]}, 1, 0]
                        }
                    }
                }}
            ]))

            # Get recent partnership activities
            recent_activities = list(db.partnership_records.find(
                {"outreach_date": {"$gte": datetime.utcnow() - timedelta(days=30)}},
                {"_id": 0, "partner_name": 1, "status": 1, "partnership_tier": 1, "outreach_date": 1}
            ).sort("outreach_date", -1).limit(10))

            # Calculate partnership ROI
            total_partnership_revenue = 0  # Would calculate from actual partnership revenue
            total_partnership_cost = 15000  # Estimated partnership program cost
            partnership_roi = ((total_partnership_revenue - total_partnership_cost) / max(total_partnership_cost, 1)) * 100

            dashboard = {
                "summary": {
                    "total_partnerships": total_partnerships,
                    "active_partnerships": active_partnerships,
                    "pending_partnerships": pending_partnerships,
                    "partnership_roi": round(partnership_roi, 2)
                },
                "partnerships_by_category": partnerships_by_category,
                "recent_activities": recent_activities,
                "programs": programs,
                "key_metrics": {
                    "response_rate": round((active_partnerships + pending_partnerships) / max(total_partnerships, 1) * 100, 2),
                    "conversion_rate": round(active_partnerships / max(total_partnerships, 1) * 100, 2),
                    "average_partnership_value": 50000,  # Estimated average partnership value
                    "projected_annual_revenue": active_partnerships * 50000
                }
            }

            return dashboard

        except Exception as e:
            logger.error(f"Error getting partnership dashboard: {str(e)}")
            return {}

# Create global strategic partnerships service instance
strategic_partnerships_service = StrategicPartnershipsService()
