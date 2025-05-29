import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EmailService:
    """Email notification service for Oil & Gas Finder platform"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@oil-trade-hub.com')
        self.company_name = "Oil & Gas Finder"
        self.platform_url = "https://oil-trade-hub.emergent.host"

    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send email using SMTP"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Email not sent.")
                return False

            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.company_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text and HTML parts
            if text_body:
                text_part = MimeText(text_body, 'plain')
                msg.attach(text_part)
            
            html_part = MimeText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = f"Welcome to {self.company_name}!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Oil & Gas Finder</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }}
                .features {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #3b82f6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛢️ Welcome to Oil & Gas Finder!</h1>
                    <p>Your gateway to global oil and gas trading opportunities</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Thank you for joining the <strong>Oil & Gas Finder</strong> platform! You're now part of a growing community of oil and gas professionals connecting worldwide.</p>
                    
                    <div class="features">
                        <h3>🚀 What you can do now:</h3>
                        <ul>
                            <li><strong>Browse Trading Opportunities:</strong> Explore oil and gas listings from verified traders</li>
                            <li><strong>Create Your Listings:</strong> Post your oil and gas trading opportunities</li>
                            <li><strong>Connect with Traders:</strong> Build valuable business relationships</li>
                            <li><strong>Access Market Data:</strong> Stay updated with real-time oil and gas prices</li>
                            <li><strong>Premium Features:</strong> Upgrade for enhanced visibility and analytics</li>
                        </ul>
                    </div>

                    <p>Ready to start trading? Visit your dashboard to create your first listing or browse available opportunities.</p>
                    
                    <a href="{self.platform_url}/dashboard" class="button">Go to Dashboard</a>
                    
                    <p><strong>Need help?</strong> Our support team is here to assist you. Reply to this email or visit our help center.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Best regards,<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Oil & Gas Finder!
        
        Hello {user_name},
        
        Thank you for joining the Oil & Gas Finder platform! You're now part of a growing community of oil and gas professionals connecting worldwide.
        
        What you can do now:
        - Browse Trading Opportunities: Explore oil and gas listings from verified traders
        - Create Your Listings: Post your oil and gas trading opportunities
        - Connect with Traders: Build valuable business relationships
        - Access Market Data: Stay updated with real-time oil and gas prices
        - Premium Features: Upgrade for enhanced visibility and analytics
        
        Visit your dashboard: {self.platform_url}/dashboard
        
        Best regards,
        The Oil & Gas Finder Team
        {self.platform_url}
        """
        
        return await self.send_email(user_email, subject, html_body, text_body)

    async def send_payment_confirmation(self, user_email: str, user_name: str, payment_details: Dict[str, Any]) -> bool:
        """Send payment confirmation email"""
        subject = "Payment Confirmation - Oil & Gas Finder"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .payment-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border: 1px solid #e5e7eb; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #10b981; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed!</h1>
                    <p>Your payment has been processed successfully</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We've successfully processed your payment. Here are the details:</p>
                    
                    <div class="payment-details">
                        <h3>Payment Details</h3>
                        <p><strong>Amount:</strong> <span class="amount">${payment_details.get('amount', 'N/A')}</span></p>
                        <p><strong>Payment Type:</strong> {payment_details.get('payment_type', 'N/A').replace('_', ' ').title()}</p>
                        <p><strong>Transaction ID:</strong> {payment_details.get('payment_id', 'N/A')}</p>
                        <p><strong>Date:</strong> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                        {"<p><strong>Subscription Tier:</strong> " + payment_details.get('subscription_tier', '').replace('_', ' ').title() + "</p>" if payment_details.get('subscription_tier') else ""}
                    </div>

                    <p>Your account has been updated and you now have access to your purchased features.</p>
                    
                    <p>Visit your dashboard to explore your new capabilities:</p>
                    <a href="{self.platform_url}/dashboard" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Visit Dashboard</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Thank you for your business!<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

    async def send_subscription_confirmation(self, user_email: str, user_name: str, subscription_details: Dict[str, Any]) -> bool:
        """Send subscription confirmation email"""
        subject = "Subscription Activated - Oil & Gas Finder Premium"
        
        tier_name = subscription_details.get('tier', '').replace('_', ' ').title()
        monthly_price = subscription_details.get('monthly_price', 'N/A')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Subscription Activated</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .subscription-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border: 1px solid #e5e7eb; }}
                .benefits {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #7c3aed; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Premium!</h1>
                    <p>Your {tier_name} subscription is now active</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Congratulations! Your premium subscription has been activated and you now have access to enhanced features.</p>
                    
                    <div class="subscription-details">
                        <h3>Subscription Details</h3>
                        <p><strong>Plan:</strong> {tier_name}</p>
                        <p><strong>Monthly Price:</strong> ${monthly_price}</p>
                        <p><strong>Status:</strong> Active</p>
                        <p><strong>Next Billing:</strong> {(datetime.utcnow() + timedelta(days=30)).strftime('%B %d, %Y')}</p>
                    </div>

                    <div class="benefits">
                        <h3>🚀 Your Premium Benefits:</h3>
                        <ul>
                            <li><strong>Featured Listings:</strong> Enhanced visibility for your trading opportunities</li>
                            <li><strong>Advanced Analytics:</strong> Detailed insights into your trading performance</li>
                            <li><strong>Priority Support:</strong> Dedicated assistance from our expert team</li>
                            <li><strong>Premium Badge:</strong> Stand out as a verified premium trader</li>
                            <li><strong>Unlimited Connections:</strong> Connect with unlimited trading partners</li>
                            {"<li><strong>API Access:</strong> Integrate with our trading API</li>" if tier_name == "Enterprise" else ""}
                        </ul>
                    </div>

                    <p>Start exploring your premium features now:</p>
                    <a href="{self.platform_url}/dashboard" style="background: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Access Premium Dashboard</a>
                    
                    <p><strong>Manage your subscription:</strong> You can view billing details, update payment methods, or cancel your subscription anytime in your account settings.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Welcome to premium!<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

    async def send_connection_request(self, trader_email: str, trader_name: str, requester_name: str, listing_title: str) -> bool:
        """Send email notification for new connection request"""
        subject = f"New Trading Connection Request - {listing_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Connection Request</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3b82f6; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .request-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border: 1px solid #e5e7eb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤝 New Connection Request</h1>
                    <p>Someone wants to connect with you!</p>
                </div>
                <div class="content">
                    <h2>Hello {trader_name},</h2>
                    <p>You have received a new connection request for one of your listings on Oil & Gas Finder.</p>
                    
                    <div class="request-details">
                        <h3>Connection Details</h3>
                        <p><strong>From:</strong> {requester_name}</p>
                        <p><strong>Listing:</strong> {listing_title}</p>
                        <p><strong>Date:</strong> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                    </div>

                    <p>This trader is interested in your listing and would like to discuss potential business opportunities.</p>
                    
                    <p>Log in to your dashboard to view the full request and respond:</p>
                    <a href="{self.platform_url}/dashboard" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">View Connection Request</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Happy trading!<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(trader_email, subject, html_body)

    async def send_listing_approval(self, user_email: str, user_name: str, listing_title: str, is_featured: bool = False) -> bool:
        """Send listing approval/publication notification"""
        subject = f"Your Listing is Live - {listing_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Listing Published</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .listing-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border: 1px solid #e5e7eb; }}
                .featured-badge {{ background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Your Listing is Live!</h1>
                    <p>Your trading opportunity is now visible to potential partners</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Great news! Your listing has been published and is now visible to traders on the Oil & Gas Finder platform.</p>
                    
                    <div class="listing-details">
                        <h3>Published Listing</h3>
                        <p><strong>Title:</strong> {listing_title}</p>
                        {"<p><span class='featured-badge'>FEATURED LISTING</span></p>" if is_featured else ""}
                        <p><strong>Status:</strong> Active and Visible</p>
                        <p><strong>Published:</strong> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                    </div>

                    <p>Your listing is now being seen by potential trading partners worldwide. Here's what happens next:</p>
                    
                    <ul>
                        <li><strong>Visibility:</strong> Your listing appears in search results and category pages</li>
                        <li><strong>Connections:</strong> Interested traders can request to connect with you</li>
                        <li><strong>Notifications:</strong> You'll receive emails when traders show interest</li>
                        {"<li><strong>Premium Placement:</strong> Your featured listing gets priority visibility</li>" if is_featured else ""}
                    </ul>
                    
                    <p>Monitor your listing performance and manage connection requests:</p>
                    <a href="{self.platform_url}/dashboard" style="background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Manage Listings</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Good luck with your trading!<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

    async def send_market_update(self, user_email: str, user_name: str, market_data: Dict[str, Any]) -> bool:
        """Send weekly market update to users"""
        subject = "Weekly Oil & Gas Market Update"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Market Update</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .price-section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; border: 1px solid #e5e7eb; }}
                .price-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f3f4f6; }}
                .price-up {{ color: #10b981; font-weight: bold; }}
                .price-down {{ color: #ef4444; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Market Update</h1>
                    <p>Stay informed with the latest oil and gas market trends</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Here's your weekly summary of oil and gas market movements:</p>
                    
                    <div class="price-section">
                        <h3>🛢️ Oil Prices</h3>
                        <div class="price-item">
                            <span>WTI Crude</span>
                            <span>${market_data.get('wti_price', 'N/A')} <span class="price-up">{market_data.get('wti_change', '')}</span></span>
                        </div>
                        <div class="price-item">
                            <span>Brent Crude</span>
                            <span>${market_data.get('brent_price', 'N/A')} <span class="price-up">{market_data.get('brent_change', '')}</span></span>
                        </div>
                    </div>

                    <div class="price-section">
                        <h3>⛽ Gas Prices</h3>
                        <div class="price-item">
                            <span>Natural Gas</span>
                            <span>${market_data.get('ng_price', 'N/A')} <span class="price-down">{market_data.get('ng_change', '')}</span></span>
                        </div>
                        <div class="price-item">
                            <span>LNG</span>
                            <span>${market_data.get('lng_price', 'N/A')} <span class="price-up">{market_data.get('lng_change', '')}</span></span>
                        </div>
                    </div>

                    <p><strong>Market Insights:</strong> {market_data.get('insights', 'Oil and gas markets continue to show volatility amid global economic factors.')}</p>
                    
                    <p>Explore current trading opportunities:</p>
                    <a href="{self.platform_url}/browse" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">View Trading Opportunities</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Stay informed, trade smart!<br>
                        The Oil & Gas Finder Team<br>
                        <a href="{self.platform_url}">{self.platform_url}</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

    async def send_referral_welcome_email(self, user_email: str, user_name: str, discount_amount: float, referrer_company: str) -> bool:
        """Send welcome email to referred user"""
        subject = f"Welcome to Oil & Gas Finder - ${discount_amount} Credit Applied!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome via Referral</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .credit-highlight {{ background: #10b981; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Oil & Gas Finder!</h1>
                    <p>You've been referred by {referrer_company}</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Congratulations! You've joined Oil & Gas Finder through a referral from <strong>{referrer_company}</strong>, and we've applied a special credit to your account.</p>
                    
                    <div class="credit-highlight">
                        <h3>💰 ${discount_amount} Account Credit Applied!</h3>
                        <p>Use this credit towards premium subscriptions or featured listings</p>
                    </div>

                    <p>As a referred member, you're already connected to a trusted network of oil and gas professionals. Start exploring trading opportunities and connect with verified industry partners.</p>
                    
                    <a href="{self.platform_url}/dashboard" style="background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Start Trading Now</a>
                    
                    <p>Your account credit expires in 30 days, so make sure to use it soon!</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Welcome to the community!<br>
                        The Oil & Gas Finder Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

    async def send_referral_notification_email(self, referrer_email: str, referrer_name: str, referee_name: str, referee_company: str) -> bool:
        """Send notification to referrer about successful referral"""
        subject = f"Great News! {referee_name} Joined Through Your Referral"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Referral Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3b82f6; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Referral Success!</h1>
                    <p>Your referral is now part of the Oil & Gas Finder community</p>
                </div>
                <div class="content">
                    <h2>Hello {referrer_name},</h2>
                    <p>Excellent news! <strong>{referee_name}</strong> from <strong>{referee_company}</strong> has successfully joined Oil & Gas Finder using your referral.</p>
                    
                    <p>Your referral reward will be processed once they complete their first transaction or upgrade to a premium subscription.</p>
                    
                    <p>Keep sharing Oil & Gas Finder with your professional network to earn more rewards and help grow the trading community!</p>
                    
                    <a href="{self.platform_url}/referrals" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">View Referral Dashboard</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Thank you for growing our community!<br>
                        The Oil & Gas Finder Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(referrer_email, subject, html_body)

    async def send_referral_reward_email(self, referrer_email: str, referrer_name: str, reward_amount: float, referee_company: str, conversion_type: str) -> bool:
        """Send referral reward notification"""
        subject = f"Referral Reward Earned - ${reward_amount}!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Referral Reward</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .reward-amount {{ font-size: 32px; font-weight: bold; color: #f59e0b; text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Referral Reward Earned!</h1>
                    <p>Your referral converted to a paying customer</p>
                </div>
                <div class="content">
                    <h2>Congratulations {referrer_name}!</h2>
                    <p>Great news! Your referral from <strong>{referee_company}</strong> has {conversion_type.replace('_', ' ')}d, which means you've earned a referral reward!</p>
                    
                    <div class="reward-amount">${reward_amount}</div>
                    
                    <p>This credit has been added to your account and can be used towards:</p>
                    <ul>
                        <li>Premium subscription upgrades</li>
                        <li>Featured listing enhancements</li>
                        <li>Future platform services</li>
                    </ul>
                    
                    <p>Keep referring quality professionals to continue earning rewards and building the Oil & Gas Finder community!</p>
                    
                    <a href="{self.platform_url}/account/credits" style="background: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">View Account Credits</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Thank you for being a valued partner!<br>
                        The Oil & Gas Finder Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(referrer_email, subject, html_body)

    async def send_lead_magnet_email(self, user_email: str, content_title: str, content_description: str, download_url: str) -> bool:
        """Send lead magnet content to prospects"""
        subject = f"Your Free Download: {content_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Lead Magnet Delivery</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6366f1; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .download-section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px solid #6366f1; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Your Content is Ready!</h1>
                    <p>Thank you for your interest in our industry insights</p>
                </div>
                <div class="content">
                    <h2>Your Free Download</h2>
                    <h3>{content_title}</h3>
                    <p>{content_description}</p>
                    
                    <div class="download-section">
                        <h4>🎯 Download Your Content</h4>
                        <a href="{self.platform_url}{download_url}" style="background: #6366f1; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; font-weight: bold;">Download Now</a>
                    </div>

                    <p>While you're here, explore Oil & Gas Finder - the leading B2B platform for oil and gas professionals:</p>
                    
                    <ul>
                        <li>🔍 <strong>Find Trading Partners:</strong> Connect with verified oil and gas traders worldwide</li>
                        <li>📈 <strong>Market Intelligence:</strong> Access real-time pricing and market analysis</li>
                        <li>🤝 <strong>Business Opportunities:</strong> Discover new trading opportunities daily</li>
                        <li>💡 <strong>Industry Insights:</strong> Stay ahead with expert analysis and reports</li>
                    </ul>
                    
                    <a href="{self.platform_url}/register" style="background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Join Oil & Gas Finder Free</a>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 14px; color: #6b7280;">
                        Stay informed with industry-leading insights<br>
                        The Oil & Gas Finder Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)

# Create global email service instance
email_service = EmailService()
