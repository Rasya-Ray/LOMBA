from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv
from model import QwenModel

# Load .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FamilyGuard AI",
    description="Analisis situs berbahaya + generate coaching",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model (load once on startup)
qwen_model = None

# ==================== MODELS ====================

class AnalyzeRequest(BaseModel):
    """Request untuk analyze situs"""
    domain: str                    # "xvideos.com"
    category: str                  # "adult", "gambling", etc
    child_name: str               # "Budi"
    child_age: int                # 13
    profile_id: str               # NextDNS profile ID "abc123"
    parent_id: str                # Firebase UID "firebase-parent-123"

class AnalyzeResponse(BaseModel):
    """Response dari analyze"""
    coaching_text: str
    category: str
    severity: str
    domain: str

class ClassifyRequest(BaseModel):
    """Request untuk classify (fast, no AI)"""
    domain: str

class ClassifyResponse(BaseModel):
    """Response classify"""
    category: str
    severity: str
    should_block: bool

# ==================== ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global qwen_model
    
    logger.info("[STARTUP] Loading Qwen model...")
    qwen_model = QwenModel(
        model_name=os.getenv("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
    )
    qwen_model.load()
    logger.info("[STARTUP] ✅ Model ready!")

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "alive",
        "service": "FamilyGuard AI",
        "model_loaded": qwen_model is not None
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_site(
    request: AnalyzeRequest,
    x_api_key: str = Header(None)
):
    """
    Analyze dangerous site & generate coaching
    
    Input:
    - domain: "xvideos.com"
    - category: "adult"
    - child_name: "Budi"
    - child_age: 13
    - profile_id: "nextdns-abc123"  ← NextDNS profile ID
    - parent_id: "firebase-parent-123"  ← Parent Firebase UID
    
    Output:
    - Coaching text untuk orang tua
    """
    
    # Verify API key
    if x_api_key != os.getenv("API_KEY", "default-key"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not qwen_model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        logger.info(
            f"[ANALYZE] Parent: {request.parent_id}, "
            f"Child: {request.child_name}, "
            f"Domain: {request.domain}"
        )
        
        # Generate coaching text
        coaching_text = qwen_model.generate_coaching(
            child_name=request.child_name,
            child_age=request.child_age,
            domain=request.domain
        )
        
        logger.info("[ANALYZE] ✅ Coaching generated")
        
        return AnalyzeResponse(
            coaching_text=coaching_text,
            category=request.category,
            severity="HIGH" if request.category in ["adult", "gambling"] else "MEDIUM",
            domain=request.domain
        )
    
    except Exception as e:
        logger.error(f"[ANALYZE] ❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify", response_model=ClassifyResponse)
async def classify_site(
    request: ClassifyRequest,
    x_api_key: str = Header(None)
):
    """
    Fast classification (no AI needed)
    Instant response, hardcoded domain list
    """
    
    if x_api_key != os.getenv("API_KEY", "default-key"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        result = qwen_model.classify_domain(request.domain)
        return ClassifyResponse(**result)
    except Exception as e:
        logger.error(f"[CLASSIFY] ❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== INFO ====================

@app.get("/")
async def root():
    return {
        "service": "FamilyGuard AI Server",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze",
            "classify": "POST /classify"
        }
    }

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,  # Single worker untuk GPU/model
        log_level="info"
    )