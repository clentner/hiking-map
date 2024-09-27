import json
import glob
import os
import webbrowser

# define bounds for the white mountains region (you can adjust these)
min_latitude = 43.79
max_latitude = 44.7
min_longitude = -72.0
max_longitude = -70.78

# function to check if the location is within the white mountains bounds
def is_within_bounds(location):
    if location:
        lat = float(location.get('latitude', 0))
        lon = float(location.get('longitude', 0))
        return (min_latitude <= lat <= max_latitude) and (min_longitude <= lon <= max_longitude)
    return False



# path where your json files are stored (change this if needed)
path_to_json_files = './'  # adjust as necessary

# find all json files (assuming names like "maps-1.json", "maps-2.json", etc.)
json_files = glob.glob(f"{path_to_json_files}/maps-*.json")

hiking_slugs = []

# read each json file and filter for hiking activities
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)
        
        # assuming 'maps' is a list of activities in the json
        for activity in data.get('maps', []):
            activity_type = activity.get('activity', {})
            location_data = activity.get('location')
            if activity_type and activity_type.get('uid') == 'snowshoeing' and is_within_bounds(location_data):
                slug = activity.get('slug')
                if slug:
                    full_url = f"https://alltrails.com/explore/recording/{slug}"
                    hiking_slugs.append(full_url)

batch_size = 5
for i in range(0, len(hiking_slugs), batch_size):
    batch = hiking_slugs[i:i + batch_size]
    
    # open each url in the batch
    for url in batch:
        webbrowser.open(url)  # this will open the link in the default browser
    
    # optional: wait for user to download files before opening next batch
    input(f"Opened batch {i//batch_size + 1}. Press Enter to open the next batch...")


