from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import json

import models, schemas
from database import SessionLocal, engine, get_db
from services import ai_chef 

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ICX Adaptive OS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "ICX Backend Operational",
        "documentation": "/docs",
        "version": "3.0"
    }

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/inventory/{user_id}", response_model=list[schemas.InventoryItem])
def get_inventory(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.InventoryItem).filter(models.InventoryItem.user_id == user_id).all()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return db_user
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/inventory/{user_id}/bulk-add")
def add_inventory(user_id: int, items: list[schemas.InventoryItemCreate], db: Session = Depends(get_db)):
    for item in items:
        db_item = models.InventoryItem(**item.model_dump(), user_id=user_id)
        db.add(db_item)
    db.commit()
    return {"status": "success"}

@app.post("/generate-recipe/", response_model=schemas.RecipeList)
def generate_recipe(request: schemas.RecipeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pantry = [i.name for i in user.inventory]

    recipe_data = ai_chef.ask_chef_json(
        ingredients=pantry,
        preferences=user.preferences,
        dietary_goal=user.dietary_goal,
        allergies=user.allergies,
        meal_type=request.meal_type,
        portion_multiplier=user.portion_multiplier,
        effort_level=user.current_effort_level,
        persona=user.persona,
    )

    if not isinstance(recipe_data, dict):
        raise HTTPException(status_code=502, detail="Invalid response from AI service")

    if "error" in recipe_data:
        raise HTTPException(status_code=502, detail=recipe_data["error"])

    if "recipes" not in recipe_data:
        raise HTTPException(status_code=502, detail="AI service returned an unexpected payload")

    return recipe_data

@app.post("/mentor/start", response_model=schemas.MentorStepResponse)
def start_session(req: schemas.SessionStartRequest, db: Session = Depends(get_db)):
    new_session = models.CookingSession(
        user_id=req.user_id,
        recipe_snapshot=req.recipe_data.model_dump(),
        current_step_index=0,
        status="active"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    first_step = req.recipe_data.steps[0]
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    welcome_text = ai_chef.get_mentor_guidance(first_step.model_dump(), persona=user.persona)

    return {
        "session_id": new_session.id,
        "step_number": 1,
        "total_steps": len(req.recipe_data.steps),
        "instruction": first_step.instruction,
        "timer_seconds": first_step.duration_seconds,
        "voice_response_text": welcome_text,
        "all_step_timers": [s.duration_seconds for s in req.recipe_data.steps]
    }

@app.post("/mentor/voice-interaction/{session_id}")
async def voice_interaction(session_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
   
    sess = db.query(models.CookingSession).filter(models.CookingSession.id == session_id).first()
    if not sess: raise HTTPException(status_code=404)
    
    
    audio_content = await file.read()
    user_text = await ai_chef.transcribe_audio(audio_content)
    
    
    current_step = sess.recipe_snapshot['steps'][sess.current_step_index]
    ai_text_answer = ai_chef.get_mentor_guidance(
        current_step, 
        user_query=user_text, 
        persona=sess.owner.persona
    )
    
    
    audio_response = await ai_chef.generate_speech(ai_text_answer)
    
    return Response(content=audio_response, media_type="audio/mpeg")
@app.delete("/inventory/{user_id}/clear")
async def clear_inventory(user_id: int, db: Session = Depends(get_db)):
    db.query(models.InventoryItem).filter(models.InventoryItem.user_id == user_id).delete()
    db.commit()
    return {"message": "Inventory cleared successfully"}
