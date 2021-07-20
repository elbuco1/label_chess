from label_chess import utils 
from PIL import Image


def test_resize_image():
    width, height = 1280, 720
    img = Image.new('RGB', (width, height))
    expected_height = 1000
    expected_ratio = height / width

    img = utils.resize_image(img, expected_height)

    r_width, r_height = img.size 

    assert expected_height == r_height 
    assert round(expected_ratio, 2) == round(r_height / r_width , 2)