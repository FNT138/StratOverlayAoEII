"""
Template matching for UI element detection
Uses OpenCV for pattern matching
"""
import cv2
import numpy as np
from typing import Tuple, Optional
from pathlib import Path


class TemplateMatcher:
    """Handles template matching for detecting UI elements"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize template matcher
        
        Args:
            confidence_threshold: Minimum confidence (0-1) for a match
        """
        self.confidence_threshold = confidence_threshold
        self.templates = {}  # Cache loaded templates
    
    def load_template(self, template_path: str, name: str):
        """
        Load a template image from file
        
        Args:
            template_path: Path to template image
            name: Name to store template under
        """
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Could not load template from {template_path}")
        self.templates[name] = template
    
    def find_template(
        self, 
        image: np.ndarray, 
        template: np.ndarray,
        method: int = cv2.TM_CCOEFF_NORMED
    ) -> Optional[Tuple[int, int, float]]:
        """
        Find a template in an image
        
        Args:
            image: Source image to search in
            template: Template image to find
            method: OpenCV matching method
            
        Returns:
            Tuple of (x, y, confidence) or None if not found
        """
        # Ensure images are the same type
        if len(image.shape) == 3 and len(template.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2 and len(template.shape) == 3:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Perform template matching
        result = cv2.matchTemplate(image, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Get the best match location
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            confidence = 1 - min_val
            location = min_loc
        else:
            confidence = max_val
            location = max_loc
        
        if confidence >= self.confidence_threshold:
            return (location[0], location[1], confidence)
        
        return None
    
    def find_all_matches(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: Optional[float] = None
    ) -> list:
        """
        Find all occurrences of a template in an image
        
        Args:
            image: Source image
            template: Template to find
            threshold: Confidence threshold (uses default if None)
            
        Returns:
            List of tuples (x, y, confidence)
        """
        if threshold is None:
            threshold = self.confidence_threshold
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image
            
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
        
        # Perform matching
        result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Find all locations above threshold
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            confidence = result[pt[1], pt[0]]
            matches.append((pt[0], pt[1], float(confidence)))
        
        return matches
    
    def extract_number_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Extract a region from image (for number recognition)
        
        Args:
            image: Source image
            x, y: Top-left corner
            width, height: Region size
            
        Returns:
            Extracted region as numpy array
        """
        return image[y:y+height, x:x+width].copy()
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess an image region for better OCR/number recognition
        
        Args:
            image: Input image region
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Optional: denoise
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return denoised
    
    def simple_digit_recognition(self, region: np.ndarray) -> Optional[int]:
        """
        Simple digit recognition using template matching
        This is a placeholder - in Phase 2 we'll improve this
        
        Args:
            region: Image region containing a number
            
        Returns:
            Recognized number or None
        """
        # For now, return None - we'll implement proper recognition later
        # Options: pytesseract, custom digit templates, or ML model
        return None
