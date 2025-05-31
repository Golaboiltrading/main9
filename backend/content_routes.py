from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_database
import re

router = APIRouter()

# Content Models
class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: str
    content: str
    category: str
    keywords: str
    author: str = "Oil & Gas Finder Team"
    featured_image: Optional[str] = None
    read_time: int = 5
    published: bool = False
    seo_meta: Optional[Dict[str, Any]] = None

class LocationData(BaseModel):
    name: str
    slug: str
    description: str
    address: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None
    market_data: Optional[Dict[str, Any]] = None

class ProductData(BaseModel):
    name: str
    slug: str
    description: str
    category: str
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    daily_volume: Optional[str] = None
    active_listings: Optional[int] = None

# Blog Content Routes

@router.get("/api/blog/posts")
async def get_blog_posts(
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = None,
    published_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get blog posts with pagination and filtering"""
    try:
        filter_query = {}
        if published_only:
            filter_query["published"] = True
        if category:
            filter_query["category"] = category

        posts = await db.blog_posts.find(filter_query)\
                                  .sort("created_at", -1)\
                                  .skip(offset)\
                                  .limit(limit)\
                                  .to_list(limit)
        
        total = await db.blog_posts.count_documents(filter_query)
        
        return {
            "posts": posts,
            "total": total,
            "has_more": (offset + limit) < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/blog/posts/{slug}")
async def get_blog_post(
    slug: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get individual blog post by slug"""
    try:
        post = await db.blog_posts.find_one({"slug": slug, "published": True})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get related posts
        related_posts = await db.blog_posts.find({
            "category": post["category"],
            "slug": {"$ne": slug},
            "published": True
        }).limit(3).to_list(3)
        
        # Update view count
        await db.blog_posts.update_one(
            {"_id": post["_id"]},
            {"$inc": {"views": 1}}
        )
        
        return {
            "post": post,
            "related_posts": related_posts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/blog/categories")
async def get_blog_categories(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all blog categories with post counts"""
    try:
        pipeline = [
            {"$match": {"published": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = await db.blog_posts.aggregate(pipeline).to_list(None)
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Location-based Content Routes

@router.get("/api/locations/{location}")
async def get_location_data(
    location: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get location-specific trading data"""
    try:
        # Get location info
        location_doc = await db.locations.find_one({"slug": location})
        
        if not location_doc:
            # Create default location data
            location_name = location.replace('-', ' ').title()
            location_doc = {
                "name": location_name,
                "slug": location,
                "description": f"Oil and gas trading hub in {location_name}",
                "address": get_default_address(location),
                "phone": "+1-713-XXX-XXXX"
            }
        
        # Get market data (could be real-time from external API)
        market_data = await get_market_data_for_location(location)
        
        return {
            "location": location_doc,
            "market_data": market_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/products/{product_type}")
async def get_product_data(
    product_type: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get product-specific trading data"""
    try:
        # Get product info
        product_doc = await db.products.find_one({"slug": product_type})
        
        if not product_doc:
            # Create default product data
            product_name = product_type.replace('-', ' ').title()
            product_doc = {
                "name": product_name,
                "slug": product_type,
                "description": f"Trade {product_name.lower()} with verified buyers and sellers",
                "category": get_product_category(product_type)
            }
        
        # Get market data for product
        market_data = await get_market_data_for_product(product_type)
        product_doc.update(market_data)
        
        return product_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Management Routes (Admin)

@router.post("/api/admin/blog/posts")
async def create_blog_post(
    post_data: BlogPost,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new blog post (admin only)"""
    try:
        # Generate slug if not provided
        if not post_data.slug:
            post_data.slug = generate_slug(post_data.title)
        
        # Check if slug already exists
        existing = await db.blog_posts.find_one({"slug": post_data.slug})
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
        
        # Calculate read time
        word_count = len(post_data.content.split())
        post_data.read_time = max(1, word_count // 200)  # Average reading speed
        
        # Create post document
        post_doc = {
            **post_data.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 0
        }
        
        result = await db.blog_posts.insert_one(post_doc)
        
        return {"status": "success", "post_id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SEO Content Generation Routes

@router.get("/api/seo/content-suggestions")
async def get_content_suggestions(
    topic: str = Query(..., description="Content topic"),
    content_type: str = Query(default="blog", description="Type of content"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get SEO-optimized content suggestions"""
    try:
        suggestions = {
            "titles": generate_seo_titles(topic),
            "keywords": generate_keywords(topic),
            "meta_descriptions": generate_meta_descriptions(topic),
            "headings": generate_headings(topic),
            "content_outline": generate_content_outline(topic)
        }
        
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/content/templates")
async def get_content_templates(
    template_type: str = Query(..., description="Type of template needed"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get content templates for different page types"""
    try:
        templates = {
            "location_page": get_location_page_template(),
            "product_page": get_product_page_template(),
            "blog_post": get_blog_post_template(),
            "landing_page": get_landing_page_template()
        }
        
        return templates.get(template_type, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def get_default_address(location: str) -> Dict[str, Any]:
    """Get default address data for location"""
    addresses = {
        "houston-tx": {
            "street": "1000 Louisiana St",
            "city": "Houston",
            "state": "TX",
            "zip": "77002",
            "country": "US",
            "lat": 29.7604,
            "lng": -95.3698
        },
        "dubai-uae": {
            "street": "Sheikh Zayed Road",
            "city": "Dubai",
            "state": "Dubai",
            "zip": "00000",
            "country": "AE",
            "lat": 25.2048,
            "lng": 55.2708
        },
        "singapore": {
            "street": "Marina Bay",
            "city": "Singapore",
            "state": "Singapore",
            "zip": "018956",
            "country": "SG",
            "lat": 1.2839,
            "lng": 103.8517
        }
    }
    return addresses.get(location, {})

async def get_market_data_for_location(location: str) -> Dict[str, Any]:
    """Get mock market data for location"""
    # In real implementation, this would fetch from external APIs
    return {
        "crude_oil_price": 75.25,
        "crude_oil_change": 1.2,
        "natural_gas_price": 2.85,
        "natural_gas_change": -0.8,
        "active_traders": 145,
        "new_traders_today": 8,
        "daily_volume": "2.5M",
        "volume_change": 5.2
    }

async def get_market_data_for_product(product_type: str) -> Dict[str, Any]:
    """Get mock market data for product"""
    # Mock data - in real implementation, fetch from market data APIs
    base_prices = {
        "crude-oil": 75.25,
        "natural-gas": 2.85,
        "lng": 12.50,
        "gasoline": 2.15,
        "diesel": 2.95
    }
    
    price = base_prices.get(product_type, 50.00)
    
    return {
        "current_price": price,
        "price_change": 1.2,
        "daily_volume": "1.2M BBL",
        "volume_change": 3.5,
        "active_listings": 125,
        "new_listings": 15
    }

def get_product_category(product_type: str) -> str:
    """Get category for product type"""
    categories = {
        "crude-oil": "Crude Oil",
        "natural-gas": "Natural Gas",
        "lng": "LNG",
        "gasoline": "Refined Products",
        "diesel": "Refined Products",
        "jet-fuel": "Refined Products"
    }
    return categories.get(product_type, "Energy Products")

def generate_seo_titles(topic: str) -> List[str]:
    """Generate SEO-optimized titles"""
    return [
        f"{topic.title()} Trading Platform | Global Market Access",
        f"Best {topic.title()} Prices | Real-time Market Data",
        f"{topic.title()} Buyers and Sellers | Verified Trading Network",
        f"Trade {topic.title()} Online | Secure Energy Trading Platform",
        f"{topic.title()} Market Analysis | Industry Insights & Trends"
    ]

def generate_keywords(topic: str) -> List[str]:
    """Generate relevant keywords"""
    base_keywords = [f"{topic} trading", f"{topic} market", f"{topic} prices"]
    location_keywords = [f"{topic} houston", f"{topic} dubai", f"{topic} singapore"]
    action_keywords = [f"buy {topic}", f"sell {topic}", f"{topic} platform"]
    
    return base_keywords + location_keywords + action_keywords

def generate_meta_descriptions(topic: str) -> List[str]:
    """Generate meta descriptions"""
    return [
        f"Trade {topic} with verified buyers and sellers worldwide. Real-time pricing, market data, and secure trading connections on our global platform.",
        f"Find the best {topic} prices and trading opportunities. Connect with trusted energy professionals in the global {topic} market.",
        f"Global {topic} trading platform with real-time market data. Join thousands of energy professionals trading {topic} securely online."
    ]

def generate_headings(topic: str) -> List[str]:
    """Generate content headings"""
    return [
        f"What is {topic.title()} Trading?",
        f"How to Trade {topic.title()} Online",
        f"{topic.title()} Market Trends",
        f"Benefits of Online {topic.title()} Trading",
        f"Getting Started with {topic.title()} Trading"
    ]

def generate_content_outline(topic: str) -> Dict[str, List[str]]:
    """Generate content outline"""
    return {
        "introduction": [
            f"Overview of {topic} trading",
            "Market importance",
            "Trading opportunities"
        ],
        "market_analysis": [
            "Current market conditions",
            "Price trends",
            "Supply and demand factors"
        ],
        "trading_guide": [
            "How to start trading",
            "Platform features",
            "Safety and verification"
        ],
        "conclusion": [
            "Future outlook",
            "Call to action"
        ]
    }

def get_location_page_template() -> Dict[str, str]:
    """Get location page content template"""
    return {
        "hero_title": "Oil & Gas Trading in {location}",
        "hero_description": "Connect with verified buyers and sellers in {location}'s energy market. Access real-time pricing, market insights, and trading opportunities.",
        "benefits_section": "Why Trade in {location}?",
        "market_data_section": "{location} Market Overview"
    }

def get_product_page_template() -> Dict[str, str]:
    """Get product page content template"""
    return {
        "hero_title": "{product} Trading Platform",
        "hero_description": "Trade {product} with verified buyers and sellers worldwide. Real-time market data, competitive pricing, and secure trading opportunities.",
        "features_section": "Why Choose Our {product} Trading Platform?",
        "market_data_section": "{product} Market Data"
    }

def get_blog_post_template() -> Dict[str, str]:
    """Get blog post content template"""
    return {
        "title_format": "{topic} Market Analysis | {date}",
        "introduction": "Introduction to {topic} market conditions...",
        "market_analysis": "Current market trends and analysis...",
        "trading_opportunities": "Trading opportunities and strategies...",
        "conclusion": "Summary and outlook..."
    }

def get_landing_page_template() -> Dict[str, str]:
    """Get landing page content template"""
    return {
        "hero_section": "Global {focus} Trading Platform",
        "value_proposition": "Connect with verified traders worldwide",
        "features_section": "Platform Features and Benefits",
        "cta_section": "Start Trading Today"
    }