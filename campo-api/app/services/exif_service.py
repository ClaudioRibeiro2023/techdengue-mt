"""
EXIF Service - Extracts metadata from images
"""
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io


class EXIFService:
    """Service for extracting EXIF metadata from images"""
    
    @staticmethod
    def calculate_sha256(file_content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            file_content: File bytes
            
        Returns:
            SHA-256 hex digest
        """
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def extract_exif(file_content: bytes) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image.
        
        Args:
            file_content: Image file bytes
            
        Returns:
            Dict with extracted EXIF data
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Get basic image info
            metadata = {
                "image_width": image.width,
                "image_height": image.height,
                "format": image.format,
                "mode": image.mode
            }
            
            # Get EXIF data if available
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    
                    # Handle GPS info separately
                    if tag_name == "GPSInfo":
                        gps_data = EXIFService._extract_gps_info(value)
                        metadata.update(gps_data)
                    else:
                        # Convert datetime to string
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)
                        
                        # Store relevant tags
                        if tag_name in ["Make", "Model", "DateTime", "DateTimeOriginal", 
                                       "Orientation", "Software", "ExifImageWidth", "ExifImageHeight"]:
                            metadata[tag_name.lower()] = value
            
            return metadata
            
        except Exception as e:
            # If EXIF extraction fails, return basic info only
            return {
                "error": f"EXIF extraction failed: {str(e)}"
            }
    
    @staticmethod
    def _extract_gps_info(gps_data: Dict) -> Dict[str, float]:
        """
        Extract GPS coordinates from EXIF GPS data.
        
        Args:
            gps_data: GPS EXIF data
            
        Returns:
            Dict with gps_latitude, gps_longitude, gps_altitude
        """
        gps_info = {}
        
        try:
            # Decode GPS tags
            gps_tags = {}
            for tag_id, value in gps_data.items():
                tag_name = GPSTAGS.get(tag_id, tag_id)
                gps_tags[tag_name] = value
            
            # Extract latitude
            if "GPSLatitude" in gps_tags and "GPSLatitudeRef" in gps_tags:
                lat = EXIFService._convert_to_degrees(gps_tags["GPSLatitude"])
                if gps_tags["GPSLatitudeRef"] == "S":
                    lat = -lat
                gps_info["gps_latitude"] = lat
            
            # Extract longitude
            if "GPSLongitude" in gps_tags and "GPSLongitudeRef" in gps_tags:
                lon = EXIFService._convert_to_degrees(gps_tags["GPSLongitude"])
                if gps_tags["GPSLongitudeRef"] == "W":
                    lon = -lon
                gps_info["gps_longitude"] = lon
            
            # Extract altitude
            if "GPSAltitude" in gps_tags:
                altitude = gps_tags["GPSAltitude"]
                if isinstance(altitude, tuple):
                    altitude = altitude[0] / altitude[1]
                gps_info["gps_altitude"] = float(altitude)
            
        except Exception as e:
            gps_info["gps_error"] = f"GPS extraction failed: {str(e)}"
        
        return gps_info
    
    @staticmethod
    def _convert_to_degrees(value: tuple) -> float:
        """
        Convert GPS coordinates from degrees/minutes/seconds to decimal degrees.
        
        Args:
            value: Tuple of (degrees, minutes, seconds)
            
        Returns:
            Decimal degrees
        """
        d, m, s = value
        
        # Handle tuple ratios (e.g., (41, 1) for 41/1)
        if isinstance(d, tuple):
            d = d[0] / d[1]
        if isinstance(m, tuple):
            m = m[0] / m[1]
        if isinstance(s, tuple):
            s = s[0] / s[1]
        
        return float(d) + float(m) / 60.0 + float(s) / 3600.0
    
    @staticmethod
    def validate_image(file_content: bytes, max_size_mb: int = 50) -> tuple[bool, Optional[str]]:
        """
        Validate image file.
        
        Args:
            file_content: Image file bytes
            max_size_mb: Maximum size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"
        
        # Try to open as image
        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()
            
            # Check format
            if image.format not in ["JPEG", "PNG", "WEBP"]:
                return False, f"Unsupported image format: {image.format}"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
