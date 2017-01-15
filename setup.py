from setuptools import setup, find_packages
from os import path
#
here = path.abspath(path.dirname(__file__))
#
# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()
#
setup(
    name='dicomtools',
    version='0.0.1',
    description='Tools for researchers working with DICOM data in Python',
    long_description=long_description,
    url='https://github.com/stevenengler/dicomtools/',
    author='Steven Engler',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
		'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='dicom imaging',
    packages=find_packages(),
    install_requires=['pydicom', 'numpy', 'matplotlib'],
)
