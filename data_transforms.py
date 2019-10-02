# -*- coding: utf-8 -*-
"""data_transforms.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jSXX2ehnzkkS1jiCsGfIaExaFqNfQDp7

#Importing all python packages
"""

import tensorflow as tf
#tf.enable_eager_execution()
import numpy as np

"""#Affine transform"""

def get_pixel_value(img: tf.Tensor, x, y) -> tf.Tensor:
    x_shape = tf.shape(x)
    B = x_shape[0]
    H = x_shape[1]
    W = x_shape[2]

    batch_idx = tf.range(0, B)
    batch_idx = tf.reshape(batch_idx, (B, 1, 1))
    b = tf.tile(batch_idx, (1, H, W))

    indices = tf.stack([b, y, x], 3)
    return tf.gather_nd(img, indices)


def reflect(x, max_x):
    x = tf.abs(x)
    x = max_x - tf.abs(max_x - x)
    return x


def bilinear_sampler(img: tf.Tensor, x, y, do_reflect: bool = False) -> tf.Tensor:
    img_shape = tf.shape(img)
    H = img_shape[1]
    W = img_shape[2]

    max_y = tf.cast(H - 1, tf.int32)
    max_x = tf.cast(W - 1, tf.int32)
    zero = tf.zeros([], dtype=tf.int32)

    # rescale x and y to [0, W-1/H-1]
    x = tf.cast(x, tf.float32)
    y = tf.cast(y, tf.float32)
    x = 0.5 * ((x + 1.0) * tf.cast(max_x - 1, tf.float32))
    y = 0.5 * ((y + 1.0) * tf.cast(max_y - 1, tf.float32))

    # grab 4 nearest corner points for each (x_i, y_i)
    x0 = tf.cast(tf.floor(x), tf.int32)
    x1 = x0 + 1
    y0 = tf.cast(tf.floor(y), tf.int32)
    y1 = y0 + 1

    if do_reflect:
        x0 = reflect(x0, max_x)
        x1 = reflect(x1, max_x)
        y0 = reflect(y0, max_y)
        y1 = reflect(y1, max_y)

    # clip to range [0, H-1/W-1] to not violate img boundaries
    x0 = tf.clip_by_value(x0, zero, max_x)
    x1 = tf.clip_by_value(x1, zero, max_x)
    y0 = tf.clip_by_value(y0, zero, max_y)
    y1 = tf.clip_by_value(y1, zero, max_y)

    # get pixel value at corner coords
    Ia = get_pixel_value(img, x0, y0)/255
    Ib = get_pixel_value(img, x0, y1)/255
    Ic = get_pixel_value(img, x1, y0)/255
    Id = get_pixel_value(img, x1, y1)/255

    # recast as float for delta calculation
    x0 = tf.cast(x0, tf.float32)
    x1 = tf.cast(x1, tf.float32)
    y0 = tf.cast(y0, tf.float32)
    y1 = tf.cast(y1, tf.float32)

    # calculate deltas
    wa = (x1 - x) * (y1 - y)
    wb = (x1 - x) * (y - y0)
    wc = (x - x0) * (y1 - y)
    wd = (x - x0) * (y - y0)

    # add dimension for addition
    wa = tf.expand_dims(wa, axis=3)
    wb = tf.expand_dims(wb, axis=3)
    wc = tf.expand_dims(wc, axis=3)
    wd = tf.expand_dims(wd, axis=3)

    # compute output
    out = tf.add_n([wa * Ia, wb * Ib, wc * Ic, wd * Id])

    return out


def affine_grid_generator(H: int, W: int, tfm_mat) -> tf.Tensor:
    B = tf.shape(tfm_mat)[0]

    x = tf.linspace(-1.0, 1.0, W)
    y = tf.linspace(-1.0, 1.0, H)
    x_t, y_t = tf.meshgrid(x, y)

    x_t_flat = tf.reshape(x_t, [-1])
    y_t_flat = tf.reshape(y_t, [-1])

    # reshape to [x_t, y_t , 1] - (homogeneous form)
    ones = tf.ones_like(x_t_flat)
    sampling_grid = tf.stack([x_t_flat, y_t_flat, ones])

    # repeat grid B times
    sampling_grid = tf.expand_dims(sampling_grid, axis=0)
    sampling_grid = tf.tile(sampling_grid, tf.stack([B, 1, 1]))

    # cast to float32 (required for matmul)
    tfm_mat = tf.cast(tfm_mat, tf.float32)
    sampling_grid = tf.cast(sampling_grid, tf.float32)

    # transform the sampling grid - batch multiply
    batch_grids = tf.matmul(tfm_mat, sampling_grid)
    # batch grid has shape (B, 2, H*W)

    # reshape to (B, H, W, 2)
    batch_grids = tf.reshape(batch_grids, [B, 2, H, W])

    return batch_grids


def affine_transform(X: tf.Tensor, tfm_mat, out_dims=None, do_reflect: bool = False) -> tf.Tensor:
    X_shape = tf.shape(X)
    B = X_shape[0]
    H = X_shape[1]
    W = X_shape[2]
    tfm_mat = tf.reshape(tfm_mat, [B, 2, 3])

    out_H, out_W = out_dims if out_dims else H, W
    batch_grids = affine_grid_generator(out_H, out_W, tfm_mat)

    x_s = batch_grids[:, 0, :, :]
    y_s = batch_grids[:, 1, :, :]

    return bilinear_sampler(X, x_s, y_s, do_reflect)

"""#Rotate"""

def rotate(img, angle):
  
  """
  
  Rotates the image
  Arguments : img    - input image tensor
              angle  - rotation angle in degree
  Return    : rotated image tensor
  
  """
  
  angleRad = (angle* np.pi) / 180
  
  # create affine transform matrix
  # [ cos(theta), -sin(theta), 0 ]
  # [ sin(theta),  cos(theta), 0 ]
  # [ 0         ,  0         , 1 ]
  transMat = tf.convert_to_tensor([[tf.cos(angleRad), -tf.sin(angleRad), 0], [tf.sin(angleRad), tf.cos(angleRad), 0], [0, 0, 1]])  
  transMat = tf.reshape(transMat, [-1])[:6]
  img = tf.expand_dims(img, 0)
    
  # Apply affine transform to rotate the image
  rotImg = affine_transform(img, transMat)
  
  # clip the negative values
  rotImg = tf.clip_by_value(rotImg, 0.0, 1.0)

  rotImg = tf.squeeze(rotImg, [0])
  
  return rotImg

"""#Cutout"""

def cutOut(img, cutOut_ht, cutOut_wd, mode):
  
    """
    
    Replaces a window of worth of data in the input image with either 0/128/mean
    Arguments: img        - inpt image tensor
               cutOut_ht  - cut out window height
               cutOut_wd  - cut out window width
               mode       - 0 : replace by zero
                            1 : replace by 128
                            2 : replace by 0.5
                            3 : replace by mean of the image
    
    """
  
    imgShape = tf.shape(img)
  
    # cutout window random starting coordinates
    y0 = tf.random.uniform([], 0, imgShape[0] + 1 - cutOut_ht, dtype=tf.int32)
    x0 = tf.random.uniform([], 0, imgShape[1] + 1 - cutOut_wd, dtype=tf.int32)
    
    if(0 == mode):
      cutoutVal = 0
    elif(1 == mode):
      cutoutVal = 128
    elif(2 == mode):
      cutoutVal = 0.5
    else:
      val = 0#tf.mean(img)
      cutoutVal = val
    
    replacement = tf.fill([cutOut_ht,cutOut_wd, imgShape[2]],tf.cast(cutoutVal,tf.float32))
    size= tf.shape(replacement) 
        
    begin = [x0, y0, 0]
    padding = tf.stack([begin , imgShape - (begin + size)], axis=1)
    replacement_pad = tf.pad(replacement, padding)
    mask = tf.pad(tf.ones_like(replacement, dtype=tf.bool), padding)
    return tf.where(mask, replacement_pad, img)

"""#Random Flip"""

def randomFlip(img):
  
  flipLR = tf.image.random_flip_left_right(img)
  
  return  tf.image.rot90(flipLR, tf.random.uniform(shape=[], minval=0, maxval=4, dtype=tf.int32))

"""#Random Pad Crop"""

def random_pad_crop(x: tf.Tensor, pad_size: int) -> tf.Tensor:
  
    """
    Randomly pad the image by `pad_size` at each border (top, bottom, left, right). Then, crop the padded image to its
    original size.
    :param x: Input image.
    :param pad_size: Number of pixels to pad at each border. For example, a 32x32 image padded with 4 pixels becomes a
                     40x40 image. Then, the subsequent cropping step crops the image back to 32x32. Padding is done in
                     `reflect` mode.
    :return: Transformed image.
    """
    
    shape = tf.shape(x)
    x = tf.pad(x, [[pad_size, pad_size], [pad_size, pad_size], [0, 0]])
    x = tf.image.random_crop(x, [shape[0], shape[1], 3])
    return x

"""#Resize"""

def resize_img(x: tf.Tensor, shape) -> tf.Tensor:    
    y = tf.image.resize_bilinear(tf.reshape(x,[1,x.shape[0],x.shape[1],x.shape[2]]), shape)
    return tf.reshape(y, [y.shape[1],y.shape[2],y.shape[3]])
