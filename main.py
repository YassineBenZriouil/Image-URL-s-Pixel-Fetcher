import json
import requests
import os
import time
import traceback

def fetch_image_from_query(query):
    """Fetch a single image URL for a query"""
    api_key = 'bNXlY7wdyTxbmMDTEKYYIWrnGiwcLjh4Dvezs0PKfey8wKqJsgS1mL2s'
    url = 'https://api.pexels.com/v1/search'
    headers = {
        'Authorization': api_key
    }
    params = {
        'query': query,
        'per_page': 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['photos']:
                return data['photos'][0]['src']['original']
            else:
                return None
        else:
            print(f"⚠️ API error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ Request error: {e}")
        return None

def update_animals(file_path, batch_size=None):
    """
    Update images for animals
    
    Parameters:
    - file_path: Path to the JSON file
    - batch_size: Number of animals to process in this run
                  If None or 0, process ALL remaining animals
    """
    print(f"Processing file: {file_path}")
    
    try:
        # Load the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("✅ Successfully loaded JSON data")
        
        animals = data['__collections__']['animals']
        print(f"Found {len(animals)} animals in total")
        
        # Find animals without images
        animals_without_images = [
            (key, info) for key, info in animals.items() 
            if 'Image URL' not in info or not info['Image URL']
        ]
        print(f"Found {len(animals_without_images)} animals without images")
        
        if not animals_without_images:
            print("All animals already have images! Nothing to do.")
            return True
        
        # Determine how many animals to process
        if batch_size is None or batch_size <= 0:
            # Process ALL remaining animals
            animals_to_process = animals_without_images
            print(f"Will process ALL {len(animals_to_process)} remaining animals")
        else:
            # Process only the specified number
            animals_to_process = animals_without_images[:batch_size]
            print(f"Will process {len(animals_to_process)} animals in this run")
        
        # Process each animal and save immediately
        processed_count = 0
        for key, info in animals_to_process:
            animal_name = info.get('Animal', key)
            print(f"🦁 Fetching image for {animal_name}...")
            
            image_url = fetch_image_from_query(animal_name)
            if image_url:
                # Update the data in memory
                animals[key]['Image URL'] = image_url
                print(f"✅ Found image URL: {image_url}")
                
                # Save immediately after each update
                temp_file = file_path + '.tmp'
                with open(temp_file, 'w') as file:
                    json.dump(data, file, indent=4)
                
                os.replace(temp_file, file_path)
                print(f"📂 Saved update for {animal_name}")
                
                processed_count += 1
            else:
                print(f"❌ Failed to find image for {animal_name}")
            
            # Add a delay to avoid rate limiting
            time.sleep(1)
        
        print(f"Completed processing {processed_count} animals")
        remaining = len(animals_without_images) - processed_count
        if remaining > 0:
            print(f"{remaining} animals still need images. Run the script again.")
        else:
            print("All animals now have images!")
            
        return True
            
    except Exception as e:
        print(f"⚠️ Error: {e}")
        traceback.print_exc()
        return False

# Set your batch size here! Use 0 or None for ALL animals
BATCH_SIZE = 0  # Change this to process more animals at once, or set to 0 for ALL

# Run the script
try:
    update_animals('backup.json', batch_size=BATCH_SIZE)
except Exception as e:
    print(f"⚠️ Unhandled exception: {e}")
    traceback.print_exc()