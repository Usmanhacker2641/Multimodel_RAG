from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os
from core.logger import setup_logger

# backend/feedback_routes.py

logger = setup_logger("backend.feedback")
router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Pydantic model for request validation
class FeedbackRequest(BaseModel):
    user_id: str
    question: str
    feedback: str
    rating: Optional[int] = None  # 1-5 star rating
    response: Optional[str] = None  # The model's response being rated
    comments: Optional[str] = None

# Simple file-based storage (replace with actual database in production)
FEEDBACK_FILE = "feedback_data.json"

def store_feedback(user_id: str, question: str, feedback: str, rating: Optional[int] = None, 
                   response: Optional[str] = None, comments: Optional[str] = None):
    """Store feedback to a JSON file (replace with database in production)"""
    feedback_entry = {
        "user_id": user_id,
        "question": question,
        "feedback": feedback,
        "rating": rating,
        "response": response,
        "comments": comments,
        "timestamp": datetime.now().isoformat()
    }
    
    # Load existing feedback
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            try:
                feedback_data = json.load(f)
            except json.JSONDecodeError:
                feedback_data = []
    else:
        feedback_data = []
    
    # Append new feedback
    feedback_data.append(feedback_entry)
    
    # Save back to file
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=2)

@router.post("/")
async def submit_feedback(
    user_id: str = Form(...),
    question: str = Form(...),
    feedback: str = Form(...),  # "positive", "negative", "thumbs_up", "thumbs_down"
    rating: Optional[int] = Form(None),
    response: Optional[str] = Form(None),
    comments: Optional[str] = Form(None)
):
    """
    Submit user feedback for a model response
    
    - **user_id**: Unique identifier for the user
    - **question**: The question that was asked
    - **feedback**: Type of feedback (e.g., "thumbs_up", "thumbs_down")
    - **rating**: Optional 1-5 star rating
    - **response**: Optional model response being rated
    - **comments**: Optional additional comments
    """
    try:
        logger.info("Feedback submission: user_id=%s feedback=%s rating=%s", user_id, feedback, rating)
        
        # Validate rating if provided
        if rating is not None and (rating < 1 or rating > 5):
            logger.warning("Invalid rating provided: rating=%d user_id=%s", rating, user_id)
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Store feedback
        store_feedback(user_id, question, feedback, rating, response, comments)
        logger.info("Feedback recorded successfully: user_id=%s", user_id)
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error recording feedback: user_id=%s error=%s", user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@router.post("/json")
async def submit_feedback_json(feedback_data: FeedbackRequest):
    """Submit feedback using JSON body instead of form data"""
    try:
        if feedback_data.rating is not None and (feedback_data.rating < 1 or feedback_data.rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        store_feedback(
            feedback_data.user_id,
            feedback_data.question,
            feedback_data.feedback,
            feedback_data.rating,
            feedback_data.response,
            feedback_data.comments
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@router.get("/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    try:
        if not os.path.exists(FEEDBACK_FILE):
            return {"total": 0, "positive": 0, "negative": 0}
        
        with open(FEEDBACK_FILE, 'r') as f:
            feedback_data = json.load(f)
        
        total = len(feedback_data)
        positive = sum(1 for f in feedback_data if f["feedback"] in ["positive", "thumbs_up"])
        negative = sum(1 for f in feedback_data if f["feedback"] in ["negative", "thumbs_down"])
        
        avg_rating = None
        ratings = [f["rating"] for f in feedback_data if f.get("rating")]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
        
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "average_rating": round(avg_rating, 2) if avg_rating else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")