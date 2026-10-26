import argparse, os
from pathlib import Path
import cv2
import numpy as np
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_config():
    return {"h_min": int(os.getenv("ECOWAVE_H_MIN", "25")),
            "h_max": int(os.getenv("ECOWAVE_H_MAX", "95")),
            "s_min": int(os.getenv("ECOWAVE_S_MIN", "35")),
            "v_min": int(os.getenv("ECOWAVE_V_MIN", "30")),
            "min_area": int(os.getenv("ECOWAVE_MIN_AREA", "150"))}

def create_vegetation_mask(image, config=None):
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("image must be a non-empty OpenCV image array")
    c = config or get_config()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([c["h_min"], c["s_min"], c["v_min"]], np.uint8),
                       np.array([c["h_max"], 255, 255], np.uint8))
    k = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)

def filter_small_contours(mask, min_area=None):
    area = get_config()["min_area"] if min_area is None else int(min_area)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) >= area]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True); p.add_argument("--output", required=True)
    a = p.parse_args()
    image = cv2.imread(a.input)
    if image is None: p.error(f"Could not read image: {a.input}")
    mask = create_vegetation_mask(image)
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(a.output, mask): p.error(f"Could not write: {a.output}")
    print(f"Saved mask: {a.output}; candidate regions: {len(filter_small_contours(mask))}")
if __name__ == "__main__": main()
