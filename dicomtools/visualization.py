import matplotlib.pylab as plt
#
def plot_slice(dicom_volume, slice_axis, slice_index, figure=None):
	r'''
	Plot a single slice (along axis 0, 1, or 2) of a :class:`dicomtools.volume.DicomVolume` using matplotlib.
	'''
	#
	dimension_indices = [0, 1, 2]
	dimension_labels = ['Axis {} (mm)'.format(x) for x in range(3)]
	assert slice_axis in dimension_indices
	#
	dimension_indices.pop(slice_axis)
	dimension_labels.pop(slice_axis)
	#
	slice = dicom_volume.info['pixel_data'].take(slice_index, axis=slice_axis)
	#
	volume_dimensions = dicom_volume.get_dimensions_in_mm()
	x_range = [0, volume_dimensions[dimension_indices[0]]]
	y_range = [0, volume_dimensions[dimension_indices[1]]]
	#
	if figure is None:
		plt.figure()
	#
	plt.imshow(slice, interpolation='none', aspect=1, extent=x_range+y_range, cmap=plt.cm.gray)
	plt.xlabel(dimension_labels[0])
	plt.ylabel(dimension_labels[1])
	plt.title('{} - slice {} along axis {}'.format(dicom_volume.description, slice_index, slice_axis))
	#
	if figure is None:
		plt.show()
	#
#
