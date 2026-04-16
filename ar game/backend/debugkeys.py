import os
from dotenv import load_dotenv

load_dotenv()

print("--- KEY INSPECTION ---")
print(f"VISION ENDPOINT:  {'FOUND' if os.getenv('AZURE_VISION_ENDPOINT') else 'MISSING'}")
print(f"OPENAI ENDPOINT:  {'FOUND' if os.getenv('AZURE_OPENAI_ENDPOINT') else 'MISSING'}")
print(f"OPENAI KEY:       {'FOUND' if os.getenv('AZURE_OPENAI_KEY') else 'MISSING'}")
print(f"DEPLOYMENT NAME:  {'FOUND' if os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME') else 'MISSING'}")
print("----------------------")