"""
Utility functions for clipboard operations and image handling.
"""

import subprocess
import platform
from typing import Optional
from PIL import Image


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.
    
    Args:
        text: The text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], 
                             input=text, text=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], 
                                 input=text, text=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return False
                    
        elif system == "Windows":
            subprocess.run(['clip'], input=text, text=True, check=True)
            return True
            
        elif system == "Darwin":  # macOS
            subprocess.run(['pbcopy'], input=text, text=True, check=True)
            return True
        else:
            return False
            
    except Exception:
        return False


def get_from_clipboard() -> Optional[str]:
    """
    Get text from system clipboard.
    
    Returns:
        Text from clipboard, or None if error
    """
    try:
        system = platform.system()
        
        if system == "Linux":
            try:
                result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                      capture_output=True, text=True, check=True)
                return result.stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                          capture_output=True, text=True, check=True)
                    return result.stdout
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return None
                    
        elif system == "Windows":
            result = subprocess.run(['powershell', '-command', 'Get-Clipboard'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout
            
        elif system == "Darwin":  # macOS
            result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
            return result.stdout
        else:
            return None
            
    except Exception:
        return None


def resize_image(image_path: str, output_path: str, size: tuple = (450, 450)) -> bool:
    """
    Resize an image to specified dimensions.
    
    Args:
        image_path: Path to source image
        output_path: Path to save resized image
        size: Tuple of (width, height)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        img = Image.open(image_path)
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        img_resized.save(output_path)
        return True
    except Exception:
        return False


def crop_image(image_path: str, output_path: str, crop_box: tuple, size: tuple = (450, 450)) -> bool:
    """
    Crop and resize an image.
    
    Args:
        image_path: Path to source image
        output_path: Path to save cropped image
        crop_box: Tuple of (left, top, right, bottom)
        size: Tuple of (width, height) for final resize
        
    Returns:
        True if successful, False otherwise
    """
    try:
        img = Image.open(image_path)
        cropped = img.crop(crop_box)
        cropped_resized = cropped.resize(size, Image.Resampling.LANCZOS)
        cropped_resized.save(output_path)
        return True
    except Exception:
        return False
