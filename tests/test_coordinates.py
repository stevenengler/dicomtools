import unittest
#
import dicomtools
#
import numpy as np
#
class TestCoordinates(unittest.TestCase):
	def test_img_2_pat_matrix_with_list(self):
		origin_position = [59.4, -180, 130]
		pixel_spacing = [1.1363, 1.2537, 1.2]
		row_vec = [0, 1, 0]
		column_vec = [0, 0, -1]
		slice_vec = [-1, 0, 0]
		#
		result = dicomtools.coordinates.build_image_to_patient_matrix(origin_position, pixel_spacing, row_vec, column_vec, slice_vec)
		#
		correct_result = [[0     , 0      , -1.2, 59.4],
						  [1.1363, 0      , 0   , -180],
						  [0     , -1.2537, 0   , 130 ],
						  [0     , 0      , 0   , 1   ]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_img_2_pat_matrix_with_numpy(self):
		origin_position = np.array([59.4, -180, 130])
		pixel_spacing = np.array([1.1363, 1.2537, 1.2])
		row_vec = np.array([0, 1, 0])
		column_vec = np.array([0, 0, -1])
		slice_vec = np.array([-1, 0, 0])
		#
		result = dicomtools.coordinates.build_image_to_patient_matrix(origin_position, pixel_spacing, row_vec, column_vec, slice_vec)
		#
		correct_result = [[0     , 0      , -1.2, 59.4],
						  [1.1363, 0      , 0   , -180],
						  [0     , -1.2537, 0   , 130 ],
						  [0     , 0      , 0   , 1   ]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_img_2_pat_matrix_without_slice_vec(self):
		origin_position = [59.4, -180, 130]
		pixel_spacing = [1.1363, 1.2537]
		row_vec = [0.298142, -0.745356, 0.596285]
		column_vec = [-3, -3, -2.25]
		slice_vec = None
		#
		result = dicomtools.coordinates.build_image_to_patient_matrix(origin_position, pixel_spacing, row_vec, column_vec, slice_vec)
		#
		correct_result = [[0.338778755 , -3.7611  , 0, 59.4],
						  [-0.846948023, -3.7611  , 0, -180],
						  [0.677558646 , -2.820825, 0, 130 ],
						  [0           , 0        , 0, 1   ]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_transform_vectors_single(self):
		transformation_matrix = [[-0.87637175, -0.82176271, -0.71364783, -0.48570265],
								 [ 0.85512268,  0.35782522, -0.38050434, -0.61564894],
								 [-0.00417963,  0.45428037,  0.33635176, -0.24575262],
								 [-0.14927934, -0.57208487,  0.32149241,  0.52701531]]
		vectors = [4, 2, -3]
		#
		result = dicomtools.coordinates.transform_vectors(transformation_matrix, vectors)
		#
		correct_result = [-3.49377158,  4.66200524, -0.36296568]
		np.testing.assert_allclose(result, correct_result)
	#
	def test_transform_vectors_multiple(self):
		transformation_matrix = [[-0.87637175, -0.82176271, -0.71364783, -0.48570265],
								 [ 0.85512268,  0.35782522, -0.38050434, -0.61564894],
								 [-0.00417963,  0.45428037,  0.33635176, -0.24575262],
								 [-0.14927934, -0.57208487,  0.32149241,  0.52701531]]
		vectors = [[4    , 2     , -3  ],
				   [3.2  , -4.223, 6.33],
				   [-1.23, 0     , 2.6 ],
				   [0    , 0     , 0   ]]
		#
		result = dicomtools.coordinates.transform_vectors(transformation_matrix, vectors)
		#
		correct_result = [[-3.49377158,  4.66200524, -0.36296568],
						  [-4.33717909, -1.79894474, -0.0484468 ],
						  [-1.26324976, -2.65676112,  0.6339029 ],
						  [-0.48570265, -0.61564894, -0.24575262]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_transform_vectors_zero_fill(self):
		transformation_matrix = [[-0.87637175, -0.82176271, -0.71364783, -0.48570265],
								 [ 0.85512268,  0.35782522, -0.38050434, -0.61564894],
								 [-0.00417963,  0.45428037,  0.33635176, -0.24575262],
								 [-0.14927934, -0.57208487,  0.32149241,  0.52701531]]
		#
		vectors = [4, 2]
		result = dicomtools.coordinates.transform_vectors(transformation_matrix, vectors)
		correct_result = [-5.63471507, 3.52049222, 0.6460896]
		np.testing.assert_allclose(result, correct_result)
		#
		vectors = [4, 2, 0]
		result = dicomtools.coordinates.transform_vectors(transformation_matrix, vectors)
		correct_result = [-5.63471507, 3.52049222, 0.6460896]
		np.testing.assert_allclose(result, correct_result)
	#
	def test_expand_transformation_dimension_without_move(self):
		transformation = [[1, 2, 3],
						  [4, 5, 6],
						  [0, 0, 1]]
		new_size = 6
		move_translation = False
		#
		result = dicomtools.coordinates.expand_transformation_dimension(transformation, new_size, move_translation)
		#
		correct_result = [[1, 2, 3, 0, 0, 0],
						  [4, 5, 6, 0, 0, 0],
						  [0, 0, 1, 0, 0, 0],
						  [0, 0, 0, 1, 0, 0],
						  [0, 0, 0, 0, 1, 0],
						  [0, 0, 0, 0, 0, 1]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_expand_transformation_dimension_with_move(self):
		transformation = [[1, 2, 3],
						  [4, 5, 6],
						  [0, 0, 1]]
		new_size = 6
		move_translation = True
		#
		result = dicomtools.coordinates.expand_transformation_dimension(transformation, new_size, move_translation)
		#
		correct_result = [[1, 2, 0, 0, 0, 3],
						  [4, 5, 0, 0, 0, 6],
						  [0, 0, 1, 0, 0, 0],
						  [0, 0, 0, 1, 0, 0],
						  [0, 0, 0, 0, 1, 0],
						  [0, 0, 0, 0, 0, 1]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_build_translation_matrix(self):
		translation = [4, 5, 6]
		#
		result = dicomtools.coordinates.build_translation_matrix(translation)
		#
		correct_result = [[1, 0, 0, 4],
						  [0, 1, 0, 5],
						  [0, 0, 1, 6],
						  [0, 0, 0, 1]]
		#
		np.testing.assert_allclose(result, correct_result)
	#
	def test_build_pat_2_physical_matrix_valid_positions(self):
		patient_positions = ['HFP', 'HFS', 'FFP', 'FFS']
		# ['HFDR', 'HFDL', 'FFDR', 'FFDL'] have not yet been programmed
		#
		correct_results = []
		correct_results.append([[-1,  0,  0,  0],
								[ 0,  1,  0,  0],
								[ 0,  0, -1,  0],
								[ 0,  0,  0,  1]])
		correct_results.append([[ 1,  0,  0,  0],
								[ 0, -1,  0,  0],
								[ 0,  0, -1,  0],
								[ 0,  0,  0,  1]])
		correct_results.append([[ 1,  0,  0,  0],
								[ 0,  1,  0,  0],
								[ 0,  0,  1,  0],
								[ 0,  0,  0,  1]])
		correct_results.append([[-1,  0,  0,  0],
								[ 0, -1,  0,  0],
								[ 0,  0,  1,  0],
								[ 0,  0,  0,  1]])
		#
		for x in range(len(patient_positions)):
			result = dicomtools.coordinates.build_patient_to_physical_matrix(patient_positions[x])
			np.testing.assert_allclose(result, correct_results[x])
		#
		def test_build_pat_2_physical_matrix_invalid_positions(self):
			patient_positions = ['HFDR', 'HFDL', 'FFDR', 'FFDL']
			# these positions have not yet been programmed
			#
			for patient_position in patient_positions:
				self.assertRaises(ValueError, dicomtools.coordinates.build_patient_to_physical_matrix(patient_positions))
			#
		#
	#
#
if __name__ == '__main__':
	unittest.main()
#