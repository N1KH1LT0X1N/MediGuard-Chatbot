"""
Direct test of Google Drive URL download to diagnose the issue.
"""
import requests
import re
from pathlib import Path

def test_google_drive_download():
    """Test Google Drive URL download with different methods."""
    
    drive_url = "https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk"
    
    print(f"\n{'='*60}")
    print(f"TESTING GOOGLE DRIVE URL DOWNLOAD")
    print(f"{'='*60}\n")
    
    # Extract file ID
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', drive_url)
    if not match:
        print("[ERROR] Could not extract file ID")
        return False
    
    file_id = match.group(1)
    print(f"[OK] File ID: {file_id}\n")
    
    # Method 1: Standard direct download
    print("[TEST 1] Standard direct download URL")
    url1 = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"URL: {url1}")
    
    try:
        session = requests.Session()
        response = session.get(url1, timeout=30, allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'None')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'None')}")
        
        if response.status_code in [302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            print(f"Redirect to: {redirect_url[:100] if redirect_url else 'None'}...")
            # Follow redirect
            response = session.get(redirect_url, timeout=30, allow_redirects=True)
            print(f"After redirect - Status: {response.status_code}")
            print(f"After redirect - Content-Type: {response.headers.get('Content-Type', 'None')}")
        
        # Check first bytes
        first_bytes = response.content[:500]
        content_str = first_bytes.decode('utf-8', errors='ignore').lower()
        
        print(f"First 200 chars: {content_str[:200]}")
        
        if '<html' in content_str or '<!doctype' in content_str:
            print("[ERROR] Response is HTML, not a file!")
            if 'sign in' in content_str or 'access denied' in content_str:
                print("[ERROR] File requires authentication!")
            elif 'virus scan' in content_str or 'large file' in content_str:
                print("[ERROR] Large file - virus scan warning!")
            return False
        else:
            print("[OK] Response appears to be a file (not HTML)")
            # Check if it's PDF
            if first_bytes[:4] == b'%PDF':
                print("[OK] File is a valid PDF!")
                # Save it
                test_file = Path("test_download.pdf")
                with open(test_file, 'wb') as f:
                    f.write(response.content)
                print(f"[OK] Saved to: {test_file}")
                print(f"[OK] File size: {test_file.stat().st_size} bytes")
                return True
            else:
                print(f"[WARN] File doesn't start with PDF header")
                print(f"First 20 bytes (hex): {first_bytes[:20].hex()}")
                return False
                
    except Exception as e:
        print(f"[ERROR] Method 1 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_google_drive_download()

