#!/usr/bin/python

# Copyright (c) 2015 Matthew Earl
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
# 
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
#     NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#     DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#     OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#     USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This is the code behind the Switching Eds blog post:

    http://matthewearl.github.io/2015/07/28/switching-eds-with-python/

See the above for an explanation of the code below.

To run the script you'll need to install dlib (http://dlib.net) including its
Python bindings, and OpenCV. You'll also need to obtain the trained model from
sourceforge:

    http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2

Unzip with `bunzip2` and change `PREDICTOR_PATH` to refer to this file. The
script is run like so:

    ./faceswap.py <head image> <face image>

If successful, a file `output.jpg` will be produced with the facial features
from `<head image>` replaced with the facial features from `<face image>`.

"""

import cv2
import dlib
import numpy as np
from scipy.misc import imresize 

import glob
import os
import sys
import faceswap
import facealign

if __name__ == "__main__":
    avg_landmarks = np.load("mean_landmark_x4.npy")
    im, landmarks = facealign.read_im_and_landmarks("celeba/000001.jpg")
    coerced_landmarks = 0 * landmarks + avg_landmarks

    source_dir = "inputs"
    dest_dir = "outputs"

    files = glob.glob("{}/*.*".format(source_dir))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in files:
        try:
            im, landmarks = facealign.read_im_and_landmarks(filename)
            outfile = "{}/{}".format(dest_dir, os.path.basename(filename))
            outfile = "{}.png".format(os.path.splitext(outfile)[0])
            M = faceswap.transformation_from_points(coerced_landmarks[faceswap.ALIGN_POINTS],
                                           landmarks[faceswap.ALIGN_POINTS])
            warped_im2 = faceswap.warp_im(im, M, (256,256,3))
            resize64 = imresize(warped_im2, (128,128), interp="bicubic", mode="RGB")
            cv2.imwrite(outfile, resize64)
        except faceswap.NoFaces:
            pass
        except faceswap.TooManyFaces:
            print("too many faces in {}".format(filename))
        # except:
        #     print "Unexpected error:", sys.exc_info()[0]
