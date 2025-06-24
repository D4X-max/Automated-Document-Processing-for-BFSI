import cv2
import numpy as np
import argparse

def preprocess_image(image_bytes: bytes):
    """
    Takes image bytes and applies a more robust series of preprocessing steps.
    This version is less aggressive and prioritizes stability.
    """
    # Convert bytes to a numpy array and decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # --- 1. Convert to Grayscale ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- 2. Apply a gentle blur to reduce noise ---
    # This helps Otsu's thresholding to work better.
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # --- 3. Binarization using Otsu's Method ---
    # This automatically determines the best threshold value to separate text from background.
    # It's more reliable than adaptive thresholding when lighting conditions are decent.
    # We invert the image (THRESH_BINARY_INV) so the text is white (255) and background is black (0).
    # Tesseract often performs well with white text on a black background.
    _, final_image = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # We are temporarily removing the automatic deskewing as it's the most likely
    # point of failure. Manual rotation or simpler methods are often better.
    print("Using robust preprocessing with Otsu's Thresholding.")
    
    return final_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="Path to the input image")
    args = parser.parse_args()
    

