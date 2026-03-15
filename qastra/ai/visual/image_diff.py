"""
Image comparison engine for visual regression testing.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import os
from typing import Tuple, Optional


class ImageDiff:
    """Advanced image comparison for visual regression testing."""
    
    def __init__(self, threshold: float = 10.0):
        self.threshold = threshold
    
    def compare_images(self, baseline_path: str, current_path: str) -> Tuple[float, np.ndarray]:
        """
        Compare two images and return difference score and diff image.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            
        Returns:
            Tuple of (difference_score, diff_image)
        """
        try:
            # Load images
            baseline = cv2.imread(baseline_path)
            current = cv2.imread(current_path)
            
            if baseline is None or current is None:
                raise ValueError("Could not load one or both images")
            
            # Ensure images have same dimensions
            if baseline.shape != current.shape:
                # Resize current to match baseline
                current = cv2.resize(current, (baseline.shape[1], baseline.shape[0]))
            
            # Calculate absolute difference
            diff = cv2.absdiff(baseline, current)
            
            # Convert to grayscale for scoring
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Calculate difference score (0 = identical, higher = more different)
            score = np.mean(gray_diff)
            
            return score, diff
        
        except Exception as e:
            print(f"Error comparing images: {e}")
            return float('inf'), np.zeros((100, 100, 3), dtype=np.uint8)
    
    def create_highlighted_diff(self, baseline_path: str, current_path: str, diff_image: np.ndarray) -> np.ndarray:
        """
        Create a highlighted diff image showing changes in red.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            diff_image: Difference image from compare_images
            
        Returns:
            Highlighted diff image
        """
        try:
            baseline = cv2.imread(baseline_path)
            current = cv2.imread(current_path)
            
            # Create a mask of significant differences
            gray_diff = cv2.cvtColor(diff_image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Create highlighted version
            highlighted = current.copy()
            
            # Highlight differences in red
            highlighted[mask > 0] = [0, 0, 255]  # Red color (BGR format)
            
            # Blend with original to show context
            alpha = 0.7
            result = cv2.addWeighted(highlighted, alpha, current, 1 - alpha, 0)
            
            return result
        
        except Exception as e:
            print(f"Error creating highlighted diff: {e}")
            return diff_image
    
    def get_pixel_difference_percentage(self, baseline_path: str, current_path: str) -> float:
        """
        Calculate percentage of pixels that differ significantly.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            
        Returns:
            Percentage of different pixels (0-100)
        """
        try:
            score, diff = self.compare_images(baseline_path, current_path)
            
            # Normalize score to percentage (assuming max pixel difference is 255)
            max_possible_score = 255.0
            percentage = (score / max_possible_score) * 100
            
            return min(percentage, 100.0)
        
        except Exception as e:
            print(f"Error calculating difference percentage: {e}")
            return 100.0
    
    def detect_layout_changes(self, baseline_path: str, current_path: str) -> dict:
        """
        Detect specific types of layout changes.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            
        Returns:
            Dictionary with detected changes
        """
        try:
            baseline = cv2.imread(baseline_path)
            current = cv2.imread(current_path)
            
            # Convert to grayscale for analysis
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
            current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            baseline_edges = cv2.Canny(baseline_gray, 50, 150)
            current_edges = cv2.Canny(current_gray, 50, 150)
            
            # Find structural differences
            edge_diff = cv2.absdiff(baseline_edges, current_edges)
            edge_changes = np.sum(edge_diff > 0)
            
            # Detect color changes
            baseline_hsv = cv2.cvtColor(baseline, cv2.COLOR_BGR2HSV)
            current_hsv = cv2.cvtColor(current, cv2.COLOR_BGR2HSV)
            
            hue_diff = cv2.absdiff(baseline_hsv[:, :, 0], current_hsv[:, :, 0])
            color_changes = np.sum(hue_diff > 30)
            
            return {
                'layout_changes': edge_changes,
                'color_changes': color_changes,
                'total_pixels': baseline.shape[0] * baseline.shape[1],
                'layout_change_percentage': (edge_changes / (baseline.shape[0] * baseline.shape[1])) * 100,
                'color_change_percentage': (color_changes / (baseline.shape[0] * baseline.shape[1])) * 100
            }
        
        except Exception as e:
            print(f"Error detecting layout changes: {e}")
            return {
                'layout_changes': 0,
                'color_changes': 0,
                'total_pixels': 1,
                'layout_change_percentage': 0,
                'color_change_percentage': 0
            }
    
    def save_diff_report(self, baseline_path: str, current_path: str, output_dir: str, name: str) -> dict:
        """
        Generate comprehensive diff report and save all images.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            output_dir: Directory to save report
            name: Base name for files
            
        Returns:
            Report dictionary
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Basic comparison
        score, diff_image = self.compare_images(baseline_path, current_path)
        
        # Create highlighted diff
        highlighted_diff = self.create_highlighted_diff(baseline_path, current_path, diff_image)
        
        # Calculate percentages
        pixel_diff_percentage = self.get_pixel_difference_percentage(baseline_path, current_path)
        
        # Detect specific changes
        layout_analysis = self.detect_layout_changes(baseline_path, current_path)
        
        # Save images
        diff_path = os.path.join(output_dir, f"{name}_diff.png")
        highlighted_path = os.path.join(output_dir, f"{name}_highlighted.png")
        
        cv2.imwrite(diff_path, diff_image)
        cv2.imwrite(highlighted_path, highlighted_diff)
        
        # Generate report
        report = {
            'name': name,
            'difference_score': score,
            'pixel_difference_percentage': pixel_diff_percentage,
            'threshold': self.threshold,
            'passed': score <= self.threshold,
            'layout_analysis': layout_analysis,
            'files': {
                'baseline': baseline_path,
                'current': current_path,
                'diff': diff_path,
                'highlighted': highlighted_path
            }
        }
        
        # Save report as JSON
        import json
        report_path = os.path.join(output_dir, f"{name}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)  # Add default=str to handle bool serialization
        
        return report
    
    def batch_compare(self, baseline_dir: str, current_dir: str, output_dir: str) -> list:
        """
        Compare multiple image pairs in batch.
        
        Args:
            baseline_dir: Directory containing baseline images
            current_dir: Directory containing current images
            output_dir: Directory to save results
            
        Returns:
            List of comparison reports
        """
        reports = []
        
        baseline_files = [f for f in os.listdir(baseline_dir) if f.endswith('.png')]
        
        for filename in baseline_files:
            baseline_path = os.path.join(baseline_dir, filename)
            current_path = os.path.join(current_dir, filename)
            
            if os.path.exists(current_path):
                name = filename.replace('.png', '')
                report = self.save_diff_report(baseline_path, current_path, output_dir, name)
                reports.append(report)
        
        return reports


# Convenience functions
def compare_images(baseline_path: str, current_path: str, threshold: float = 10.0) -> Tuple[float, np.ndarray]:
    """Quick image comparison function."""
    diff_engine = ImageDiff(threshold)
    return diff_engine.compare_images(baseline_path, current_path)


def save_diff(diff_image: np.ndarray, name: str, output_dir: str = ".qastra_visual/diff"):
    """Quick diff saving function."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.png")
    cv2.imwrite(path, diff_image)
    print(f"Visual difference saved: {path}")
    return path


def get_visual_report(baseline_path: str, current_path: str, name: str, 
                     output_dir: str = ".qastra_visual/diff", threshold: float = 10.0) -> dict:
    """Quick visual report generation."""
    diff_engine = ImageDiff(threshold)
    return diff_engine.save_diff_report(baseline_path, current_path, output_dir, name)
