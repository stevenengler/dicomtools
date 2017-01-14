import numpy as np
import dicom
import os
import warnings
#
from .series import DicomSeries
#
def get_all_series_from_dicomdir(dicomdir_file):
	r'''
	For a given 'DICOMDIR' file, loop through all of the linked patients and
	studies, and return a list of all the series.
	'''
	#
	base_dir = os.path.dirname(dicomdir_file)
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		# this is needed since read_dicomdir() throws a DeprecationWarning
		# this is already fixed in github, and should no longer be needed in the next version
		# DeprecationWarning: 'OffsetoftheNextDirectoryRecord' as tag name has been deprecated; use official DICOM keyword 'OffsetOfTheNextDirectoryRecord'
		# https://github.com/darcymason/pydicom/pull/246
		dicomdir = dicom.read_dicomdir(dicomdir_file)
	#
	series_list = []
	# each element is a list of dicom files within a series, and not all dicom files will be images
	#
	# Patient -> Study -> Series -> Images
	#
	for patient_record in dicomdir.patient_records:
		# loop through patient records
		for study in patient_record.children:
			# loop through studies
			for series in study.children:
				# loop through series
				#
				image_filenames = [os.path.join(base_dir, *image_rec.ReferencedFileID) for image_rec in series.children]
				series_list.append(image_filenames)
			#
		#
	#
	return series_list
#
def read_dicomdir(dicomdir_file):
	r'''
	Build a list of DicomSeries objects, one for each series in the 'DICOMDIR' file.
	'''
	#
	series_list = get_all_series_from_dicomdir(dicomdir_file)
	# this is a list of series, each series containing the paths to dicom files within that series
	loaded_series_list = [[dicom.read_file(x) for x in y] for y in series_list]
	# this is a list of series, each series containing the loaded dicom files within that series
	#
	return [DicomSeries(x) for x in loaded_series_list]
#
def read_dicom(dicom_file):
	r'''
	Build a DicomSeries object containing the DICOM.
	'''
	#
	return DicomSeries([dicom.read_file(dicom_file)])
#
def read_dicom_series(dicom_file_list):
	r'''
	Build a DicomSeries object containing all of the given DICOMs in a series.
	'''
	#
	loaded_series = [dicom.read_file(x) for x in dicom_file_list]
	# this is a series containing the loaded dicom files within that series
	#
	return DicomSeries(loaded_series)
#
