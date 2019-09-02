# -*- coding: utf-8 -*-
"""tfRecord_creator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jSXX2ehnzkkS1jiCsGfIaExaFqNfQDp7

#Importing all python packages
"""

import keras
from keras.datasets import cifar10
import tensorflow as tf
from keras import backend as k
import sys
from google.colab import drive
from google.colab import files

tf.enable_eager_execution()
#drive.mount('/content/drive')

"""#Utility functions"""

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))
  
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

"""#tfrecord file create function"""

def create_tfRecord(dataset, trainFile=None, validFile=None, testFile=None):
  
  if(trainFile != None):
    writerTrain = tf.python_io.TFRecordWriter(trainFile)
    
  if(validFile != None):
    writerValid = tf.python_io.TFRecordWriter(validFile)
  
  if(testFile != None):
    writerTest = tf.python_io.TFRecordWriter(testFile)
    
    
  # For CIFAR10 dataset
  
  if(dataset == 'CIFAR10'): 
    
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        
    if(trainFile != None):
      for i in range(len(x_train)):
          # Create a feature
          feature = {
              'image': _bytes_feature(x_train[i].tostring()),
              'label': _int64_feature(y_train[i])
          }
          # Create an example protocol buffer
          example = tf.train.Example(features=tf.train.Features(feature=feature))

          # Serialize to string and write on the file
          writerTrain.write(example.SerializeToString())
      writerTrain.close()
      sys.stdout.flush()
          
    if(validFile != None):
      writerValid.close()
      sys.stdout.flush()
      
    if(testFile != None):
      for i in range(len(x_test)):
          # Create a feature
          feature = {
              'image': _bytes_feature(x_test[i].tostring()),
              'label': _int64_feature(y_test[i])
          }
          # Create an example protocol buffer
          example = tf.train.Example(features=tf.train.Features(feature=feature))

          # Serialize to string and write on the file
          writerTest.write(example.SerializeToString())
      writerTest.close()
      sys.stdout.flush()          
    
   
  else:
    print('Not supported')

"""#tfrecord file parse function"""

def _parse_image_function(example_proto):
  
  
  # Create a dictionary describing the features.
  image_feature_description = {
        "image": tf.FixedLenFeature([], tf.string),
        "label": tf.FixedLenFeature([], tf.int64)
  }

  # Parse the input tf.Example proto using the dictionary above.
  example = tf.parse_single_example(example_proto, image_feature_description)
  image = tf.decode_raw(example["image"], tf.uint8)
  image = tf.cast(image, tf.float32)
  label = tf.cast(example["label"], tf.int32)
  
  return image, label



def parse_tfRecord(fileName):
  
  raw_image_dataset = tf.data.TFRecordDataset(fileName)
  
  parsed_image_dataset = raw_image_dataset.map(_parse_image_function)
      
  return parsed_image_dataset

"""#Create tfrecord files for CIFAR10 and store in Google drive"""

#create_tfRecord('CIFAR10',trainFile='cifarTfTrain.tfrecords', testFile='cifarTfTest.tfrecords')

#import IPython.display as display
#import matplotlib.pyplot as plt
#import numpy as np
#% matplotlib inline

#dataset = parse_tfRecord('cifarTfTrain.tfrecords')


#for parsed_record in dataset.take(1):
#  plt.rcParams['figure.figsize'] = (1,1)
#  f, ax = plt.subplots(1, 1)
#  ax.set_xticks([])
#  ax.set_yticks([])
#  ax.imshow(parsed_record[0].numpy().reshape(32,32,3).astype('int32'))
#  break

tf.executing_eagerly()