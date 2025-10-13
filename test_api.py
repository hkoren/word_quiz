#!/usr/bin/env python3
"""
Test the API endpoint directly using requests
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5556"
    
    # Test cases
    test_cases = [
        {"grades": [1], "word_type": "r"},
        {"grades": [1, 2], "word_type": "r"},
        {"grades": [1], "word_type": "s"},
        {"grades": [1], "word_type": "o"},
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case}")
        
        # Build query parameters
        params = {
            'word_type': test_case['word_type']
        }
        
        # Add multiple grades parameters
        grade_params = []
        for grade in test_case['grades']:
            grade_params.append(('grades', str(grade)))
        
        try:
            url = f"{base_url}/api/available_words"
            response = requests.get(url, params=grade_params + [('word_type', test_case['word_type'])])
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data}")
                print(f"Word count: {data.get('count', 0)}")
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == '__main__':
    test_api()