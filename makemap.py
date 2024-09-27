import os
import gpxpy
import folium
import xyzservices.providers as xyz
from geopy.distance import geodesic



# path to your gpx files
gpx_folder = './gpx'

# create a map object (centered roughly in the White Mountains)
map_center = [44.0, -71.0]  # adjust if needed
my_map = folium.Map(
    location=map_center,
    zoom_start=10,
#    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
#    attr="OpenTopoMap"
)
m = my_map
#Add the Stadia Maps Stamen Toner provider details via xyzservices
tile_provider = xyz.Stadia.StamenTerrain

#Update the URL to include the API key placeholder
folium_key = os.environ['FOLIUM_KEY']
tile_provider["url"] = tile_provider["url"] + "?api_key=" + folium_key

#Create the folium TileLayer, specifying the API key
folium.TileLayer(
    tiles=tile_provider.build_url(api_key=folium_key),
    attr=tile_provider.attribution,
    name=tile_provider.name,
    max_zoom=tile_provider.max_zoom,
    detect_retina=True
).add_to(m)

folium.LayerControl().add_to(m)

total_length_miles = 0.0

# iterate over all gpx files in the folder
for gpx_file in os.listdir(gpx_folder):
    if gpx_file.endswith('.gpx'):
        file_path = os.path.join(gpx_folder, gpx_file)
        
        # open and parse the gpx file
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)
            
            # loop through all the tracks and segments in the gpx file
            for track in gpx.tracks:
                for segment in track.segments:
                    points = []
                    for point in segment.points:
                        points.append((point.latitude, point.longitude))
                    
                    # add the track as a line on the map
                    color = "orange" if "DEFAULT" in gpx_file else "red"
                    folium.PolyLine(points, color=color, weight=2.5, opacity=1).add_to(my_map)

# save the map to an html file
my_map.save('hiking_map.html')

print("Map created! Open 'hiking_map.html' to view it.")

