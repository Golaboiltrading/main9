from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_database

router = APIRouter()

# Analytics Data Models
class PageViewData(BaseModel):
    path: str
    title: str
    timestamp: int
    userId: Optional[str] = None
    sessionId: str
    referrer: Optional[str] = None
    userAgent: Optional[str] = None

class EventData(BaseModel):
    event: str
    parameters: Dict[str, Any]

class LeadData(BaseModel):
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    formType: str
    source: str
    timestamp: int

class ConversionData(BaseModel):
    conversionType: str
    value: float
    currency: str = "USD"
    userId: Optional[str] = None
    sessionId: str
    timestamp: int

# Analytics Tracking Endpoints

@router.post("/api/analytics/pageview")
async def track_pageview(
    pageview_data: PageViewData,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Track page views for analytics"""
    try:
        # Store in database
        await db.analytics_pageviews.insert_one({
            **pageview_data.dict(),
            "created_at": datetime.utcnow()
        })
        
        # Update user session data
        if pageview_data.userId:
            await db.user_sessions.update_one(
                {"user_id": pageview_data.userId, "session_id": pageview_data.sessionId},
                {
                    "$set": {"last_activity": datetime.utcnow()},
                    "$inc": {"page_views": 1},
                    "$push": {"pages_visited": pageview_data.path}
                },
                upsert=True
            )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analytics/event")
async def track_event(
    event_data: EventData,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Track custom events for analytics"""
    try:
        # Store in database
        await db.analytics_events.insert_one({
            **event_data.dict(),
            "created_at": datetime.utcnow()
        })
        
        # Update conversion funnel data if applicable
        if event_data.event in ['lead_generated', 'conversion', 'signup_started']:
            await update_conversion_funnel(db, event_data)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/leads")
async def capture_lead(
    lead_data: LeadData,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Capture and store lead information"""
    try:
        # Check if lead already exists
        existing_lead = await db.leads.find_one({"email": lead_data.email})
        
        if existing_lead:
            # Update existing lead with new interaction
            await db.leads.update_one(
                {"email": lead_data.email},
                {
                    "$set": {
                        "last_interaction": datetime.utcnow(),
                        "last_form_type": lead_data.formType,
                        "last_source": lead_data.source
                    },
                    "$inc": {"interaction_count": 1},
                    "$push": {
                        "interactions": {
                            "form_type": lead_data.formType,
                            "source": lead_data.source,
                            "timestamp": datetime.utcnow()
                        }
                    }
                }
            )
            lead_id = existing_lead["_id"]
        else:
            # Create new lead
            lead_doc = {
                **lead_data.dict(),
                "created_at": datetime.utcnow(),
                "last_interaction": datetime.utcnow(),
                "interaction_count": 1,
                "status": "new",
                "lead_score": calculate_lead_score(lead_data.formType),
                "interactions": [{
                    "form_type": lead_data.formType,
                    "source": lead_data.source,
                    "timestamp": datetime.utcnow()
                }]
            }
            result = await db.leads.insert_one(lead_doc)
            lead_id = result.inserted_id
        
        # Track lead generation event
        await db.analytics_events.insert_one({
            "event": "lead_captured",
            "parameters": {
                "lead_id": str(lead_id),
                "form_type": lead_data.formType,
                "source": lead_data.source,
                "is_new_lead": not bool(existing_lead)
            },
            "created_at": datetime.utcnow()
        })
        
        return {"status": "success", "lead_id": str(lead_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/newsletter/subscribe")
async def newsletter_subscribe(
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Newsletter subscription endpoint"""
    try:
        email = data.get("email")
        source = data.get("source", "newsletter")
        
        # Check if already subscribed
        existing = await db.newsletter_subscribers.find_one({"email": email})
        
        if not existing:
            await db.newsletter_subscribers.insert_one({
                "email": email,
                "source": source,
                "subscribed_at": datetime.utcnow(),
                "status": "active"
            })
        
        # Also capture as lead
        lead_data = LeadData(
            email=email,
            formType="newsletter",
            source=source,
            timestamp=int(datetime.utcnow().timestamp())
        )
        await capture_lead(lead_data, db)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Reporting Endpoints

@router.get("/api/analytics/dashboard")
async def get_analytics_dashboard(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get analytics dashboard data"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Page views
        pageviews = await db.analytics_pageviews.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Unique visitors
        unique_visitors = len(await db.analytics_pageviews.distinct(
            "sessionId", 
            {"created_at": {"$gte": start_date}}
        ))
        
        # New leads
        new_leads = await db.leads.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Conversions (premium signups)
        conversions = await db.analytics_events.count_documents({
            "event": "conversion",
            "created_at": {"$gte": start_date}
        })
        
        # Top pages
        top_pages_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {"_id": "$path", "views": {"$sum": 1}}},
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]
        top_pages = await db.analytics_pageviews.aggregate(top_pages_pipeline).to_list(10)
        
        # Lead sources
        lead_sources_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        lead_sources = await db.leads.aggregate(lead_sources_pipeline).to_list(None)
        
        # Daily trends
        daily_trends_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "pageviews": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        daily_trends = await db.analytics_pageviews.aggregate(daily_trends_pipeline).to_list(None)
        
        return {
            "overview": {
                "pageviews": pageviews,
                "unique_visitors": unique_visitors,
                "new_leads": new_leads,
                "conversions": conversions,
                "conversion_rate": (conversions / unique_visitors * 100) if unique_visitors > 0 else 0
            },
            "top_pages": top_pages,
            "lead_sources": lead_sources,
            "daily_trends": daily_trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/leads")
async def get_leads_analytics(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed leads analytics"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Lead funnel analysis
        funnel_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": "$formType",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$lead_score"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        lead_funnel = await db.leads.aggregate(funnel_pipeline).to_list(None)
        
        # Lead quality distribution
        quality_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$bucket": {
                    "groupBy": "$lead_score",
                    "boundaries": [0, 25, 50, 75, 100],
                    "default": "100+",
                    "output": {"count": {"$sum": 1}}
                }
            }
        ]
        lead_quality = await db.leads.aggregate(quality_pipeline).to_list(None)
        
        # Conversion rates by source
        conversion_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": "$source",
                    "leads": {"$sum": 1},
                    "converted": {
                        "$sum": {"$cond": [{"$gte": ["$lead_score", 75]}, 1, 0]}
                    }
                }
            },
            {
                "$project": {
                    "source": "$_id",
                    "leads": 1,
                    "converted": 1,
                    "conversion_rate": {
                        "$multiply": [{"$divide": ["$converted", "$leads"]}, 100]
                    }
                }
            },
            {"$sort": {"conversion_rate": -1}}
        ]
        conversion_rates = await db.leads.aggregate(conversion_pipeline).to_list(None)
        
        return {
            "lead_funnel": lead_funnel,
            "lead_quality_distribution": lead_quality,
            "conversion_rates_by_source": conversion_rates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

async def update_conversion_funnel(db: AsyncIOMotorDatabase, event_data: EventData):
    """Update conversion funnel tracking"""
    funnel_data = {
        "event": event_data.event,
        "user_id": event_data.parameters.get("userId"),
        "session_id": event_data.parameters.get("sessionId"),
        "timestamp": datetime.utcnow()
    }
    
    await db.conversion_funnel.insert_one(funnel_data)

def calculate_lead_score(form_type: str) -> int:
    """Calculate lead score based on form type and other factors"""
    scores = {
        "newsletter": 20,
        "demo_request": 80,
        "premium_inquiry": 90,
        "contact_form": 50,
        "whitepaper_download": 60,
        "webinar_registration": 70
    }
    return scores.get(form_type, 30)

# Lead scoring update endpoint
@router.post("/api/analytics/update-lead-score")
async def update_lead_score(
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update lead score based on actions"""
    try:
        lead_id = data.get("lead_id")
        action = data.get("action")
        score_delta = data.get("score_delta", 0)
        
        await db.leads.update_one(
            {"_id": lead_id},
            {
                "$inc": {"lead_score": score_delta},
                "$push": {
                    "scoring_events": {
                        "action": action,
                        "score_delta": score_delta,
                        "timestamp": datetime.utcnow()
                    }
                }
            }
        )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))