import numpy as np
import dicom
import os
import warnings
#
class DicomSeries(object):
	r'''
	A class for storing and processing DICOM series. Instances are verified to all have
	consistent ``SeriesInstanceUID`` attributes.
	'''
	#
	def __init__(self, dicom_list):
		r'''
		
		'''
		#
		if len(dicom_list) == 0:
			raise Exception('No DICOM instances were given for the series.')
		#
		if not self._uids_equal(dicom_list):
			raise Exception('Each \'SeriesInstanceUID\' does not match, so images do not belong to the same series.')
		#
		self.instances = self._sort_dicom_instances(dicom_list)
		self.uid = self.instances[0].SeriesInstanceUID
		if hasattr(self.instances[0], 'SeriesDescription'):
			self.description = self.instances[0].SeriesDescription
		else:
			self.description = None
		#
	#
	def __str__(self):
		return "DICOM Series (Description: {}, Series UID: {})".format(self.description, self.uid)
	#
	def _uids_equal(self, dicom_list):
		r'''
		Returns True if all the dicom instances have the same Series UID, otherwise
		returns False.
		'''
		#
		uid = dicom_list[0].SeriesInstanceUID
		return all(x.SeriesInstanceUID==uid for x in dicom_list)
	#
	def _sort_dicom_instances(self, dicom_list):
		r'''
		Not all instances will have instance numbers, so put the instances without
		instance numbers at the start, and the ordered instances with instance numbers
		at the end. Sorting is **not** done in-place.
		'''
		#
		with_instance_numbers = [x for x in dicom_list if hasattr(x, 'InstanceNumber')]
		without_instance_numbers = [x for x in dicom_list if x not in with_instance_numbers]
		#
		return without_instance_numbers + sorted(with_instance_numbers, key=lambda x: x.InstanceNumber)
		# concat lists
	#
	def _instance_has_image_data(self, dicom_instance):
		r'''
		Returns True if the dicom instance seems to have image data, otherwise returns
		False.
		'''
		#
		return hasattr(dicom_instance, 'pixel_array')
	#
	def get_instances_with_image_data(self):
		r'''
		Get all of the DICOM instances in the series which contain image data (has the
		``pixel_array`` property).
		'''
		#
		return [x for x in self.instances if self._instance_has_image_data(x)]
	#
	def get_instances_without_image_data(self):
		r'''
		Get all of the DICOM instances in the series which do not contain image data
		(do not have the ``pixel_array`` property).
		'''
		#
		return [x for x in self.instances if not self._instance_has_image_data(x)]
	#
#
