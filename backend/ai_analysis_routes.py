from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import JSONResponse
import os
import json
import tempfile
from typing import Optional
import PyPDF2
import pytesseract
from PIL import Image
import io

router = APIRouter()

# Mock Perplexity AI integration (replace with actual API when key is provided)
def analyze_with_perplexity(text_content: str) -> dict:
    """
    Analyze document content using Perplexity AI
    This is a mock implementation - replace with actual Perplexity API call
    """
    
    # Mock analysis based on content keywords
    analysis = {
        "product_type": "Unknown",
        "grade": "Not specified",
        "api_gravity": "Not found",
        "sulfur_content": "Not found",
        "specifications": {},
        "red_flags": [],
        "recommendations": [],
        "market_insights": "No insights available",
        "confidence_score": 0.0
    }
    
    content_lower = text_content.lower()
    
    # Product type identification
    if "crude oil" in content_lower or "crude" in content_lower:
        analysis["product_type"] = "Crude Oil"
        
        # API Gravity detection
        api_matches = ["api", "gravity", "°api", "degrees api"]
        for line in text_content.split('\n'):
            line_lower = line.lower()
            if any(term in line_lower for term in api_matches):
                # Extract API gravity value
                import re
                api_match = re.search(r'(\d+\.?\d*)\s*°?\s*api', line_lower)
                if api_match:
                    api_value = float(api_match.group(1))
                    analysis["api_gravity"] = f"{api_value}° API"
                    
                    if api_value < 22:
                        analysis["grade"] = "Heavy Crude"
                        analysis["recommendations"].append("Heavy crude - suitable for specialized refineries")
                    elif api_value > 31:
                        analysis["grade"] = "Light Crude"
                        analysis["recommendations"].append("Light crude - premium grade for most refineries")
                    else:
                        analysis["grade"] = "Medium Crude"
                        analysis["recommendations"].append("Medium crude - good for standard refining")
                    
                    analysis["confidence_score"] += 0.3
        
        # Sulfur content detection
        sulfur_terms = ["sulfur", "sulphur", "s content", "sulfur content"]
        for line in text_content.split('\n'):
            line_lower = line.lower()
            if any(term in line_lower for term in sulfur_terms):
                import re
                sulfur_match = re.search(r'(\d+\.?\d*)\s*%?\s*wt', line_lower)
                if sulfur_match:
                    sulfur_value = float(sulfur_match.group(1))
                    analysis["sulfur_content"] = f"{sulfur_value}% wt"
                    
                    if sulfur_value > 0.5:
                        analysis["grade"] += " (Sour)"
                        analysis["red_flags"].append("High sulfur content - requires specialized processing")
                    else:
                        analysis["grade"] += " (Sweet)"
                        analysis["recommendations"].append("Low sulfur content - premium sweet crude")
                    
                    analysis["confidence_score"] += 0.2
    
    elif "natural gas" in content_lower or "lng" in content_lower:
        analysis["product_type"] = "Natural Gas/LNG"
        analysis["recommendations"].append("Natural gas product - verify BTU content and composition")
        analysis["confidence_score"] += 0.3
    
    elif "gasoline" in content_lower or "petrol" in content_lower:
        analysis["product_type"] = "Gasoline"
        analysis["recommendations"].append("Refined product - check octane rating and additives")
        analysis["confidence_score"] += 0.3
    
    elif "diesel" in content_lower or "gasoil" in content_lower:
        analysis["product_type"] = "Diesel/Gas Oil"
        analysis["recommendations"].append("Diesel fuel - verify cetane number and cold flow properties")
        analysis["confidence_score"] += 0.3
    
    # Red flag detection
    red_flag_terms = [
        ("expired", "Document appears to contain expired certificates"),
        ("invalid", "Invalid or questionable certifications detected"),
        ("suspicious", "Suspicious content patterns detected"),
        ("fake", "Potential document authenticity issues"),
        ("counterfeit", "Possible counterfeit documentation"),
        ("sanction", "Potential sanctions-related concerns"),
        ("embargo", "Embargo or trade restriction warnings"),
        ("contaminated", "Product contamination indicators"),
        ("off-spec", "Off-specification product warnings"),
        ("rejected", "Previously rejected product indicators")
    ]
    
    for term, warning in red_flag_terms:
        if term in content_lower:
            analysis["red_flags"].append(warning)
            analysis["confidence_score"] -= 0.1
    
    # Market insights
    if analysis["product_type"] != "Unknown":
        market_insights = {
            "Crude Oil": "Current crude oil markets show strong demand. Light sweet crudes command premium pricing.",
            "Natural Gas/LNG": "LNG markets remain tight with strong Asian demand. Consider long-term contracts.",
            "Gasoline": "Gasoline markets affected by seasonal demand patterns. Summer driving season approaching.",
            "Diesel/Gas Oil": "Diesel demand strong in marine and industrial sectors. Supply constraints continue."
        }
        analysis["market_insights"] = market_insights.get(analysis["product_type"], "Market conditions vary by region and season.")
    
    # General recommendations
    if not analysis["red_flags"]:
        analysis["recommendations"].append("Document appears clean - proceed with standard due diligence")
    else:
        analysis["recommendations"].append("CAUTION: Red flags detected - conduct thorough verification")
    
    analysis["recommendations"].extend([
        "Verify all certificates with issuing authorities",
        "Conduct independent quality testing",
        "Confirm sanctions compliance",
        "Review transportation and insurance requirements"
    ])
    
    # Ensure confidence score is reasonable
    analysis["confidence_score"] = max(0.0, min(1.0, analysis["confidence_score"]))
    
    return analysis

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_image(file_content: bytes) -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@router.post("/api/ai/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze uploaded document for oil & gas technical specifications
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload PDF, JPG, or PNG files only."
            )
        
        # Validate file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 10MB."
            )
        
        # Extract text based on file type
        if file.content_type == 'application/pdf':
            text_content = extract_text_from_pdf(file_content)
        else:
            text_content = extract_text_from_image(file_content)
        
        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document. Please ensure the document contains readable text."
            )
        
        # Analyze with AI (mock implementation)
        analysis = analyze_with_perplexity(text_content)
        
        # Log analysis for monitoring
        print(f"Document analyzed: {file.filename}")
        print(f"Analysis confidence: {analysis['confidence_score']}")
        
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "analysis": analysis,
            "extracted_text_length": len(text_content),
            "timestamp": "2024-12-01T00:00:00Z"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during document analysis. Please try again."
        )

@router.get("/api/ai/analysis-history")
async def get_analysis_history():
    """Get user's document analysis history"""
    # Mock data - in real implementation, fetch from database
    return JSONResponse(content={
        "status": "success",
        "analyses": [
            {
                "id": "1",
                "filename": "crude_oil_spec.pdf",
                "product_type": "Light Sweet Crude",
                "analyzed_at": "2024-11-30T15:30:00Z",
                "red_flags_count": 0
            },
            {
                "id": "2", 
                "filename": "gas_certificate.jpg",
                "product_type": "Natural Gas",
                "analyzed_at": "2024-11-29T10:15:00Z",
                "red_flags_count": 1
            }
        ]
    })

@router.get("/api/ai/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats for analysis"""
    return JSONResponse(content={
        "status": "success",
        "formats": [
            {
                "type": "PDF",
                "extensions": [".pdf"],
                "max_size": "10MB",
                "description": "Product specifications, certificates, lab reports"
            },
            {
                "type": "Images",
                "extensions": [".jpg", ".jpeg", ".png"],
                "max_size": "10MB", 
                "description": "Scanned documents, photos of certificates"
            }
        ],
        "analysis_features": [
            "Product type identification",
            "Technical specification extraction",
            "Red flag detection",
            "Quality assessment",
            "Market insights",
            "Trading recommendations"
        ]
    })

# Mock news endpoint for NewsBar component
@router.get("/api/news/oil-gas")
async def get_oil_gas_news():
    """Get latest oil and gas industry news"""
    
    # Mock news data - in real implementation, integrate with news APIs
    mock_articles = [
        {
            "title": "Oil Prices Rise 3% on Supply Concerns",
            "summary": "Crude oil futures gained after reports of production cuts from major exporters affecting global supply chains.",
            "source": "Energy News",
            "time": "2 hours ago",
            "category": "Market",
            "sentiment": "positive",
            "url": "#"
        },
        {
            "title": "Natural Gas Demand Surges in Winter Season",
            "summary": "European gas prices hit seasonal highs as winter demand increases across the region amid cold weather forecasts.",
            "source": "Gas Daily",
            "time": "4 hours ago",
            "category": "Natural Gas", 
            "sentiment": "positive",
            "url": "#"
        },
        {
            "title": "New LNG Terminal Opens in Texas",
            "summary": "Major infrastructure development boosts US export capacity by 15 million tons per year, strengthening global position.",
            "source": "LNG Journal",
            "time": "6 hours ago",
            "category": "Infrastructure",
            "sentiment": "positive", 
            "url": "#"
        },
        {
            "title": "OPEC+ Meeting Scheduled for Next Week",
            "summary": "Oil ministers to discuss production quotas amid changing market conditions and global economic outlook.",
            "source": "OPEC News", 
            "time": "8 hours ago",
            "category": "Policy",
            "sentiment": "neutral",
            "url": "#"
        },
        {
            "title": "Renewable Energy Investment Hits Record High",
            "summary": "Global investment in clean energy technologies reaches $2.8 trillion in 2024, reshaping energy landscape.",
            "source": "Energy Transition",
            "time": "1 day ago",
            "category": "Renewables",
            "sentiment": "positive",
            "url": "#"
        },
        {
            "title": "Geopolitical Tensions Affect Oil Trade Routes", 
            "summary": "Shipping companies adjust routes as regional conflicts impact key maritime passages and insurance costs.",
            "source": "Maritime Oil",
            "time": "1 day ago",
            "category": "Geopolitics",
            "sentiment": "negative",
            "url": "#"
        }
    ]
    
    return JSONResponse(content={
        "status": "success",
        "articles": mock_articles,
        "total": len(mock_articles),
        "last_updated": "2024-12-01T00:00:00Z"
    })