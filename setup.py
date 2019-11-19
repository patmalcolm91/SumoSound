from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='SumoSound',
  packages=['SumoSound'],
  version='1.0.2',
  license='MIT',
  description='A python library to add 3D sound to a Sumo traffic simulation.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Patrick Malcolm',
  author_email='patmalcolm91@gmail.com',
  url='https://github.com/patmalcolm91/SumoSound',
  download_url='https://github.com/patmalcolm91/SumoSound/archive/v_1.0.2.tar.gz',
  keywords=['sumo', 'TraCI', 'sound', 'sound effects', '3D sound', 'OpenAL', 'traffic'],
  install_requires=[
          'pyopenal',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ],
  package_data={'SumoSound': ['stock_sounds/*.wav']}
)
