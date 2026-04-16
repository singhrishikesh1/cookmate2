import os
import httpx
import base64
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")
VISION_KEY = os.getenv("AZURE_VISION_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def encode_image(image_data: bytes):
    return base64.b64encode(image_data).decode('utf-8')

async def analyze_image_stream(image_data: bytes):
    """
    Sends an image to Azure Computer Vision and returns a list of detected food items.
    (Used for scanning the fridge).
    """
    if not VISION_ENDPOINT or not VISION_KEY:
        return ["Error: Vision Keys Missing"]

    base_url = VISION_ENDPOINT.rstrip("/")
    api_url = f"{base_url}/computervision/imageanalysis:analyze?features=tags,objects&api-version=2023-10-01"

    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, content=image_data)
        
        if response.status_code != 200:
            logger.error(f"Azure Vision Error: {response.text}")
            return []

        result = response.json()
        detected_items = []

        if "tagsResult" in result:
            for tag in result["tagsResult"]["values"]:
                if tag.get("confidence", 0) > 0.4:
                    detected_items.append(tag["name"])

        if "objectsResult" in result:
            for obj in result["objectsResult"]["values"]:
                if "tags" in obj:
                    for sub_tag in obj["tags"]:
                        if sub_tag.get("confidence", 0) > 0.4:
                            detected_items.append(sub_tag["name"])

        return list(set(detected_items))

async def check_cooking_progress(image_data: bytes, current_step_instruction: str):
    """
    Analyzes a photo of the cooking pot using GPT-4o.
    Detects if food is Undercooked, Perfect, or Burning based on the current step.
    """
    try:
        base64_image = encode_image(image_data)
        
        from services.ai_chef import client, DEPLOYMENT_NAME 

        system_msg = "You are a Realtime Cooking Safety Assistant. Analyze the visual state of the food."
        
        user_msg = f"""
        CONTEXT: The user is currently executing this instruction: "{current_step_instruction}".
        
        TASK: Look at the image provided.
        1. Compare the visual state (color, texture, steam) to what is expected for this step.
        2. Identify any risks (burning, boiling over, dry pan).
        3. Determine if the step is complete.

        Return a JSON object with this exact structure:
        {{
            "status": "on_track" OR "risk" OR "done" OR "undercooked",
            "message": "The onions are turning translucent but not yet golden. Keep stirring.",
            "correction": "None" OR "Lower heat immediately!"
        }}
        """

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME, 
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": user_msg},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Guardian Error: {e}")
        return '{"status": "error", "message": "Vision system offline. Please check manually."}'