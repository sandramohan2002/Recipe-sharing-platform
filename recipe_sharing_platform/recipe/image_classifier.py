import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io

class RecipeImageClassifier:
    def __init__(self):
        # Load pre-trained MobileNetV2 model
        self.model = MobileNetV2(weights='imagenet')
        
        # Define food-related categories
        self.food_categories = {
            'dessert': ['cake', 'chocolate', 'ice_cream', 'cookie', 'pie'],
            'vegetarian': ['vegetable', 'salad', 'broccoli', 'mushroom', 'spinach'],
            'meat': ['meat', 'steak', 'chicken', 'beef', 'pork'],
            'seafood': ['fish', 'seafood', 'shrimp', 'crab', 'lobster'],
            'breakfast': ['egg', 'pancake', 'waffle', 'bread', 'toast'],
            'beverage': ['coffee', 'tea', 'juice', 'smoothie', 'drink']
        }

    def preprocess_image(self, img_file):
        # Open and preprocess image
        if isinstance(img_file, (bytes, io.BytesIO)):
            img = Image.open(io.BytesIO(img_file.read()) if hasattr(img_file, 'read') else io.BytesIO(img_file))
        else:
            img = Image.open(img_file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize image to required size
        img = img.resize((224, 224))
        
        # Convert to array and preprocess
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        return img_array

    def classify_image(self, img_file):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(img_file)
            
            # Get predictions
            predictions = self.model.predict(processed_image)
            decoded_predictions = decode_predictions(predictions, top=5)[0]
            
            # Initialize category scores
            category_scores = {category: 0.0 for category in self.food_categories.keys()}
            
            # Calculate scores for each category
            for _, pred_class, score in decoded_predictions:
                for category, keywords in self.food_categories.items():
                    if any(keyword in pred_class.lower() for keyword in keywords):
                        category_scores[category] += score
            
            # Get the top category
            top_category = max(category_scores.items(), key=lambda x: x[1])
            
            # Prepare response
            result = {
                'category': top_category[0],
                'confidence': float(top_category[1]),
                'is_food': any(score > 0.1 for score in category_scores.values())
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'category': 'unknown',
                'confidence': 0.0,
                'is_food': False
            }