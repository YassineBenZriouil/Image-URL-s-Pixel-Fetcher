
import json
import requests
import os
import time
import traceback

def fetch_image_from_query(query):
    """Fetch a single image URL for a query"""
    api_key = 'your api_key'
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

def update_entities(file_path, batch_size=None):
    """
    Update images for entities (e.g., animals, plants, cities, etc.)
    
    Parameters:
    - file_path: Path to the JSON file
    - batch_size: Number of entities to process in this run
                  If None or 0, process ALL remaining entities
    """
    print(f"Processing file: {file_path}")
    
    try:
        # Load the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("✅ Successfully loaded JSON data")
        
        entities = data['__collections__']['entities']
        print(f"Found {len(entities)} entities in total")
        
        # Find entities without images
        entities_without_images = [
            (key, info) for key, info in entities.items() 
            if 'Image URL' not in info or not info['Image URL']
        ]
        print(f"Found {len(entities_without_images)} entities without images")
        
        if not entities_without_images:
            print("All entities already have images! Nothing to do.")
            return True
        
        # Determine how many entities to process
        if batch_size is None or batch_size <= 0:
            # Process ALL remaining entities
            entities_to_process = entities_without_images
            print(f"Will process ALL {len(entities_to_process)} remaining entities")
        else:
            # Process only the specified number
            entities_to_process = entities_without_images[:batch_size]
            print(f"Will process {len(entities_to_process)} entities in this run")
        
        # Process each entity and save immediately
        processed_count = 0
        for key, info in entities_to_process:
            entity_name = info.get('Name', key)
            print(f"🌍 Fetching image for {entity_name}...")
            
            image_url = fetch_image_from_query(entity_name)
            if image_url:
                # Update the data in memory
                entities[key]['Image URL'] = image_url
                print(f"✅ Found image URL: {image_url}")
                
                # Save immediately after each update
                temp_file = file_path + '.tmp'
                with open(temp_file, 'w') as file:
                    json.dump(data, file, indent=4)
                
                os.replace(temp_file, file_path)
                print(f"📂 Saved update for {entity_name}")
                
                processed_count += 1
            else:
                print(f"❌ Failed to find image for {entity_name}")
            
            # Add a delay to avoid rate limiting
            time.sleep(1)
        
        print(f"Completed processing {processed_count} entities")
        remaining = len(entities_without_images) - processed_count
        if remaining > 0:
            print(f"{remaining} entities still need images. Run the script again.")
        else:
            print("All entities now have images!")
            
        return True
            
    except Exception as e:
        print(f"⚠️ Error: {e}")
        traceback.print_exc()
        return False

# Set your batch size here! Use 0 or None for ALL entities
BATCH_SIZE = 0  # Change this to process more entities at once, or set to 0 for ALL

# Run the script
try:
    update_entities('backup.json', batch_size=BATCH_SIZE)
except Exception as e:
    print(f"⚠️ Unhandled exception: {e}")
    traceback.print_exc()
