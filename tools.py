from PIL import Image
import random
from bs4 import BeautifulSoup
import requests
import regex as re
import time


def resize_image(input_file, request):
    """open and resize image
        :param input_file: file path on server
        :type input_file: string

        :param request: request from user (resizing argument)
        :type input_file: string

        :rtype: tuple (Boolean, pillow image) or (Boolean, string)
        :return: resized image or error description
    """
    sizes_px = re.findall(r'[0-9.]+px', request)
    sizes_percent = re.findall(r'[0-9.]+z', request)

    im1 = Image.open(input_file)

    width, height = im1.size

    if len(sizes_px) > 0:
        parsed_px = float(sizes_px[0][:-2])
        coef_ = parsed_px / max(width, height)
        if parsed_px > 1000 or parsed_px <= 50:
            return False, "Wrong request, read manual /help"

    elif len(sizes_percent) > 0:
        coef_ = float(sizes_percent[0][:-1])
        if coef_ > 10 or coef_ <= 0.1:
            return False, "Wrong request, read manual /help"
    else:
        return False, "No arguments found, read manual /help"

    width_new = width * coef_
    height_new = height * coef_

    # resize image
    im1_out = im1.resize((int(width_new), int(height_new)))

    return True, im1_out


def convert_image(input_file, new_format):
    """open and convert image
        :param input_file: file path on server
        :type input_file: string

        :param new_format: request from user (format for convert)
        :type input_file: string

        :rtype: (file object, string)
        :return: file with converted image, new image's path
    """
    im = Image.open(input_file)
    old_format = im.format
    rgb_im = im.convert('RGB')
    path = "./photos/converted/image_%s.%s" % (str(int(time.time() * 1000)), new_format)
    rgb_im.save(path, quality=95)
    ret_img = open(path, 'rb')
    return ret_img, path


def get_random(request_word):
    """search random image in web
        :param request_word: request from user
        :type request_word: string

        :rtype: URL
        :return: url of image in web
    """
    s = requests.session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})

    r = s.get('https://www.google.ru/search?q=' + request_word + '&tbm=isch')
    if r is not None:

        soup = BeautifulSoup(r.text, "html.parser")

        images = soup.findAll(attrs={'class': 'wXeWr islib nfEiy'})
        images = [img for img in images if "data-src" in str(img)]
        if len(images) == 0:
            return ""
        random_ref = random.choice(images)
        return random_ref.img["data-src"]
