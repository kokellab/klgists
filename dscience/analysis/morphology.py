import numpy as np
from PIL import Image
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.morphology import convex_hull_image


class ConvexHullCropper:
	"""Auto-crops images based on their convex hull, assuming a white or transparent background.
	Idea & code from Sandipan Dey's answer on
	https://stackoverflow.com/questions/14211340/automatically-cropping-an-image-with-python-pil
	"""

	def crop(self, im_array: np.array) -> Image:
		# create a binary image first
		im1 = 1 - rgb2gray(im_array)
		im1[im1 <= 0.5] = 0
		im1[im1 > 0.5] = 1
		# now compute the hull
		chull = convex_hull_image(im1)
		# now crop
		img_box = Image.fromarray((chull * 255).astype(np.uint8)).getbbox()
		return Image.fromarray(im_array).crop(img_box)

	def crop_file(self, from_path: str, to_path: str):
		im = imread(from_path)
		cropped = self.crop(im)
		cropped.save(to_path)

	def __repr__(self):
		return type(self).__name__

	def __str__(self): return repr(self)


__all__ = ['ConvexHullCropper']
