# -*- coding: utf-8 -*-
import base64
import os
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from PIL import Image


from openerp.tools.translate import _
import logging
logger = logging.getLogger(__name__)


def resize_to_thumbnail(img, box=(440, 440), fit='mid'):
    """Downsample the image.
    @param img: Image - base64 Image Data
    @param box: tuple(x, y) - the bounding box of the result image
    @param fit: char - 'top' crops to the top, any other value crops to the middle
    """

    # DECODE the img to an base64 PIL object
    img = Image.open(StringIO.StringIO(img.decode('base64')))
    filetype = img.format.upper()
    filetype = {'BMP': 'PNG', }.get(filetype, filetype)
    if img.mode not in ["1", "L", "P", "RGB", "RGBA"]:
        img = img.convert("RGB")

    # Crop the image
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2/box[0]
        hRatio = 1.0 * y2/box[1]
        if hRatio > wRatio:
            y1 = int(y2/2-box[1]*wRatio/2)
            y2 = int(y2/2+box[1]*wRatio/2)
        else:
            x1 = int(x2/2-box[0]*hRatio/2)
            x2 = int(x2/2+box[0]*hRatio/2)
        if fit == 'top':
            y2 -= y1
            y1 = 0
        img = img.crop((x1, y1, x2, y2))

    # Resize the image
    img.thumbnail(box, Image.ANTIALIAS)

    # RETURN the image
    background_stream = StringIO.StringIO()
    img.save(background_stream, filetype)
    return background_stream.getvalue().encode('base64')


# Get a screen-shot for the target URL
# http://randomdotnext.com/selenium-phantomjs-on-aws-ec2-ubuntu-instance-headless-browser-automation/
# TODO: Add Timeouts
def screenshot(url, src_width=1024, src_height=768, tgt_width=int(), tgt_height=int()):
    # Import selenium
    try:
        from selenium import webdriver
    except ImportError:
        logger.error(_('Could not import selenium for screen-shot generation of %s!') % url)
        return False

    # Load PhantomJS()
    try:
        driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
    except Exception as error:
        logger.error(_('Could not load PhantomJS() for screen-shot generation of %s!\n\n%s\n') % (url, error))
        return False

    # Generate screen-shot
    try:
        driver.set_window_size(src_width, src_height)
        driver.get(url)
        image = driver.get_screenshot_as_png()
        image = base64.b64encode(image)
    except Exception as error:
        logger.warning('Could not generate screen-shot for url:\n\n%s\n' % error)
        return False

    # Resize Image
    if tgt_width or tgt_height:
        x = tgt_width or 320
        y = tgt_height or 240
        image = resize_to_thumbnail(image, box=(x, y), fit='top')

    # Return Image
    return image
