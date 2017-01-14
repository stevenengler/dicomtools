import numpy as np
import os
import matplotlib
#
def export_stack_to_png(images, axis, directory, filename_prefix):
	r'''
	Given a 3-dimensional array, save each slice to a file. Use the 'axis'
	argument to describe which axis to iterate over.
	'''
	#
	for x in range(images.shape[axis]):
		img = images.take(x, axis=axis)
		filename = os.path.join(directory, filename_prefix)
		filename += '_{}.png'.format(x)
		#
		export_image_to_png(img, filename)
	#
#
def export_image_to_png(image, filename):
	r'''
	Given a 2-dimensional image, save it to a file.
	'''
	#
	matplotlib.image.imsave(filename, image, cmap=matplotlib.cm.gray)
	# let matplotlib deal with saving the image since it probably already has a supported backend
#
