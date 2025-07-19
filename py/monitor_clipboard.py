import os
import hashlib
import shutil
import logging
import argparse
from typing import Optional, List
from pathlib import Path
from PIL import ImageGrab, Image
import time
import filetype
import PIL
import ctypes

# Configuration constants
OUTPUT_DIR = "F:\\pics"

DEBUG = False
SLEEP_DURATION_SHORT = 0.1
SLEEP_DURATION_LONG = 2
INACTIVITY_THRESHOLD = 10  # seconds

MAX_CACHE_FILES = 99 #number of files to check in the cache
BRAVE_CACHE_PATH = r"%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Cache\Cache_Data"
BRAVE_CACHE_PATH = os.path.expandvars(BRAVE_CACHE_PATH)
HASH_FILE = os.path.join(OUTPUT_DIR, "sha256.txt")

# Global cache for image hashes
cached_hashes = {}

# Setup logging
def setup_logging(debug: bool = False) -> None:
    """Configure logging with appropriate level."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('clipboard_monitor.log')
        ]
    )

def validate_paths() -> None:
    """Validate that required paths exist."""
    if not os.path.exists(BRAVE_CACHE_PATH):
        logging.error(f"Brave cache path does not exist: {BRAVE_CACHE_PATH}")
        exit(1)

    if not os.path.exists(OUTPUT_DIR):
        logging.error(f"Output directory does not exist: {OUTPUT_DIR}")
        exit(1)

def get_clipboard_sequence_number() -> int:
    """Get the current clipboard sequence number."""
    return ctypes.windll.user32.GetClipboardSequenceNumber()

def get_clipboard_image() -> Optional[Image.Image]:
    """
    Get image from clipboard if available.
    
    Returns:
        PIL Image object if clipboard contains an image, None otherwise.
    """
    try:
        image = ImageGrab.grabclipboard()
        if image:
            logging.debug(f"Clipboard contains an image of type {type(image)}")
            return image
        else:
            logging.debug("No image found in clipboard")
            return None
    except Exception as e:
        logging.error(f"Error accessing clipboard: {e}")
        return None

def get_last_files_in_cache(n: int = MAX_CACHE_FILES) -> List[str]:
    """
    Get the most recently modified files from Brave cache.
    
    Args:
        n: Maximum number of files to return
        
    Returns:
        List of filenames sorted by modification time (newest first)
    """
    try:
        files = sorted(
            os.listdir(BRAVE_CACHE_PATH), 
            key=lambda x: os.path.getmtime(os.path.join(BRAVE_CACHE_PATH, x)), 
            reverse=True
        )
        return files[:n]
    except OSError as e:
        logging.error(f"Error reading cache directory: {e}")
        return []

def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        result = file_hash.hexdigest()
        logging.debug(f"Calculated hash for {file_path}: {result}")
        return result
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return ""

def calculate_image_hash(file_path: str) -> Optional[str]:
    """
    Calculate hash of image data with caching.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        SHA256 hash of image data or None if error
    """
    if file_path in cached_hashes:
        return cached_hashes[file_path]
    
    try:
        with Image.open(file_path) as image:
            hash_value = hashlib.sha256(image.tobytes()).hexdigest()
            cached_hashes[file_path] = hash_value
            return hash_value
    except Exception as e:
        logging.debug(f"Error calculating image hash for {file_path}: {e}")
        return None

def is_hash_duplicate(clipboard_hash: str) -> bool:
    """
    Check if hash already exists in the hash file.
    
    Args:
        clipboard_hash: Hash to check for duplicates
        
    Returns:
        True if hash is a duplicate, False otherwise
    """
    try:
        with open(HASH_FILE, "r") as hash_file:
            content = hash_file.read()
            return f"{clipboard_hash} " in content
    except FileNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Error reading hash file: {e}")
        return False

def save_image_with_hash(file_path: str, clipboard_hash: str) -> bool:
    """
    Save image file to output directory with hash-based filename.
    
    Args:
        file_path: Source file path
        clipboard_hash: Hash to use for filename and tracking
        
    Returns:
        True if successful, False otherwise
    """
    try:
        kind = filetype.guess(file_path)
        if not kind:
            logging.warning(f"Could not determine file type for {file_path}")
            return False
            
        ext = kind.extension
        new_file_path = os.path.join(OUTPUT_DIR, f"{clipboard_hash}.{ext}")
        
        shutil.copyfile(file_path, new_file_path)
        
        with open(HASH_FILE, "a") as hash_file:
            hash_file.write(f"{clipboard_hash} {new_file_path}\n")
            
        logging.info(f"Copied {os.path.basename(file_path)} to {new_file_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return False

def process_clipboard_image(clipboard_image: Image.Image) -> Optional[str]:
    """
    Process clipboard image and find matching cache file.
    
    Args:
        clipboard_image: PIL Image from clipboard
        
    Returns:
        Hash of the image if processed successfully, None otherwise
    """
    try:
        clipboard_hash = hashlib.sha256(clipboard_image.tobytes()).hexdigest()
        logging.debug(f"Clipboard hash: {clipboard_hash}")
        
        if is_hash_duplicate(clipboard_hash):
            logging.debug(f"Hash {clipboard_hash} already exists, skipping")
            return clipboard_hash
            
        last_files = get_last_files_in_cache(MAX_CACHE_FILES)
        
        for file_name in last_files:
            if not file_name.startswith("f_"):
                continue
                
            file_path = os.path.join(BRAVE_CACHE_PATH, file_name)
            if not os.path.isfile(file_path):
                continue
                
            file_hash = calculate_image_hash(file_path)
            if file_hash is None:
                continue
                
            logging.debug(f"File hash: {file_hash}")
            
            if file_hash == clipboard_hash:
                logging.debug(f"Found matching file: {file_name}")
                if save_image_with_hash(file_path, clipboard_hash):
                    return clipboard_hash
                break
                
        return clipboard_hash
        
    except Exception as e:
        logging.error(f"Error processing clipboard image: {e}")
        return None

def main() -> None:
    """Main monitoring loop."""
    setup_logging(DEBUG)
    validate_paths()
    
    logging.info("Starting clipboard monitor...")
    
    last_clipboard_hash = None  
    last_clipboard_sequence_number = None
    last_action_time = time.time()

    try:
        while True:
            clipboard_sequence_number = get_clipboard_sequence_number()
            
            # Skip if clipboard hasn't changed
            if clipboard_sequence_number == last_clipboard_sequence_number:
                continue
                
            last_clipboard_sequence_number = clipboard_sequence_number
            clipboard_image = get_clipboard_image()
            
            if clipboard_image:
                current_hash = process_clipboard_image(clipboard_image)
                
                # Skip if same image as before
                if current_hash == last_clipboard_hash:
                    continue
                    
                last_clipboard_hash = current_hash
                last_action_time = time.time()
            
            # Adaptive sleep based on activity
            if time.time() - last_action_time > INACTIVITY_THRESHOLD:
                time.sleep(SLEEP_DURATION_LONG)
            else:
                time.sleep(SLEEP_DURATION_SHORT)
                
    except KeyboardInterrupt:
        logging.info("Clipboard monitor stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor clipboard for images and save from browser cache")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    if args.debug:
        DEBUG = True
        
    main()