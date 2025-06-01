from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import PyPDF2
import io
import re
from PIL import Image
import pytesseract
from datetime import datetime
import json

router = APIRouter()

@router.post("/api/ai/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """AI-powered document analysis for oil & gas documents"""
    try:
        # Validate file type
        if file.content_type not in ['application/pdf', 'image/jpeg', 'image/png']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.content_type == 'application/pdf':
            text = extract_text_from_pdf(content)
        else:
            text = extract_text_from_image(content)
        
        # Perform AI analysis
        analysis_result = perform_ai_analysis(text, file.filename)
        
        return JSONResponse(content=analysis_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def extract_text_from_pdf(content):
    """Extract text from PDF files"""
    try:
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")

def extract_text_from_image(content):
    """Extract text from image files using OCR"""
    try:
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        # Return placeholder if OCR fails
        return "OCR extraction not available - manual text analysis required"

def perform_ai_analysis(text, filename):
    """Perform comprehensive AI analysis of oil & gas documents"""
    
    # Initialize analysis result
    analysis = {
        "filename": filename,
        "analysis_date": datetime.utcnow().isoformat(),
        "overall_score": 0,
        "summary": "",
        "product_classification": {},
        "red_flags": [],
        "technical_analysis": [],
        "market_insights": [],
        "recommendations": []
    }
    
    # Text preprocessing
    text_lower = text.lower()
    
    # Product Classification
    analysis["product_classification"] = classify_product(text_lower)
    
    # Red Flag Detection
    analysis["red_flags"] = detect_red_flags(text_lower, filename)
    
    # Technical Analysis
    analysis["technical_analysis"] = extract_technical_data(text_lower)
    
    # Market Insights
    analysis["market_insights"] = generate_market_insights(analysis["product_classification"])
    
    # Generate Recommendations
    analysis["recommendations"] = generate_recommendations(analysis)
    
    # Calculate Overall Score
    analysis["overall_score"] = calculate_overall_score(analysis)
    
    # Generate Summary
    analysis["summary"] = generate_summary(analysis)
    
    return analysis

def classify_product(text):
    """Classify oil & gas product type and specifications"""
    classification = {
        "type": "Unknown",
        "api_gravity": None,
        "sulfur_content": None,
        "grade": None,
        "origin": None
    }
    
    # Product type detection
    if any(term in text for term in ["crude oil", "crude", "petroleum"]):
        classification["type"] = "Crude Oil"
        
        # API Gravity detection
        api_pattern = r"api\s+gravity[:\s]*(\d+\.?\d*)"
        api_match = re.search(api_pattern, text)
        if api_match:
            api_value = float(api_match.group(1))
            classification["api_gravity"] = f"{api_value}°"
            
            if api_value < 22:
                classification["grade"] = "Heavy Crude"
            elif api_value > 31:
                classification["grade"] = "Light Crude"
            else:
                classification["grade"] = "Medium Crude"
    
    elif any(term in text for term in ["natural gas", "lng", "lpg"]):
        classification["type"] = "Natural Gas"
        if "lng" in text:
            classification["grade"] = "Liquefied Natural Gas"
        elif "lpg" in text:
            classification["grade"] = "Liquefied Petroleum Gas"
    
    elif any(term in text for term in ["gasoline", "petrol", "diesel", "jet fuel"]):
        classification["type"] = "Refined Products"
        if "gasoline" in text or "petrol" in text:
            classification["grade"] = "Gasoline"
        elif "diesel" in text:
            classification["grade"] = "Diesel"
        elif "jet fuel" in text:
            classification["grade"] = "Jet Fuel"
    
    # Sulfur content detection
    sulfur_pattern = r"sulfur[:\s]*(\d+\.?\d*)\s*(?:%|ppm|percent)"
    sulfur_match = re.search(sulfur_pattern, text)
    if sulfur_match:
        sulfur_value = float(sulfur_match.group(1))
        if "ppm" in text:
            classification["sulfur_content"] = f"{sulfur_value} ppm"
        else:
            classification["sulfur_content"] = f"{sulfur_value}%"
    
    # Origin detection
    origins = ["brent", "wti", "dubai", "urals", "maya", "canadian", "venezuelan", "iranian", "saudi", "kuwait"]
    for origin in origins:
        if origin in text:
            classification["origin"] = origin.title()
            break
    
    return classification

def detect_red_flags(text, filename):
    """Detect potential red flags and suspicious elements"""
    red_flags = []
    
    # Price-related red flags
    if any(term in text for term in ["below market", "special discount", "urgent sale", "distressed"]):
        red_flags.append({
            "type": "Pricing Anomaly",
            "description": "Document mentions below-market pricing or urgent sales terms",
            "severity": "High"
        })
    
    # Documentation red flags
    if any(term in text for term in ["draft", "preliminary", "estimated", "approximate"]):
        red_flags.append({
            "type": "Incomplete Documentation",
            "description": "Document appears to be draft or preliminary version",
            "severity": "Medium"
        })
    
    # Quality concerns
    if any(term in text for term in ["contaminated", "off-spec", "mixed", "blended"]):
        red_flags.append({
            "type": "Quality Concern",
            "description": "Potential quality issues mentioned in documentation",
            "severity": "High"
        })
    
    # Geographic red flags (sanctioned regions)
    sanctioned_regions = ["iran", "venezuela", "north korea", "syria", "myanmar"]
    for region in sanctioned_regions:
        if region in text:
            red_flags.append({
                "type": "Sanctions Risk",
                "description": f"Reference to potentially sanctioned region: {region.title()}",
                "severity": "Critical"
            })
    
    # Financial red flags
    if any(term in text for term in ["advance payment", "upfront fee", "processing fee", "insurance fee"]):
        red_flags.append({
            "type": "Advance Fee Risk",
            "description": "Document mentions advance payments or upfront fees",
            "severity": "High"
        })
    
    # Certificate validity
    if "certificate" in text or "test report" in text:
        if not any(term in text for term in ["sgs", "intertek", "bureau veritas", "cotecna"]):
            red_flags.append({
                "type": "Unverified Certificate",
                "description": "Certificate not from recognized inspection company",
                "severity": "Medium"
            })
    
    return red_flags

def extract_technical_data(text):
    """Extract technical specifications and parameters"""
    technical_data = []
    
    # Common oil & gas parameters
    parameters = {
        "API Gravity": r"api\s+gravity[:\s]*(\d+\.?\d*)",
        "Sulfur Content": r"sulfur[:\s]*(\d+\.?\d*)\s*(?:%|ppm)",
        "Viscosity": r"viscosity[:\s]*(\d+\.?\d*)",
        "Pour Point": r"pour\s+point[:\s]*(-?\d+\.?\d*)",
        "Flash Point": r"flash\s+point[:\s]*(\d+\.?\d*)",
        "Water Content": r"water[:\s]*(\d+\.?\d*)\s*(?:%|ppm)",
        "Sediment": r"sediment[:\s]*(\d+\.?\d*)\s*%"
    }
    
    for param_name, pattern in parameters.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            technical_data.append({
                "parameter": param_name,
                "value": f"{value} {'°API' if 'API' in param_name else '% or ppm' if 'Content' in param_name else 'units'}",
                "recommendation": get_parameter_recommendation(param_name, float(value) if value.replace('.', '').replace('-', '').isdigit() else 0)
            })
    
    return technical_data

def get_parameter_recommendation(param_name, value):
    """Generate recommendations based on technical parameters"""
    recommendations = {
        "API Gravity": {
            "condition": value > 31,
            "good": "Excellent light crude quality, high market value",
            "poor": "Heavy crude, may require specialized refining"
        },
        "Sulfur Content": {
            "condition": value < 0.5,
            "good": "Sweet crude, premium quality",
            "poor": "Sour crude, requires sulfur removal processing"
        },
        "Water Content": {
            "condition": value < 0.5,
            "good": "Low water content, good quality",
            "poor": "High water content, may affect pricing"
        }
    }
    
    if param_name in recommendations:
        rec = recommendations[param_name]
        return rec["good"] if rec["condition"] else rec["poor"]
    
    return "Within acceptable industry standards"

def generate_market_insights(classification):
    """Generate market insights based on product classification"""
    insights = []
    
    product_type = classification.get("type", "Unknown")
    
    if product_type == "Crude Oil":
        insights.append("Crude oil markets currently showing strong demand from Asian refineries")
        
        api_gravity = classification.get("api_gravity")
        if api_gravity and "Heavy" in classification.get("grade", ""):
            insights.append("Heavy crude prices at discount to light crude, good arbitrage opportunities")
        elif api_gravity and "Light" in classification.get("grade", ""):
            insights.append("Light crude commanding premium pricing in current market conditions")
        
        origin = classification.get("origin")
        if origin:
            insights.append(f"{origin} crude typically trades with specific regional premiums/discounts")
    
    elif product_type == "Natural Gas":
        insights.append("Natural gas markets volatile due to seasonal demand and storage levels")
        if "LNG" in classification.get("grade", ""):
            insights.append("LNG demand strong in Asia-Pacific region, especially Japan and South Korea")
    
    elif product_type == "Refined Products":
        insights.append("Refined products margins under pressure from crude oil price volatility")
        grade = classification.get("grade", "")
        if "Gasoline" in grade:
            insights.append("Gasoline demand seasonal with summer driving season approaching")
        elif "Diesel" in grade:
            insights.append("Diesel demand supported by industrial and transportation sectors")
    
    return insights

def generate_recommendations(analysis):
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    # Red flag based recommendations
    red_flags = analysis.get("red_flags", [])
    if red_flags:
        if any(flag["severity"] == "Critical" for flag in red_flags):
            recommendations.append("URGENT: Critical red flags detected - conduct thorough sanctions screening")
        if any(flag["type"] == "Advance Fee Risk" for flag in red_flags):
            recommendations.append("WARNING: Avoid any advance payments - use secure payment methods only")
        if any(flag["type"] == "Quality Concern" for flag in red_flags):
            recommendations.append("Recommend independent quality inspection before proceeding")
    
    # Product-specific recommendations
    product_type = analysis.get("product_classification", {}).get("type")
    if product_type == "Crude Oil":
        recommendations.append("Verify crude oil specifications with independent laboratory testing")
        recommendations.append("Confirm storage and transportation logistics arrangements")
    elif product_type == "Natural Gas":
        recommendations.append("Ensure proper gas composition analysis and BTU content verification")
    
    # General recommendations
    recommendations.append("Conduct thorough due diligence on counterparty credentials")
    recommendations.append("Use secure payment methods and proper legal documentation")
    recommendations.append("Consider engaging commodity trading legal counsel")
    
    return recommendations

def calculate_overall_score(analysis):
    """Calculate overall document quality score"""
    base_score = 70
    
    # Deduct for red flags
    red_flags = analysis.get("red_flags", [])
    for flag in red_flags:
        if flag["severity"] == "Critical":
            base_score -= 30
        elif flag["severity"] == "High":
            base_score -= 15
        elif flag["severity"] == "Medium":
            base_score -= 5
    
    # Add points for complete technical data
    technical_data = analysis.get("technical_analysis", [])
    base_score += min(len(technical_data) * 3, 20)
    
    # Add points for product classification
    classification = analysis.get("product_classification", {})
    if classification.get("type") != "Unknown":
        base_score += 10
    
    return max(0, min(100, base_score))

def generate_summary(analysis):
    """Generate executive summary of the analysis"""
    score = analysis["overall_score"]
    red_flags_count = len(analysis.get("red_flags", []))
    product_type = analysis.get("product_classification", {}).get("type", "Unknown")
    
    if score >= 80:
        quality_assessment = "High quality document with minimal concerns"
    elif score >= 60:
        quality_assessment = "Acceptable document quality with some areas for verification"
    else:
        quality_assessment = "Document quality concerns detected - proceed with caution"
    
    summary = f"{quality_assessment}. "
    
    if product_type != "Unknown":
        summary += f"Document appears to be related to {product_type} trading. "
    
    if red_flags_count > 0:
        summary += f"{red_flags_count} potential red flag(s) identified requiring attention. "
    
    summary += "Recommend independent verification and due diligence before proceeding with any transactions."
    
    return summary