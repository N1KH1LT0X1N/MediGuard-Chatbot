"""
Media Handler Module
Handles downloading and processing media files (PDF/images) from Twilio WhatsApp.
"""

import os
import requests
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse


class MediaHandler:
    """
    Handles media file downloads from Twilio WhatsApp API.
    Downloads PDF/images, validates them, and manages temporary storage.
    """

    # Supported file extensions
    SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
    SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize media handler.

        Args:
            temp_dir: Directory for temporary files (defaults to system temp)
        """
        if temp_dir:
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.temp_dir = Path(tempfile.gettempdir()) / "mediguard_media"
            self.temp_dir.mkdir(parents=True, exist_ok=True)

    def download_media(
        self,
        media_url: str,
        account_sid: str,
        auth_token: str,
        file_extension: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Download media file from Twilio Media URL.

        Args:
            media_url: Twilio Media URL (requires auth)
            account_sid: Twilio Account SID for authentication
            auth_token: Twilio Auth Token for authentication
            file_extension: Optional file extension (e.g., '.pdf', '.jpg')

        Returns:
            Tuple of (file_path, error_message)
            Returns (None, error_msg) on failure
        """
        try:
            # Initialize variable at the start to avoid scope issues
            first_chunk_for_file = None
            response = None
            
            # Check if this is a Twilio media URL (requires auth) or public URL
            is_twilio_url = "api.twilio.com" in media_url or "twilio.com" in media_url
            
            print(f"[DEBUG] Downloading from {'Twilio' if is_twilio_url else 'public'} URL: {media_url[:100]}...")
            
            # Download with or without authentication
            if is_twilio_url and account_sid and auth_token:
                # Twilio media URL - requires authentication
                response = requests.get(
                    media_url,
                    auth=(account_sid, auth_token),
                    timeout=30,
                    stream=True
                )
            else:
                # Public URL - no authentication needed (workaround for PDF uploads)
                print(f"[DEBUG] Downloading from public URL (no auth required)")
                
                # Handle Google Drive URLs - convert to direct download
                if "drive.google.com" in media_url:
                    print(f"[DEBUG] ========== GOOGLE DRIVE URL CONVERSION ==========")
                    print(f"[DEBUG] Original URL: {media_url[:200]}...")
                    
                    # Extract file ID from various Google Drive URL formats
                    import re as url_re
                    gd_patterns = [
                        r'/file/d/([a-zA-Z0-9_-]+)',  # Standard share link: /file/d/ID/view
                        r'id=([a-zA-Z0-9_-]+)',      # URL with id parameter: ?id=ID
                        r'/open\?id=([a-zA-Z0-9_-]+)', # Open link format: /open?id=ID
                    ]
                    file_id = None
                    original_url = media_url
                    
                    for pattern in gd_patterns:
                        match = url_re.search(pattern, media_url)
                        if match:
                            file_id = match.group(1)
                            print(f"[DEBUG] Extracted Google Drive file ID: {file_id}")
                            print(f"[DEBUG] Pattern matched: {pattern}")
                            break
                    
                    if file_id:
                        # Try multiple Google Drive download URL formats
                        # Method 1: Standard direct download (works for files < 100MB)
                        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                        print(f"[DEBUG] Converted to direct download URL: {direct_url}")
                        print(f"[DEBUG] File ID: {file_id}")
                        media_url = direct_url
                    else:
                        print(f"[ERROR] Could not extract file ID from Google Drive URL")
                        print(f"[ERROR] URL: {original_url[:200]}...")
                        print(f"[ERROR] Tried patterns: {gd_patterns}")
                        # Continue with original URL - might work for some formats
                        print(f"[WARN] Continuing with original URL (may fail)")
                
                # For Google Drive, we need to handle large files differently
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "*/*"
                }
                
                # For Google Drive, handle the virus scan warning for large files
                if "drive.google.com" in media_url and "uc?export=download" in media_url:
                    # First request to get the download link (may redirect for large files)
                    session = requests.Session()
                    initial_response = session.get(
                        media_url,
                        timeout=30,
                        headers=headers,
                        allow_redirects=False
                    )
                    
                    # Check if we got a redirect (large file warning)
                    if initial_response.status_code in [302, 303, 307, 308]:
                        # Follow the redirect
                        redirect_url = initial_response.headers.get('Location')
                        if redirect_url:
                            print(f"[DEBUG] Following Google Drive redirect: {redirect_url[:100]}...")
                            media_url = redirect_url
                    elif initial_response.status_code == 200:
                        # Check if response is HTML (virus scan warning page)
                        content_type = initial_response.headers.get('Content-Type', '').lower()
                        if 'text/html' in content_type:
                            # Read first few bytes to check
                            try:
                                content_preview = initial_response.content[:500].decode('utf-8', errors='ignore').lower()
                                if 'virus scan' in content_preview or 'large file' in content_preview:
                                    print(f"[WARN] Google Drive returned virus scan warning page")
                                    # Try to extract the actual download link from the HTML
                                    import re
                                    download_match = re.search(r'href="([^"]*uc\?[^"]*)"', content_preview)
                                    if download_match:
                                        actual_url = download_match.group(1)
                                        if not actual_url.startswith('http'):
                                            actual_url = 'https://drive.google.com' + actual_url
                                        print(f"[DEBUG] Found download link in warning page: {actual_url[:100]}...")
                                        media_url = actual_url
                            except Exception as e:
                                print(f"[WARN] Could not parse Google Drive warning page: {str(e)}")
                    
                    # Now download the actual file
                    response = session.get(
                        media_url,
                        timeout=60,  # Longer timeout for large files
                        stream=True,
                        headers=headers,
                        allow_redirects=True
                    )
                    
                    # Check if redirect led to sign-in page
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'text/html' in content_type:
                            # Check if it's a sign-in page
                            content_preview = response.content[:1000].decode('utf-8', errors='ignore').lower()
                            if 'accounts.google.com' in content_preview or 'sign in' in content_preview:
                                print(f"[ERROR] Google Drive redirect led to sign-in page - file is NOT publicly accessible")
                                return None, (
                                    "Google Drive file requires authentication and is not publicly accessible.\n\n"
                                    "To fix:\n"
                                    "1. Open the file in Google Drive\n"
                                    "2. Click 'Share' button\n"
                                    "3. Click 'Change to anyone with the link'\n"
                                    "4. Set permission to 'Viewer'\n"
                                    "5. Copy the link and try again\n\n"
                                    "The file must be accessible without signing in."
                                )
                else:
                    # Regular public URL download
                    response = requests.get(
                        media_url,
                        timeout=30,
                        stream=True,
                        headers=headers,
                        allow_redirects=True
                    )
            
            # Ensure response exists
            if response is None:
                return None, "Failed to get response from server"
            
            response.raise_for_status()
            
            # CRITICAL: Check if response is HTML (sign-in page or error page)
            # This must happen BEFORE we try to save the file
            # Note: first_chunk_for_file is already initialized at function start
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                # Read first chunk to check
                first_chunk = next(response.iter_content(chunk_size=1024), b'')
                content_str = first_chunk.decode('utf-8', errors='ignore').lower()
                
                if 'accounts.google.com' in content_str or 'sign in' in content_str:
                    print(f"[ERROR] Downloaded content is Google sign-in page - file is NOT publicly accessible")
                    return None, (
                        "Google Drive file requires authentication and is not publicly accessible.\n\n"
                        "To fix:\n"
                        "1. Open the file in Google Drive\n"
                        "2. Click 'Share' button\n"
                        "3. Click 'Change to anyone with the link'\n"
                        "4. Set permission to 'Viewer'\n"
                        "5. Copy the link and try again\n\n"
                        "The file must be accessible without signing in."
                    )
                
                # Reset response for actual download
                response = session.get(media_url, timeout=60, stream=True, headers=headers, allow_redirects=True) if 'session' in locals() else requests.get(media_url, timeout=60, stream=True, headers=headers, allow_redirects=True)
                response.raise_for_status()

            # Check file size
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                return None, f"File too large (max {self.MAX_FILE_SIZE / 1024 / 1024}MB)"

            # Determine file extension from Content-Type or URL (initial guess)
            initial_extension = file_extension
            if not initial_extension:
                content_type = response.headers.get('Content-Type', '')
                initial_extension = self._get_extension_from_content_type(content_type)
                
                if not initial_extension:
                    # Try to get from URL
                    parsed_url = urlparse(media_url)
                    initial_extension = Path(parsed_url.path).suffix.lower()
                
                # Default to .pdf for Google Drive (most lab reports are PDFs)
                if not initial_extension or initial_extension not in self.SUPPORTED_EXTENSIONS:
                    if "drive.google.com" in media_url:
                        initial_extension = '.pdf'  # Google Drive files are usually PDFs
                    else:
                        initial_extension = '.pdf'  # Default to PDF for unknown

            # Validate extension
            if initial_extension not in self.SUPPORTED_EXTENSIONS:
                return None, f"Unsupported file type: {initial_extension}. Supported: PDF, JPG, PNG, etc."

            # Create temporary file with initial extension
            import uuid
            temp_filename = f"lab_report_{uuid.uuid4().hex[:8]}{initial_extension}"
            temp_file_path = self.temp_dir / temp_filename

            # Download file
            # If we already peeked at first chunk (for HTML check), include it
            first_chunk_data = first_chunk_for_file if first_chunk_for_file else None
            
            with open(temp_file_path, 'wb') as f:
                if first_chunk_data:
                    f.write(first_chunk_data)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # CRITICAL: Detect actual file type from content (magic bytes)
            # This fixes the issue where PDFs are saved as .jpg
            if temp_file_path.exists():
                file_size = temp_file_path.stat().st_size
                print(f"[DEBUG] Downloaded file size: {file_size} bytes")
                
                try:
                    with open(temp_file_path, 'rb') as f:
                        first_bytes = f.read(1024)
                        content_str = first_bytes.decode('utf-8', errors='ignore').lower()
                        
                        print(f"[DEBUG] First 200 bytes (hex): {first_bytes[:200].hex()}")
                        print(f"[DEBUG] First 200 bytes (text): {content_str[:200]}")
                        
                        # Detect actual file type from magic bytes
                        actual_extension = None
                        if first_bytes.startswith(b'%PDF'):
                            actual_extension = '.pdf'
                            print(f"[DEBUG] Detected PDF from magic bytes")
                        elif first_bytes.startswith(b'\xff\xd8\xff'):
                            actual_extension = '.jpg'
                            print(f"[DEBUG] Detected JPEG from magic bytes")
                        elif first_bytes.startswith(b'\x89PNG'):
                            actual_extension = '.png'
                            print(f"[DEBUG] Detected PNG from magic bytes")
                        elif first_bytes.startswith(b'GIF'):
                            actual_extension = '.gif'
                            print(f"[DEBUG] Detected GIF from magic bytes")
                        
                        # If detected extension differs from initial, rename file
                        if actual_extension and actual_extension != initial_extension:
                            print(f"[WARN] File type mismatch! Initial: {initial_extension}, Actual: {actual_extension}")
                            print(f"[INFO] Renaming file to correct extension...")
                            try:
                                new_temp_path = temp_file_path.with_suffix(actual_extension)
                                if new_temp_path.exists():
                                    new_temp_path.unlink()  # Remove if exists
                                temp_file_path.rename(new_temp_path)
                                temp_file_path = new_temp_path
                                temp_filename = temp_file_path.name
                                print(f"[OK] File renamed to: {temp_filename}")
                            except Exception as rename_error:
                                print(f"[ERROR] Failed to rename file: {str(rename_error)}")
                                # Continue with original path - validation will handle it
                        elif actual_extension:
                            print(f"[OK] File type matches: {actual_extension}")
                        else:
                            print(f"[WARN] Could not detect file type from magic bytes, using initial extension: {initial_extension}")
                        
                        # Check for HTML content (Google Drive error pages)
                        if b'<html' in first_bytes.lower() or b'<!doctype' in first_bytes.lower():
                            print(f"[ERROR] Downloaded file is HTML, not a valid media file!")
                            # Check for specific Google Drive error messages
                            if 'drive.google.com' in content_str or 'virus scan warning' in content_str or 'sign in' in content_str.lower():
                                temp_file_path.unlink()
                                
                                # Check for specific error types
                                if 'virus scan warning' in content_str or 'large file' in content_str.lower():
                                    return None, (
                                        "Google Drive file is too large or requires virus scan confirmation.\n\n"
                                        "For large files:\n"
                                        "1. Right-click file → 'Share' → 'Get link'\n"
                                        "2. Set to 'Anyone with the link' → 'Viewer'\n"
                                        "3. Try downloading manually first to confirm it works\n"
                                        "4. Or convert PDF to images and send those instead"
                                    )
                                elif 'sign in' in content_str.lower() or 'access denied' in content_str.lower():
                                    return None, (
                                        "Google Drive file requires authentication.\n\n"
                                        "To fix:\n"
                                        "1. Right-click the file in Google Drive\n"
                                        "2. Click 'Share' → 'Change to anyone with the link'\n"
                                        "3. Set permission to 'Viewer' (not 'Restricted')\n"
                                        "4. Copy the new link and try again\n\n"
                                        "The file must be publicly accessible without sign-in."
                                    )
                                else:
                                    return None, (
                                        "Google Drive file is not publicly accessible.\n\n"
                                        "To fix:\n"
                                        "1. Right-click the file in Google Drive\n"
                                        "2. Select 'Share' → 'Change to anyone with the link'\n"
                                        "3. Set permission to 'Viewer'\n"
                                        "4. Copy the new link and try again"
                                    )
                            else:
                                # HTML but not Google Drive - generic error
                                temp_file_path.unlink()
                                return None, "Downloaded file appears to be HTML. The file may require authentication or is not accessible."
                except Exception as e:
                    # If we can't read it, it might be locked - wait a moment and try again
                    import time
                    time.sleep(0.1)
                    try:
                        with open(temp_file_path, 'rb') as f:
                            first_bytes = f.read(1024)
                            content_str = first_bytes.decode('utf-8', errors='ignore').lower()
                            
                            if b'<html' in first_bytes.lower() or b'<!doctype' in first_bytes.lower():
                                if 'drive.google.com' in content_str:
                                    temp_file_path.unlink()
                                    return None, (
                                        "Google Drive file is not publicly accessible.\n\n"
                                        "Please share the file with 'Anyone with the link' and try again."
                                    )
                                else:
                                    temp_file_path.unlink()
                                    return None, "Downloaded file appears to be HTML. The file may require authentication."
                    except:
                        pass  # Continue with validation

            # Verify file was downloaded
            if not temp_file_path.exists() or temp_file_path.stat().st_size == 0:
                return None, "Downloaded file is empty"

            file_size = temp_file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                temp_file_path.unlink()  # Clean up
                return None, f"File too large ({file_size / 1024 / 1024:.2f}MB, max {self.MAX_FILE_SIZE / 1024 / 1024}MB)"

            print(f"[OK] Downloaded media: {temp_file_path.name} ({file_size / 1024:.2f}KB)")
            return str(temp_file_path), None

        except requests.exceptions.RequestException as e:
            return None, f"Failed to download media: {str(e)}"
        except Exception as e:
            return None, f"Error downloading media: {str(e)}"

    def is_valid_lab_report(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if file is a valid lab report (PDF or image).

        Args:
            file_path: Path to file

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)

        if not path.exists():
            return False, "File does not exist"

        # Check extension
        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type: {extension}. Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"

        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            return False, "File is empty"
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large ({file_size / 1024 / 1024:.2f}MB, max {self.MAX_FILE_SIZE / 1024 / 1024}MB)"

        return True, None

    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        Remove temporary file.

        Args:
            file_path: Path to file to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                print(f"[OK] Cleaned up temp file: {path.name}")
                return True
            return False
        except Exception as e:
            print(f"[WARN] Warning: Failed to cleanup temp file {file_path}: {str(e)}")
            return False

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        if not path.exists():
            return {"exists": False}

        stat = path.stat()
        return {
            "exists": True,
            "path": str(path),
            "name": path.name,
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "is_pdf": path.suffix.lower() == '.pdf',
            "is_image": path.suffix.lower() in self.SUPPORTED_IMAGE_EXTENSIONS,
        }

    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """
        Get file extension from Content-Type header.

        Args:
            content_type: Content-Type header value

        Returns:
            File extension (e.g., '.pdf', '.jpg') or None
        """
        content_type_lower = content_type.lower()

        # PDF
        if 'pdf' in content_type_lower:
            return '.pdf'

        # Images
        if 'jpeg' in content_type_lower or 'jpg' in content_type_lower:
            return '.jpg'
        if 'png' in content_type_lower:
            return '.png'
        if 'gif' in content_type_lower:
            return '.gif'
        if 'bmp' in content_type_lower:
            return '.bmp'
        if 'tiff' in content_type_lower:
            return '.tiff'

        return None


def extract_media_from_twilio_request(request_form: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract media information from Twilio webhook request.
    
    CRITICAL: Twilio WhatsApp sends media in different ways:
    - Images: NumMedia=1, MediaUrl0, MediaContentType0
    - Documents/PDFs: May have NumMedia=0 or 1, might use different fields
    - Always check ALL possible field names
    
    Args:
        request_form: Flask request.form dictionary

    Returns:
        Dictionary with media info or None if no media
    """
    print(f"\n[DEBUG] ========== EXTRACTING MEDIA ==========")
    print(f"[DEBUG] ALL REQUEST KEYS: {list(request_form.keys())}")
    print(f"[DEBUG] ALL REQUEST VALUES:")
    for key, value in request_form.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"[DEBUG]   {key}: {value[:100]}...")
        else:
            print(f"[DEBUG]   {key}: {value}")
    print(f"[DEBUG] ========================================\n")
    
    # Check ALL possible field names Twilio might use
    # Twilio WhatsApp can use various field names for media/documents
    
    # Method 1: Check NumMedia (standard media messages)
    num_media_str = request_form.get("NumMedia", "0")
    try:
        num_media = int(num_media_str)
    except (ValueError, TypeError):
        print(f"[DEBUG] Invalid NumMedia value: {num_media_str}, defaulting to 0")
        num_media = 0
    
    # Method 2: Check for MediaUrl0 (most common)
    media_url = request_form.get("MediaUrl0")
    media_content_type = request_form.get("MediaContentType0")
    media_sid = request_form.get("MediaSid0")
    
    # Method 3: Check for document-specific fields
    document_url = request_form.get("DocumentUrl")
    document_content_type = request_form.get("DocumentContentType")
    document_filename = request_form.get("DocumentFilename")
    
    # Method 4: Check MessageType
    message_type = request_form.get("MessageType", "").lower()
    
    # Method 5: Check for any URL in any field (comprehensive search)
    all_urls = []
    for key, value in request_form.items():
        if isinstance(value, str) and value.startswith("http"):
            all_urls.append((key, value))
            print(f"[DEBUG] Found URL in field '{key}': {value[:100]}...")
    
    # Priority: Use MediaUrl0 if available, then DocumentUrl, then any URL found
    final_media_url = media_url or document_url
    if not final_media_url and all_urls:
        # Use first URL found
        final_media_url = all_urls[0][1]
        print(f"[DEBUG] Using URL from field '{all_urls[0][0]}'")
    
    final_content_type = media_content_type or document_content_type
    final_sid = media_sid or request_form.get("MessageSid")
    final_filename = document_filename or request_form.get("MediaFilename")
    
    print(f"[DEBUG] Extraction Summary:")
    print(f"[DEBUG]   NumMedia: {num_media}")
    print(f"[DEBUG]   MessageType: {message_type}")
    print(f"[DEBUG]   MediaUrl0: {media_url[:100] if media_url else 'None'}...")
    print(f"[DEBUG]   DocumentUrl: {document_url[:100] if document_url else 'None'}...")
    print(f"[DEBUG]   Final URL: {final_media_url[:100] if final_media_url else 'None'}...")
    print(f"[DEBUG]   Content Type: {final_content_type}")
    
    # If we found ANY URL, treat it as media (even if NumMedia=0)
    if final_media_url:
        # Determine if it's a document or image
        is_document = (
            message_type == "document" or
            final_filename or
            (final_content_type and "pdf" in final_content_type.lower()) or
            (final_media_url.lower().endswith('.pdf'))
        )
        
        result = {
            "num_media": num_media if num_media > 0 else 1,  # Set to 1 if we found URL but NumMedia=0
            "media_url": final_media_url,
            "media_content_type": final_content_type or _guess_content_type_from_url(final_media_url),
            "media_sid": final_sid,
            "message_type": "document" if is_document else "media",
            "filename": final_filename,
        }
        print(f"[DEBUG] [OK] MEDIA DETECTED: {result}")
        return result
    
    # If NumMedia > 0 but no URL found, that's an error
    if num_media > 0:
        print(f"[WARN] NumMedia={num_media} but no MediaUrl0 found! Checking all MediaUrl fields...")
        # Check MediaUrl1, MediaUrl2, etc. (for multiple media)
        for i in range(num_media):
            url_key = f"MediaUrl{i}"
            if url_key in request_form:
                media_url = request_form[url_key]
                content_type = request_form.get(f"MediaContentType{i}")
                print(f"[DEBUG] Found {url_key}: {media_url[:100]}...")
                result = {
                    "num_media": num_media,
                    "media_url": media_url,
                    "media_content_type": content_type,
                    "media_sid": request_form.get(f"MediaSid{i}"),
                    "message_type": "media",
                }
                print(f"[DEBUG] [OK] MEDIA DETECTED (from MediaUrl{i}): {result}")
                return result
    
    print(f"[DEBUG] [ERROR] NO MEDIA DETECTED")
    return None


def _guess_content_type_from_url(url: str) -> str:
    """Guess content type from URL extension."""
    url_lower = url.lower()
    if url_lower.endswith('.pdf'):
        return "application/pdf"
    elif url_lower.endswith(('.jpg', '.jpeg')):
        return "image/jpeg"
    elif url_lower.endswith('.png'):
        return "image/png"
    elif url_lower.endswith('.gif'):
        return "image/gif"
    return "application/octet-stream"

