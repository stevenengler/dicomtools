import numpy as np
#
def build_image_to_patient_matrix(origin_position, pixel_spacing, row_vec, column_vec, slice_vec=None):
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
	if len(pixel_spacing) != 2 and len(pixel_spacing) != 3:
		raise ValueError('The pixel_spacing argument must have a length of 2 or 3.')
	#
	if slice_vec is None and len(pixel_spacing) == 3:
		raise ValueError('The pixel_spacing has a length of 3, but the slice_vec was not specified.')
	if slice_vec is not None and len(pixel_spacing) == 2:
		raise ValueError('The pixel_spacing has a length of 2, but the slice_vec was specified.')
	#
	is3D = (len(pixel_spacing) == 3)
	# is3D should be a boolean meaning the data is for a 3D volume, where the negation means it is for a 2D image
	#
	col1 = np.copy(row_vec)
	col1 = col1*pixel_spacing[0]
	col1 = np.append(col1, 0)
	#
	col2 = np.copy(column_vec)
	col2 = col2*pixel_spacing[1]
	col2 = np.append(col2, 0)
	#
	if is3D:
		col3 = np.copy(slice_vec)
		col3 = col3*pixel_spacing[2]
		col3 = np.append(col3, 0)
	else:
		col3 = np.zeros(4)
	#
	col4 = np.copy(origin_position)
	col4 = np.append(col4, 1)
	#
	transform_image_position_to_patient_position = np.transpose(np.array([col1, col2, col3, col4]))
	#
	# this matrix should be applied to the LHS of the position
	return transform_image_position_to_patient_position
#
def build_patient_to_physical_matrix(patient_position):
	r'''
	This function builds a rotation matrix to transform a position in patient
	coordinates to a position in physical coordinates. This physical coordinate
	space is arbitrary, but it simply undoes the effect of the patient position.
	The transformation matrix is the identity matrix for a patient in feet-first
	prone position. This is useful if you have a robot within the imaging device,
	and want a consistent coordinate system regardless of the patient position.
	For example, the up direction will always remain the same for both prone and
	supine positions. Due to the unknown orientation of the imaging device, we
	cannot assign direction labels to these physical axes, so you must test it
	yourself.
	
	Possible patient positions are:
	
		- HFP = head first-prone
		- HFS = head first-supine
		- HFDR = head first-decibitus right
		- HFDL = head first-decubiturs left
		- FFP = feet first-prone
		- FFS = feet first-supine
		- FFDR = feet first-decibitus right
		- FFDL = feet first-decibitus left
	
	source: https://public.kitware.com/IGSTKWIKI/index.php/DICOM_data_orientation
	'''
	#
	if len(patient_position) == 4:
		# I'm sorry, but I don't feel like thinking about this condition (patient on their side)
		raise ValueError('Code cannot handle lateral decubitus positions.')
	#
	if patient_position not in ['HFP', 'HFS', 'FFP', 'FFS']:
		raise ValueError('Unknown patient position: ' + str(patient_position))
	#
	if patient_position[0] == 'H':
		# head-first
		z_factor = -1
	elif patient_position[0] == 'F':
		# feet-first
		z_factor = 1
	#
	if patient_position[2] == 'P':
		# prone
		y_factor = 1
	elif patient_position[2] == 'S':
		# supine
		y_factor = -1
	#
	if patient_position == 'HFP' or patient_position == 'FFS':
		# head-first and prone, or feet-first and supine
		x_factor = -1
	elif patient_position == 'HFS' or patient_position == 'FFP':
		# head-first and supine, or feet-first and prone
		x_factor = 1
	#
	transformation = np.array([
			[x_factor, 0, 0, 0],
			[0, y_factor, 0, 0],
			[0, 0, z_factor, 0],
			[0, 0, 0, 1]
		])
	#
	# this matrix should be applied to the LHS of the position
	return transformation
#
def build_translation_matrix(translation):
	r'''
	For a given translation vector, this function builds the corresponding transformation matrix.
	
	Example:
	::
	
		>>> build_translation_matrix([4,5,6])
		array([[1 0 0 4]
		       [0 1 0 5]
		       [0 0 1 6]
		       [0 0 0 1]])
	'''
	#
	transformation = np.eye(len(translation)+1)
	transformation[0:len(translation), transformation.shape[1]-1] = translation
	# fill in the last column with the translation
	#
	# this matrix should be applied to the LHS of the position
	return transformation
#
def expand_transformation_dimension(transformation, new_size, move_translation):
	r'''
	This function takes an :math:`n \times n` transformation matrix and expands it to a :math:`new\_size \times new\_size` matrix.
	It expands the array, fills in ones along the diagonal, and moves the translation values to the
	new right column if requested.
	
	Example:
	::
	
		>>> test = np.array([[1,2,3],[4,5,6],[0,0,1]])
		>>> test
		array([[1 2 3]
		       [4 5 6]
		       [0 0 1]])
		
		>>> expand_transformation_dimension(test, 6, True)
		array([[1 2 0 0 0 3]
		       [4 5 0 0 0 6]
		       [0 0 1 0 0 0]
		       [0 0 0 1 0 0]
		       [0 0 0 0 1 0]
		       [0 0 0 0 0 1]])
	'''
	#
	if transformation.shape[0] != transformation.shape[1]:
		raise Exception('Transformation must be an nxn array.')
	if transformation.shape[0] > new_size:
		raise Exception('Transformation size cannot be greater than the new size.')
	#
	expand_size = new_size-transformation.shape[0]
	#
	if expand_size > 0:
		new_transformation = np.pad(transformation, ((0,expand_size),(0,expand_size)), mode='constant')
		# make it into a new_size x new_size matrix
		#
		for x in xrange(expand_size):
			# fill in ones along the diagonal
			new_transformation[-(x+1),-(x+1)] = 1
		#
		if move_translation:
			translation = np.copy(new_transformation[0:transformation.shape[0]-1, transformation.shape[1]-1])
			new_transformation[0:transformation.shape[0]-1, transformation.shape[1]-1] = 0
			new_transformation[0:transformation.shape[0]-1, new_transformation.shape[1]-1] = translation
		#
	#
	return new_transformation
#
def transform_vectors(transformation_matrix, vectors):
	r'''
	This function applies (LHS) the :math:`n \times n` transformation matrix to a list of vectors
	and returns a list of the transformed vectors.
	
	The vectors can be any length less than n. The vectors will be zero-filled so that
	they have length :math:`n-1`. If the input is one-dimensional, it is assumed that a
	single vector was given and a one-dimensional vector will be returned.
	'''
	#
	vectors = np.array(vectors)
	input1D = False
	if vectors.ndim == 1:
		# given a single vector rather than a list
		vectors = vectors[np.newaxis, :]
		input1D = True
	#
	vector_length = transformation_matrix.shape[1]-1
	#
	if vectors.shape[1] < vector_length:
		to_add = np.zeros((vectors.shape[0], vector_length-vectors.shape[1]))
		vectors = np.concatenate((vectors,to_add), axis=1)
	elif vectors.shape[1] > vector_length:
		raise ValueError('Cannot transform a position in a dimension higher than '+str(vector_length)+'.')
	#
	to_add = np.zeros((vectors.shape[0], 1))+1
	vectors = np.concatenate((vectors,to_add), axis=1)
	vectors = np.transpose(vectors)
	#
	ans = np.transpose(np.array(np.dot(transformation_matrix, vectors)[0:vector_length]))
	if input1D:
		return ans[0]
	return ans
#
