import requests
import json

def get_nutritional_info_from_ai(recipe_name, api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    prompt = {
        "contents": [{
            "parts": [{
                "text": f"""
                Analyze and provide estimated nutritional information for a typical serving of '{recipe_name}'.
                Return only a JSON object with these exact keys and numerical values:
                {{
                    "calories": number,
                    "protein": number,
                    "carbohydrates": number,
                    "fat": number,
                    "fiber": number,
                    "sugar": number
                }}
                """
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        content = response.json()
        
        # Extract the text from the response
        text = content['candidates'][0]['content']['parts'][0]['text']
        
        # Find and extract the JSON object
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            nutrition_data = json.loads(json_match.group())
            return {
                'calories': float(nutrition_data.get('calories', 0)),
                'protein': float(nutrition_data.get('protein', 0)),
                'carbohydrates': float(nutrition_data.get('carbohydrates', 0)),
                'fat': float(nutrition_data.get('fat', 0)),
                'fiber': float(nutrition_data.get('fiber', 0)),
                'sugar': float(nutrition_data.get('sugar', 0))
            }
        else:
            print("No JSON data found in response")
            return None
            
    except Exception as e:
        print(f"Error getting AI nutrition data: {str(e)}")
        return None