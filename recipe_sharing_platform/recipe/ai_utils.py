import requests
import json

def get_nutritional_info_from_ai(recipe_name, api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
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
                {{"calories": number, "protein": number, "carbohydrates": number, "fat": number, "fiber": number, "sugar": number}}
                """
            }]
        }]
    }
    
    try:
        print(f"Sending request to Gemini AI for {recipe_name}...")  # Debugging
        print(f"Using API Key: {api_key}")  # Ensure API key is available

        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()  # Raises an error for bad responses
        
        content = response.json()
        
        # Extract the text from the response
        text = content.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            nutrition_data = json.loads(json_match.group())
            return {key: float(nutrition_data.get(key, 0)) for key in ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar"]}
        else:
            print("No JSON data found in response")
            return None
            
    except Exception as e:
        print(f"Error getting AI nutrition data: {str(e)}")
        return None
