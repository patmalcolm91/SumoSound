from distutils.core import setup
setup(
  name='SumoSound',
  packages=['SumoSound'],
  version='1.0.0',
  license='MIT',
  description='A python library to add 3D sound to a Sumo traffic simulation.',
  author='Patrick Malcolm',
  author_email='patmalcolm91@gmail.com',
  url='https://github.com/patmalcolm91/SumoSound',
  download_url='https://github.com/patmalcolm91/SumoSound/archive/v_1.0.0.tar.gz',
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
