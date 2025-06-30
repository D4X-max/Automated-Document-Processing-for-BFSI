import easyocr
import cv2
import numpy as np

# --- Load the EasyOCR reader into memory ---
# We specify English ('en') and Hindi ('hi')
# This will download the models the first time it's run.
print("Loading EasyOCR models into memory...")
reader = easyocr.Reader(['en', 'hi'], gpu=False) # Set gpu=True if you have a compatible GPU
print("EasyOCR models loaded successfully.")


# We can keep our advanced preprocessing as it helps all OCR engines
from skimage.transform import rotate
from skimage.color import rgb2gray
from skimage.feature import canny
from scipy.ndimage import sobel

def deskew_image(image: np.ndarray) -> np.ndarray:
    # This function remains unchanged.
    grayscale = rgb2gray(image)
    edges = canny(grayscale, sigma=3.0)
    sobel_filtered = sobel(edges)
    coords = np.column_stack(np.where(sobel_filtered > 0))
    if coords.shape[0] <= 1:
        return image
    mean = np.mean(coords, axis=0)
    coords_centered = coords - mean
    cov = np.cov(coords_centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    vec = eigenvectors[:, -1]
    angle = np.degrees(np.arctan2(vec[1], vec[0]))
    if abs(angle) > 45:
        angle = (90 - abs(angle)) * np.sign(angle)
    return rotate(image, angle, resize=True, mode='constant', cval=1, preserve_range=True).astype(np.uint8)

def preprocess_for_easyocr(image_bytes: bytes):
    # Preprocessing for EasyOCR is simpler; it handles a lot internally.
    # We'll just do deskewing and read the image.
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    deskewed_img = deskew_image(img)
    return deskewed_img

def extract_text(image_bytes: bytes) -> str:
    """
    Takes image bytes, preprocesses, and extracts text using EasyOCR.
    """
    processed_image = preprocess_for_easyocr(image_bytes)
    
    # EasyOCR returns a list of (bounding_box, text, confidence)
    results = reader.readtext(processed_image)
    
    # We'll combine the extracted text into a single string
    raw_text = "\n".join([res[1] for res in results])
    
    return raw_text

