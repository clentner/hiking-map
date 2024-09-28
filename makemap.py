import json
import os
import gpxpy
import folium
import xyzservices.providers as xyz
from geopy.distance import geodesic



# path to your gpx files
gpx_folder = './gpx'
json_folder = './'  # where the maps-*.json files are stored

# function to load all json data
def load_all_json():
    json_data = []
    json_files = [f for f in os.listdir(json_folder) if f.startswith('maps-') and f.endswith('.json')]
    for json_file in json_files:
        with open(os.path.join(json_folder, json_file), 'r') as f:
            data = json.load(f)
            json_data.extend(data.get('maps', []))
    return json_data

# load json data once
all_json_data = load_all_json()

# function to match gpx filename with json data
def match_gpx_to_json(gpx_filename):
    # clean gpx filename to match json names (replace '_' with ':')
    cleaned_name = gpx_filename.replace('_', ':').replace('.gpx', '')

    for activity in all_json_data:
        if cleaned_name in activity.get('name', ''):
            return activity.get('slug')  # return the slug for the matched activity
    print("couldn't find matching activity for " + gpx_filename)
    return None



# create a map object (centered roughly in the White Mountains)
map_center = [44.0, -71.0]  # adjust if needed
my_map = folium.Map(
    location=map_center,
    zoom_start=10,
#    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
#    attr="OpenTopoMap"
)
m = my_map
#Add the Stadia Maps Stamen Terrain provider details via xyzservices
folium_key = os.environ.get('FOLIUM_KEY', False)
if folium_key:
    tile_provider = xyz.Stadia.StamenTerrain
    tile_provider["url"] = tile_provider["url"] + "?api_key=" + folium_key

    #Create the folium TileLayer, specifying the API key
    folium.TileLayer(
        tiles=tile_provider.build_url(api_key=folium_key),
        attr=tile_provider.attribution,
        name=tile_provider.name,
        max_zoom=tile_provider.max_zoom,
        detect_retina=True
    ).add_to(m)

# Let's try some other layers
thunderforest_key = os.environ.get('THUNDERFOREST_KEY', False)
if thunderforest_key:
    folium.TileLayer(
        tiles="https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=" + thunderforest_key,
        attr="Thunderforest",
        name="Thunderforest landscape"
    ).add_to(m)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="OpenTopoMap"
).add_to(m)

folium.TileLayer(
    tiles='https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
    max_zoom = 20,
    name="USGS Topo",
    attr='Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
).add_to(m)

folium.LayerControl().add_to(m)

# function to add polylines to the map with a larger clickable area
def add_polyline_with_buffer(points, color, url=None):
    # add the visible polyline first
    folium.PolyLine(points, color=color, weight=2.5, opacity=1).add_to(my_map)

    # create a popup with a link, if there's a URL
    if url:
        popup = folium.Popup(f'<a href="{url}" target="_blank">{gpx_file}</a>')

        # add the wider invisible polyline for larger click area and attach the popup to it
        folium.PolyLine(points, color="transparent", weight=5, opacity=0, popup=popup).add_to(my_map)


total_length_miles = 0.0

# iterate over all gpx files in the folder
for gpx_file in sorted(os.listdir(gpx_folder)):
    if gpx_file.endswith('.gpx'):
        print(f'drawing {gpx_file}')
        file_path = os.path.join(gpx_folder, gpx_file)
        
        # open and parse the gpx file
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)

            # try to match the gpx file with the json data
            slug = match_gpx_to_json(gpx_file)
            url = f"https://alltrails.com/explore/recording/{slug}" if slug else None
            
            # loop through all the tracks and segments in the gpx file
            for track in gpx.tracks:
                for segment in track.segments:
                    points = []
                    for point in segment.points:
                        points.append((point.latitude, point.longitude))
                    for i in range(len(segment.points) - 1):
                        start = (segment.points[i].latitude, segment.points[i].longitude)
                        end = (segment.points[i + 1].latitude, segment.points[i + 1].longitude)

                        # calculate the distance between consecutive points
                        total_length_miles += geodesic(start, end).miles

                    # add the track as a line on the map
                    color = "orange" if "DEFAULT" in gpx_file else "red"
                    # add the track as a clickable polyline
                    add_polyline_with_buffer(points, color, url)

# save the map to an html file
if os.environ.get('FOLIUM_KEY') or os.environ.get('THUNDERFOREST_KEY'):
    output_file = 'hiking_map.html'
else:
    output_file = 'public_hiking_map.html'
my_map.save(output_file)
print(f"Total length of all GPX tracks: {total_length_miles:.2f} miles")

print(f"Map created! Open '{output_file}' to view it.")

