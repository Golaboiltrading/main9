from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional, List
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

router = APIRouter()

# SEO and Sitemap Generation Routes

@router.get("/sitemap.xml", response_class=Response)
async def generate_sitemap():
    """Generate dynamic XML sitemap for better SEO indexing"""
    
    # Create root sitemap element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    urlset.set("xsi:schemaLocation", "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")
    
    base_url = "https://oilgasfinder.com"  # Updated domain
    
    # Static pages
    static_pages = [
        {"url": "/", "priority": "1.0", "changefreq": "daily"},
        {"url": "/browse", "priority": "0.9", "changefreq": "daily"},
        {"url": "/market-data", "priority": "0.8", "changefreq": "hourly"},
        {"url": "/premium", "priority": "0.7", "changefreq": "weekly"},
        {"url": "/register", "priority": "0.6", "changefreq": "monthly"},
        {"url": "/login", "priority": "0.5", "changefreq": "monthly"},
    ]
    
    for page in static_pages:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}{page['url']}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = page['changefreq']
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = page['priority']
    
    # Dynamic product pages
    product_types = [
        "crude-oil", "natural-gas", "lng", "lpg", 
        "gasoline", "diesel", "jet-fuel", "gas-condensate"
    ]
    
    for product in product_types:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}/products/{product}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = "weekly"
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = "0.8"
    
    # Location-based pages
    locations = [
        "houston-tx", "dubai-uae", "singapore", "london-uk", 
        "rotterdam-netherlands", "cushing-ok"
    ]
    
    for location in locations:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}/locations/{location}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = "weekly"
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = "0.7"
    
    # Product + Location combinations for long-tail keywords
    for product in product_types[:4]:  # Limit to avoid too many URLs
        for location in locations[:3]:  # Top 3 locations
            url_elem = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_elem, "loc")
            loc.text = f"{base_url}/trading/{product}/{location}"
            
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
            
            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = "weekly"
            
            priority = ET.SubElement(url_elem, "priority")
            priority.text = "0.6"
    
    # Convert to pretty XML
    rough_string = ET.tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    # Remove empty lines and return
    clean_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    return Response(
        content=clean_xml,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@router.get("/api/seo/keywords")
async def get_seo_keywords(
    product_type: Optional[str] = None,
    location: Optional[str] = None
):
    """Generate SEO-optimized keywords for pages"""
    
    base_keywords = [
        "oil trading", "gas trading", "crude oil", "natural gas",
        "petroleum products", "energy trading", "oil market", "gas market"
    ]
    
    location_keywords = {
        "houston": ["Houston oil", "Texas crude", "Gulf Coast trading"],
        "dubai": ["Dubai oil", "Middle East crude", "UAE trading"],
        "singapore": ["Singapore trading", "Asia Pacific oil", "Southeast Asia gas"],
        "london": ["London oil", "Brent crude", "Europe trading"],
        "rotterdam": ["Rotterdam trading", "European gas", "Netherlands oil"],
        "cushing": ["Cushing oil", "WTI crude", "Oklahoma trading"]
    }
    
    product_keywords = {
        "crude_oil": ["crude oil trading", "oil futures", "petroleum crude"],
        "natural_gas": ["natural gas trading", "gas futures", "LNG trading"],
        "lng": ["LNG trading", "liquefied natural gas", "LNG export"],
        "gasoline": ["gasoline trading", "petrol trading", "refined products"],
        "diesel": ["diesel trading", "gasoil trading", "heating oil"],
        "jet_fuel": ["jet fuel trading", "aviation fuel", "kerosene trading"]
    }
    
    keywords = base_keywords.copy()
    
    if location:
        location_key = location.lower().replace('-', ' ').split()[0]
        if location_key in location_keywords:
            keywords.extend(location_keywords[location_key])
    
    if product_type:
        if product_type in product_keywords:
            keywords.extend(product_keywords[product_type])
    
    return {
        "primary_keywords": keywords[:10],
        "secondary_keywords": keywords[10:20] if len(keywords) > 10 else [],
        "long_tail_keywords": [
            f"{product_type} trading in {location}" if product_type and location else None,
            f"{location} oil and gas market" if location else None,
            f"best {product_type} prices" if product_type else None
        ]
    }

@router.get("/api/seo/meta-data")
async def get_page_meta_data(
    page_type: str = Query(..., description="Type of page (home, browse, product, location)"),
    product_type: Optional[str] = None,
    location: Optional[str] = None
):
    """Generate dynamic meta data for pages"""
    
    meta_templates = {
        "home": {
            "title": "Oil & Gas Finder - Global Trading Platform | Connect Buyers & Sellers",
            "description": "Premier global oil & gas trading platform connecting buyers and sellers worldwide. Find crude oil, natural gas, LNG, and petroleum products with real-time market data.",
            "keywords": "oil trading, gas trading, crude oil, natural gas, LNG, petroleum products"
        },
        "browse": {
            "title": "Browse Oil & Gas Traders | Global Energy Trading Network",
            "description": "Discover verified oil and gas traders worldwide. Connect with buyers and sellers of crude oil, natural gas, LNG, and petroleum products.",
            "keywords": "oil traders, gas traders, energy trading network, petroleum buyers, oil sellers"
        },
        "product": {
            "title": f"{product_type.replace('_', ' ').title()} Trading | Oil & Gas Finder" if product_type else "Product Trading",
            "description": f"Trade {product_type.replace('_', ' ')} with verified buyers and sellers worldwide. Real-time pricing and secure connections." if product_type else "Product trading platform",
            "keywords": f"{product_type} trading, {product_type} market, {product_type} prices" if product_type else "product trading"
        },
        "location": {
            "title": f"Oil & Gas Trading in {location.replace('-', ' ').title()} | Energy Market" if location else "Location Trading",
            "description": f"Connect with oil and gas traders in {location.replace('-', ' ').title()}. Local market insights and trading opportunities." if location else "Location-based trading",
            "keywords": f"{location} oil trading, {location} gas market, {location} energy trading" if location else "location trading"
        }
    }
    
    if page_type not in meta_templates:
        raise HTTPException(status_code=400, detail="Invalid page type")
    
    meta_data = meta_templates[page_type].copy()
    
    # Enhance with location and product data
    if location and product_type and page_type == "product":
        location_name = location.replace('-', ' ').title()
        product_name = product_type.replace('_', ' ').title()
        meta_data["title"] = f"{product_name} Trading in {location_name} | Oil & Gas Finder"
        meta_data["description"] = f"Trade {product_name.lower()} in {location_name}. Connect with local buyers and sellers. Real-time market data and secure trading platform."
        meta_data["keywords"] = f"{product_type} trading {location}, {location} {product_type} market, {product_name} {location_name}"
    
    return meta_data

@router.get("/api/seo/schema-data")
async def get_schema_data(
    schema_type: str = Query(..., description="Type of schema (organization, product, localbusiness)"),
    product_type: Optional[str] = None,
    location: Optional[str] = None,
    price: Optional[float] = None
):
    """Generate structured data for SEO"""
    
    base_url = "https://oilgasfinder.com"  # Updated domain
    
    if schema_type == "organization":
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Oil & Gas Finder",
            "description": "Premier global oil & gas trading platform",
            "url": base_url,
            "logo": f"{base_url}/logo.png",
            "sameAs": [
                "https://linkedin.com/company/oil-gas-finder",
                "https://twitter.com/oilgasfinder"
            ],
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+1-713-XXX-XXXX",
                "contactType": "customer service"
            }
        }
    
    elif schema_type == "product" and product_type:
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_type.replace('_', ' ').title(),
            "description": f"Trade {product_type.replace('_', ' ')} with verified buyers and sellers",
            "category": "Energy/Oil & Gas",
            "brand": {
                "@type": "Brand",
                "name": "Oil & Gas Finder"
            }
        }
        
        if price:
            schema["offers"] = {
                "@type": "Offer",
                "priceCurrency": "USD",
                "price": price,
                "availability": "https://schema.org/InStock"
            }
        
        return schema
    
    elif schema_type == "localbusiness" and location:
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"Oil & Gas Finder - {location.replace('-', ' ').title()}",
            "description": f"Oil and gas trading services in {location.replace('-', ' ').title()}",
            "url": f"{base_url}/locations/{location}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": location.replace('-', ' ').title()
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid schema type or missing required parameters")

# Generate robots.txt dynamically
@router.get("/robots.txt", response_class=Response)
async def get_robots_txt():
    """Generate robots.txt file"""
    
    robots_content = """User-agent: *
Allow: /

# Allow all crawlers access to key pages
Allow: /api/listings
Allow: /browse
Allow: /market-data
Allow: /premium

# Block sensitive areas
Disallow: /api/auth/
Disallow: /api/user/
Disallow: /api/connections/
Disallow: /dashboard/

# XML Sitemap location
Sitemap: https://oilgasfinder.com/sitemap.xml

# Crawl delay for respectful crawling
Crawl-delay: 1

# Special rules for specific bots
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1"""
    
    return Response(
        content=robots_content,
        media_type="text/plain",
        headers={"Cache-Control": "public, max-age=86400"}
    )