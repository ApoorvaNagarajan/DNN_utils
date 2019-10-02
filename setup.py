from setuptools import setup

setup(name='DNN_utils',
      version='1.0',
      description='My DNN utility',
      url='https://github.com/ApoorvaNagarajan/DNN_utils',
      author='Apoorva Nagarajan',
      author_email='apoorvanagarajan26@gmail.com',
      license='MIT',
      packages=['DNN_utils'],
      install_requires=[
          'keras_applications>=1.0.7,<=1.0.8',
      ],
      zip_safe=False)
