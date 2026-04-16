import os
import json
import logging
import io
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_azure_client(api_key_env, endpoint_env):
    key = os.getenv(api_key_env)
    endpoint = os.getenv(endpoint_env)
    if not key or not endpoint:
        return None
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version="2024-02-15-preview"
    )

client_main = get_azure_client("AZURE_OPENAI_KEY", "AZURE_OPENAI_ENDPOINT")
client_tts = get_azure_client("AZURE_TTS_KEY", "AZURE_TTS_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
TTS_DEPLOYMENT_NAME = os.getenv("AZURE_TTS_DEPLOYMENT_NAME", "tts-1")

async def transcribe_audio(audio_bytes: bytes) -> str:
    """Converts Audio -> Text using Whisper."""
    if not client_main: return "System Offline"
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav" 
        
        response = client_main.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return response.text
    except Exception as e:
        logger.error(f"Transcription Error: {e}")
        return "I'm sorry, I couldn't catch that."

async def generate_speech(text: str) -> bytes:
    """Converts Text -> AI Voice Audio."""
    if not client_tts: return b""
    try:
        response = client_tts.audio.speech.create(
            model=TTS_DEPLOYMENT_NAME,
            voice="alloy",
            input=text
        )
        return response.content 
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return b"" 

def get_persona_prompt(persona: str) -> str:
    prompts = {
        "hosteler": "You are a Hosteler Chef. Use 1 pan/kettle, cheap ingredients, and 15-min prep. Be casual: 'Listen bro...'",
        "indian_mom": "You are a caring Indian Mom. Focus on health and 'ghar ka khana'. Be warm: 'Beta, eat this...'",
        "gym_bro": "You are a Gym Bro. Prioritize PROTEIN and MACROS. Be hype: 'Let's get these gains!'",
        "master_chef": "You are a Michelin Star Chef. Focus on technique and plating. Be elegant: 'Notice the texture...'"
    }
    return prompts.get(persona.lower(), "You are a helpful culinary assistant.")

def ask_chef_json(ingredients, preferences, dietary_goal, allergies, meal_type, portion_multiplier, effort_level, persona):
    if not client_main: return {"error": "Client not configured"}
    
    system_msg = f"{get_persona_prompt(persona)} You MUST return ONLY JSON."

    user_prompt = f"""
    Create 5 different {meal_type} options for {portion_multiplier} person(s).
    Ingredients: {ingredients} | Goal: {dietary_goal} | Persona: {persona}
    
    Return ONLY this JSON structure:
    {{
        "recipes": [
            {{
                "dish_name": "...",
                "description": "...",
                "effort_score": 5,
                "protein_content": "...",
                "image_url": "...",
                "steps": [...]
            }}
            ]
    }}
        """
    
    try:
        response = client_main.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Recipe JSON Error: {e}")
        return {"error": "Failed to generate recipe"}
def get_mentor_guidance(step_data: dict, user_query: str = None, persona: str = "hosteler"):
    """Voice response for the 'Mentor' phase."""
    persona_prompt = get_persona_prompt(persona)
    context = f"Step: {step_data['instruction']}."
    if user_query:
        query = f"User asks: {user_query}"
    else:
        query = "Give a 1-sentence instruction for this step."

    try:
        response = client_main.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": f"{persona_prompt} Keep it under 20 words for voice output."},
                {"role": "user", "content": f"{context} {query}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return step_data['instruction']
