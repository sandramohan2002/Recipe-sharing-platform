import requests
import json
from django.conf import settings

def get_nutritional_info_from_ai(recipe_name, ingredients=None):
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.GEMINI_API_KEY
        }
        
        # Create a more detailed prompt
        ingredients_text = f"\nIngredients: {', '.join(ingredients)}" if ingredients else ""
        prompt = {
            "contents": [{
                "parts": [{
                    "text": f"""Analyze and provide estimated nutritional information for a typical serving of '{recipe_name}'.{ingredients_text}
                    Return only a JSON object with these exact keys and numerical values:
                    {{
                        "calories": number,
                        "protein": number,
                        "carbohydrates": number,
                        "fat": number,
                        "fiber": number,
                        "sugar": number
                    }}"""
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()
        
        content = response.json()
        text = content.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            nutrition_data = json.loads(json_match.group())
            return {
                key: float(nutrition_data.get(key, 0)) 
                for key in ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar"]
            }
        
        return None
        
    except Exception as e:
        print(f"Error getting AI nutrition data: {str(e)}")
        return None
