import os
import exifread
import simplekml



# === SETTINGS ===
# Directory containing your photos
photo_dir = r"/home/deolivea/Mapas/Fotos/Pixel76-100/PIXL83PT_zip"
os.chdir(photo_dir)

# === FUNCTION TO EXTRACT GPS COORDINATES ===
def get_decimal_from_dms(dms, ref):
    """Convert GPS coordinates stored as DMS to decimal degrees."""
    degrees = dms[0].num / dms[0].den
    minutes = dms[1].num / dms[1].den
    seconds = dms[2].num / dms[2].den
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_gps(file_path):
    """Extract GPS Latitude and Longitude from a photo using EXIF."""
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)

    gps_lat = tags.get('GPS GPSLatitude')
    gps_lat_ref = tags.get('GPS GPSLatitudeRef')
    gps_lon = tags.get('GPS GPSLongitude')
    gps_lon_ref = tags.get('GPS GPSLongitudeRef')

    if gps_lat and gps_lon and gps_lat_ref and gps_lon_ref:
        lat = get_decimal_from_dms(gps_lat.values, gps_lat_ref.values)
        lon = get_decimal_from_dms(gps_lon.values, gps_lon_ref.values)
        return lat, lon
    else:
        return None, None

# === CREATE KML ===
kml = simplekml.Kml()

# === LOOP THROUGH ALL JPG FILES ===
for root, dirs, files in os.walk(photo_dir):
    for file_name in files:
        if file_name.lower().endswith(".jpg"):
            file_path = os.path.join(root, file_name)
            lat, lon = extract_gps(file_path)
            if lat is not None and lon is not None:
                image_name = os.path.splitext(os.path.basename(file_path))[0]
                kml.newpoint(
                    name=image_name,
                    description=file_path,
                    coords=[(lon, lat)]  # KML uses (lon, lat)
                )

# === SAVE KML FILE ===
output_file = os.path.join(photo_dir, "Pixel83PT_zip.kml")
kml.save(output_file)
print(f"KML file saved: {output_file}")