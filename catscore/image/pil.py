from PIL import Image
from catscore.lib.logger import CatsLogging as logging

class CatsPil:
    @classmethod
    def resize_fix_aspect_ratio(cls, input_fullpath: str, output_fullpath: str, width=None, high=None):
        img = Image.open(input_fullpath)
        logging.debug("resize_fix_aspect_ratio")
        logging.debug("base size　width: {}, height: {}".format(img.size[0], img.size[1]))
        resize_image = img.resize((width, int(width * img.size[1] / img.size[0])))
        logging.debug("resized　width: {}, height: {}".format(resize_image.size[0], resize_image.size[1])) 
        resize_image.save(output_fullpath)