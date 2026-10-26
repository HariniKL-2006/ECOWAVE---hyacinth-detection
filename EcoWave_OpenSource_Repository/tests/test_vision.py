import cv2, numpy as np, pytest
from vision.segment_hyacinth import create_vegetation_mask, filter_small_contours

def test_invalid_image():
    with pytest.raises(ValueError): create_vegetation_mask(np.array([]))

def test_green_patch_detected():
    img=np.zeros((100,100,3),dtype=np.uint8); img[:]=(180,80,20); img[25:75,25:75]=(30,180,30)
    mask=create_vegetation_mask(img,{"h_min":25,"h_max":95,"s_min":35,"v_min":30,"min_area":100})
    assert mask.shape==(100,100) and set(np.unique(mask)).issubset({0,255})
    assert int(mask[50,50])==255

def test_small_contour_filter():
    mask=np.zeros((50,50),dtype=np.uint8); cv2.rectangle(mask,(5,5),(20,20),255,-1)
    assert len(filter_small_contours(mask,50))==1
