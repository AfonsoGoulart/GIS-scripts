import zipfile
import xml.etree.ElementTree as ET
import sys
import os
from typing import Optional

# Define KML namespaces and tags
KML_NAMESPACE = "{http://www.opengis.net/kml/2.2}" # This may change depending on where you got your kml file
POLYGON_TAG = f"{KML_NAMESPACE}Polygon"
PLACEMARK_TAG = f"{KML_NAMESPACE}Placemark"
KML_FILENAME = 'doc.kml' # Name of the KML file inside the KMZ archive

def _get_kml_root(kmz_filepath: str) -> Optional[ET.Element]:
    """Handles file checking, KMZ extraction, and KML parsing, returning the root element."""
    if not os.path.exists(kmz_filepath):
        print(f"Error: File not found at path: {kmz_filepath}")
        return None

    try:
        # 1. Open the KMZ file as a ZIP archive
        with zipfile.ZipFile(kmz_filepath, 'r') as kmz_archive:
            
            # 2. Read the KML file content from the archive
            kml_files = [name for name in kmz_archive.namelist() if name.lower().endswith('.kml')]
            
            kml_to_read = None
            if KML_FILENAME in kml_files:
                kml_to_read = KML_FILENAME
            elif kml_files:
                # Handle non-standard KMZ files by looking for the first .kml file
                kml_to_read = kml_files[0]
                print(f"Warning: '{KML_FILENAME}' not found. Using '{kml_to_read}' instead.")
            else:
                print(f"Error: No KML file found inside {kmz_filepath}.")
                return None

            kml_content = kmz_archive.read(kml_to_read)

            # 3. Parse the KML (XML) content
            root = ET.fromstring(kml_content)
            return root

    except zipfile.BadZipFile:
        print(f"Error: '{kmz_filepath}' is not a valid KMZ/ZIP file.")
        return None
    except ET.ParseError:
        print(f"Error: Failed to parse KML content inside '{kmz_filepath}'. The file may be corrupted.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during file reading or parsing: {e}")
        return None

def count_all_polygons(root: ET.Element) -> int:
    """
    Counts the total number of <Polygon> elements found anywhere in the KML structure.
    This gives the raw count of geometry objects.
    """
    # Recursively search for all <Polygon> tags in the entire document
    # The 'findall(".//TAG")' syntax with the namespace is crucial for correct KML parsing.
    polygon_elements = root.findall(f".//{POLYGON_TAG}")
    return len(polygon_elements)

def count_polygon_features(root: ET.Element) -> int:
    """
    Counts the number of <Placemark> features that contain at least one <Polygon>.
    This typically matches the number of separate items/features visible on a map.
    """
    feature_count = 0
    
    # Find all <Placemark> elements in the document
    for placemark in root.findall(f".//{PLACEMARK_TAG}"):
        # Check if this Placemark contains any <Polygon> as a descendant
        if placemark.findall(f".//{POLYGON_TAG}"):
            feature_count += 1
            
    return feature_count

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kmz_processor.py <path_to_your_file.kmz>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    print(f"--- KMZ Polygon Count Report ---")
    print(f"Analyzing file: {input_file}")

    kml_root = _get_kml_root(input_file)
    
    if kml_root is None:
        sys.exit(1) # Exit if parsing failed

    # Calculate both counts
    raw_polygon_count = count_all_polygons(kml_root)
    feature_count = count_polygon_features(kml_root)
    
    print(f"\nResults for '{input_file}':")
    print("-" * 30)

    # Report 1: Raw Geometry Count (The original method)
    print(f"1. Raw Polygon (<Polygon> Tag) Count: {raw_polygon_count}")
    
    # Report 2: Feature Count (The likely corrected count)
    print(f"2. Polygon Feature (<Placemark> Count): {feature_count}")
    
    if raw_polygon_count > feature_count:
        print(f"\n💡 Note: The raw count is higher because some features contain multiple <Polygon> tags.")
    
    print("-" * 30)
