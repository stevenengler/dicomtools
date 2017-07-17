import numpy as np
import dicom
import os
import warnings
#
from . import coordinates
from . import export
#
class DicomVolume(object):
	r'''
	Simplifies working with 3D DICOM data.
	'''
	def __init__(self, dicom_series):
		r'''
		Given a DicomSeries object, this determines volume data about the
		series.
		'''
		#
		self._dicom_series = dicom_series
		#
		# the series could either be a single dicom instance, or multiple dicom instances
		# if a single dicom instance, it could be either a single slice or a multi-frame dicom
		# if multiple dicom instances, it could be multiple single slice instances
		#
		self.image_instances = self._dicom_series.get_instances_with_image_data()
		if len(self.image_instances) == 0:
			raise Exception('There are no DICOM instances with image data in the series.')
		#
		self._is_multiframe = len(self.image_instances)==1 and hasattr(self.image_instances[0], 'NumberOfFrames')
		if not self._is_multiframe and any(hasattr(x, 'NumberOfFrames') for x in self.image_instances):
			# if there are multiple dicom instances and one or more are multi-frame, we consider the input to be bad
			raise Exception('One of the dicom instances is a multi-frame dicom. If a multi-frame dicom is used, it can be the only dicom in the series.')
		#
		if self._is_multiframe and self.image_instances[0].pixel_array.ndim != 3:
			raise Exception('Multi-frame dicom data must be 3D.')
		#
		if not self._is_multiframe and any(x.pixel_array.ndim != 2 for x in self.image_instances):
			# not multi-frame and one of the pixel_arrays is not 2D
			raise Exception('Non-multi-frame dicom instance data must be 2D.')
		#
		if self._is_multiframe:
			self._num_of_slices = self.image_instances[0].NumberOfFrames
		else:
			self._num_of_slices = len(self.image_instances)
		#
		self.info = {}
		self.description = self._dicom_series.description
		#
		self._validate_volume()
		self._build_volume()
	#
	def __str__(self):
		return "DICOM Volume (Description: \'{}\', Multi-frame: {}, Series UID: {})".format(self.description, self._is_multiframe, self._dicom_series.uid)
	#
	def _validate_volume(self):
		r'''
		Make sure that all of the slices are proper (same size, slice thickness, etc).
		'''
		#
		# make sure all images are the correct size
		# not applicable for a multi-frame dicom
		if not self._is_multiframe and any(x.pixel_array.shape != self.image_instances[0].pixel_array.shape for x in self.image_instances):
			raise Exception('Images are not all the same size.')
		#
		# make sure all images are in the same direction (check row and col vectors)
		if any(np.any(self._get_image_orientation_patient(x) != self._get_image_orientation_patient(0)) for x in range(self._num_of_slices)):
			raise Exception('Images do not have the same direction.')
		#
		# make sure all images have the same slice thickness, pixel spacing, etc
		if any(np.any(self._get_pixel_spacing(x) != self._get_pixel_spacing(0)) for x in range(self._num_of_slices)):
			raise Exception('Images do not have the same pixel spacing.')
		if any(self._get_slice_thickness(x) != self._get_slice_thickness(0) for x in range(self._num_of_slices)):
			raise Exception('Images do not have the same slice thickness.')
		#
		imagePositions = [self._get_image_position_patient(x) for x in range(self._num_of_slices)]
		#
		# make sure no images are at the same position
		for x in range(1, len(imagePositions)):
			if np.linalg.norm(imagePositions[x]-imagePositions[x-1]) < 0.001:
				raise Exception('At least two images have the same position.')
			#
		#
		# make sure images are in order relative to their position
		for x in range(1, len(imagePositions)):
			if any(y > 0.001 for y in (imagePositions[x]-imagePositions[x-1])-(imagePositions[1]-imagePositions[0])):
				# make sure the vectors between positions of adjacent slices are all the same
				raise Exception('Images are not evenly spaced.')
			#
		#
	#
	def _get_denormalized_dicom_image(self, slice):
		r'''
		
		'''
		#
		return np.transpose(self._get_raw_image_slice(slice)*self._get_rescale_slope(slice) + self._get_rescale_intercept(slice))
	#
	def _get_raw_image_slice(self, slice):
		if self._is_multiframe:
			return self.image_instances[0].pixel_array[slice, :, :].astype(np.double)
		else:
			return self.image_instances[slice].pixel_array.astype(np.double)
		#
	#
	def _get_pixel_spacing(self, slice):
		if self._is_multiframe:
			return np.array(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PixelMeasuresSequence[0].PixelSpacing)
		else:
			return np.array(self.image_instances[slice].PixelSpacing)
		#
	#
	def _get_slice_thickness(self, slice):
		if self._is_multiframe:
			return float(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PixelMeasuresSequence[0].SliceThickness)
		else:
			return float(self.image_instances[slice].SliceThickness)
		#
	#
	def _get_image_position_patient(self, slice):
		if self._is_multiframe:
			return np.array(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PlanePositionSequence[0].ImagePositionPatient)
		else:
			return np.array(self.image_instances[slice].ImagePositionPatient)
		#
	#
	def _get_patient_position(self, slice):
		return str(self.image_instances[slice].PatientPosition)
	#
	def _get_image_orientation_patient(self, slice):
		if self._is_multiframe:
			return np.array(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PlaneOrientationSequence[0].ImageOrientationPatient)
		else:
			return np.array(self.image_instances[slice].ImageOrientationPatient)
		#
	#
	def _get_rescale_slope(self, slice):
		if self._is_multiframe:
			return float(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PixelValueTransformationSequence[0].RescaleSlope)
		else:
			return float(self.image_instances[slice].RescaleSlope)
		#
	#
	def _get_rescale_intercept(self, slice):
		if self._is_multiframe:
			return float(self.image_instances[0].PerFrameFunctionalGroupsSequence[slice].PixelValueTransformationSequence[0].RescaleIntercept)
		else:
			return float(self.image_instances[slice].RescaleIntercept)
		#
	#
	def _build_volume(self):
		r'''
		Build the volume data and metadata.
		'''
		#
		image_shape = self._get_denormalized_dicom_image(0).shape
		self.info['pixel_data'] = np.zeros((image_shape[0], image_shape[1], self._num_of_slices))
		for x in range(self._num_of_slices):
			self.info['pixel_data'][:,:,x] = self._get_denormalized_dicom_image(x)
		#
		if self._num_of_slices == 1:
			self.info['pixel_spacing'] = np.array([self._get_pixel_spacing(0)[0], self._get_pixel_spacing(0)[1]])
			# slice_vec doesn't make sense for a 2D dataset
		else:
			self.info['pixel_spacing'] = np.array([self._get_pixel_spacing(0)[0], self._get_pixel_spacing(0)[1], np.linalg.norm(self._get_image_position_patient(1)-self._get_image_position_patient(0))])
			self.info['slice_vec'] = (self._get_image_position_patient(1)-self._get_image_position_patient(0))/self.info['pixel_spacing'][2]
		#
		self.info['pixel_size'] = np.array([self._get_pixel_spacing(0)[0], self._get_pixel_spacing(0)[1], self._get_slice_thickness(0)])
		self.info['position'] = np.array(self._get_image_position_patient(0))
		self.info['patient_orientation'] = self._get_patient_position(0)
		self.info['row_vec'] = self._get_image_orientation_patient(0)[0:3]
		self.info['col_vec'] = self._get_image_orientation_patient(0)[3:6]
	#
	def build_image_to_patient_matrix(self):
		r'''
		Get a matrix to transform a pixel coordinate to a DICOM patient
		coordinate. The pixel coordinate corresponds to the center of that
		pixel/voxel.
		
		The DICOM standard defines the patient coordinate system as:
		
			- x -> increasing to the left hand side of the patient
			- y -> increasing to the posterior side of the patient
			- z -> increasing toward the head of the patient
	
		source: https://public.kitware.com/IGSTKWIKI/index.php/DICOM_data_orientation
		'''
		#
		slice_vec = self.info.get('slice_vec')
		# returns None if it doesn't exist
		#
		return coordinates.build_image_to_patient_matrix(self.info['position'], self.info['pixel_spacing'], self.info['row_vec'], self.info['col_vec'], slice_vec)
	#
	def get_dimensions_in_mm(self):
		r'''
		Get the dimensions in millimeters for each axis of the volume.
		Returns a list of length 3.
		
		For 3 pixels...
		::
		
			+---+   +---+   +---+
			| 1 |   | 2 |   | 3 |
			+---+   +---+   +---+
			
			|-|-------|-------|-|
			 ^    ^       ^    ^
			 |    |       |    |
			 |    |       |    ---- 1/2 pixel_size
			 |    |       --------- 1 pixel_spacing
			 |    ----------------- 1 pixel_spacing
			 ---------------------- 1/2 pixel_size
		'''
		#
		return [self.info['pixel_spacing'][x]*(self.info['pixel_data'].shape[x]-1)+self.info['pixel_size'][x] for x in range(self.info['pixel_data'].ndim)]
	#
	def export_images(self, directory, filename_prefix, axis=2):
		'''
		Save slices of the volume to images. The pixels in the resulting images will be
		square, regardless of the DICOM pixel size. These images should not be expected
		to have perfect pixel-accuracy, and compression may be used.
		'''
		#
		return export.export_stack_to_png(self.info['pixel_data'], axis, directory, filename_prefix)
	#
#
def compare_volume_metadata(volume1, volume2):
	r'''
	This compares the volume metadata (position, pixel_size, etc) and shape of the pixel
	data, but not the actual pixel data. Returns True if equal, otherwise returns False.
	'''
	#
	assert volume1.info['pixel_data'].shape == volume2.info['pixel_data'].shape
	#
	keys = set(list(volume1.info)+list(volume2.info))
	# get union of keys from both dictionaries
	keys.remove('pixel_data')
	# we want to compare everything but the pixel data
	#
	for x in keys:
		if type(volume1.info[x]) is np.ndarray or type(volume2.info[x]) is np.ndarray:
			assert (volume1.info[x]==volume2.info[x]).all()
		else:
			assert volume1.info[x]==volume2.info[x]
		#
	#
	return True
#
