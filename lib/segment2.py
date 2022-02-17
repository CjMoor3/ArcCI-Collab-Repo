# title: Watershed Transform
# Revised and by: Xin Miao Oct. 2019


import numpy as np
import gc
import warnings
import skimage
from skimage import filters, morphology, feature, img_as_ubyte, segmentation, data, color
from skimage.filters import rank
from skimage.morphology import disk
from scipy import ndimage
from ctypes import *
from lib import utils
from scipy import ndimage as ndi
from skimage.future import graph

from skimage import data, io, segmentation, color

from skimage.exposure import rescale_intensity
#from skimage.util import img_as_ubyte

#import matplotlib.pyplot as plt


# For Testing:
##from skimage import segmentation
import matplotlib.image as mimg

#--------Region Adjacency Graphs (RAGs) Merging process ---------------

def _weight_mean_color(graph, src, dst, n):
    """Callback to handle merging nodes by recomputing mean color.

    The method expects that the mean color of `dst` is already computed.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    n : int
        A neighbor of `src` or `dst` or both.

    Returns
    -------
    data : dict
        A dictionary with the `"weight"` attribute set as the absolute
        difference of the mean color between node `dst` and `n`.
    """

    diff = graph.nodes[dst]['mean color'] - graph.nodes[n]['mean color']
    diff = np.linalg.norm(diff)
    return {'weight': diff}


def merge_mean_color(graph, src, dst):
    """Callback called before merging two nodes of a mean color distance graph.

    This method computes the mean color of `dst`.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    """
    graph.nodes[dst]['total color'] += graph.nodes[src]['total color']
    graph.nodes[dst]['pixel count'] += graph.nodes[src]['pixel count']
    graph.nodes[dst]['mean color'] = (graph.nodes[dst]['total color'] /
                                      graph.nodes[dst]['pixel count'])
def segment_image2(input_data, smooth, gradient_cut, merging_cut, image_type=False):
 
    #### Define segmentation parameters

    if image_type == 'pan' or image_type == 'wv02_ms':
#        high_threshold = 0.15 * 255   ## Needs to be checked
#        low_threshold = 0.05 * 255     ## Needs to be checked
#        gauss_sigma = 1
#        feature_separation = 1

        band_list = [0, 0, 0]
        
#        high_threshold = 200   ## Needs to be checked
#        low_threshold = 20
        
#        band_list = [0]
        

    else:   #image_type == 'srgb'
        band_list = [0, 1, 2]
        
    
    # print(image_type) 
    # print(input_data.shape)
    # print(img.shape)
        
    segmented_data = watershed_transformation(input_data, band_list, smooth, gradient_cut)
    #segmented_data = watershed_transformation(input_data, band_list, smooth, gradient_cut)

#    img = np.stack((WV3,)*3, axis=-1) #axis=-1 new dimension will be the last dimension
    

    # if np.amax(segmented_data) >= 1:

    #     g = graph.rag_mean_color(img, segmented_data)
    #     segmented_merge_data = graph.merge_hierarchical(segmented_data, g, thresh=merging_cut, rag_copy=False,
    #                                in_place_merge=True,
    #                                merge_func=merge_mean_color,
    #                                weight_func=_weight_mean_color)
    
    #     return segmented_merge_data
    
    return segmented_data

#    return segmented_data, gradient, markers_nolabel
    

def watershed_transformation(image_data, band_list, smooth, gradient_cut):
    '''
    Runs a watershed transform on the main dataset (Revised by Xin Miao 1/7/2019)
        1. Create an edge-detection layer using the sobel algorithm
        2. Find the local minimum based on distance transform and place a marker
        3. Adjust the gradient image based on given threshold and amplification.
        4. Construct watersheds on top of the gradient image starting at the
            markers.
    '''

    # If this block has no data, return a placeholder watershed.
    if np.amax(image_data[0]) <= 1:
        # We just need the dimensions from one band
        blankimg = np.zeros(np.shape(image_data)[0:2])
        return blankimg  # Handel blank image

    genDisk = disk(smooth)
    denoised = rank.median(image_data[:, :, 0], genDisk)   # Modified 12/4/2020

    # find continuous region (low gradient -
    # where less than 10 for this image) --> markers    
    # disk(5) is used here to get a more smooth image
#    markers = rank.gradient(denoised, disk(5)) < 12
 
    # a=image_data  
    # print(type(a), a.dtype, a.shape)
    # print(a)

    # a=denoised      
    # print(type(a), a.dtype, a.shape)
   
    gradient = rank.gradient(denoised, genDisk)
    
    
    
    # a=gradient
    # print(type(a), a.dtype, a.shape)
    

    markers = gradient < gradient_cut
    # markers_nolabel = markers
   
#    markers = rank.gradient(denoised, disk(5)) < 15
    markers = ndi.label(markers)[0]  # Label each marker 1,2,3...
    
    # a=markers_nolabel
    # print(type(a), a.dtype, a.shape)
    
    # local gradient (disk(2) is used to keep edges thin)
    
    
    
#    plt.figure(figsize = (100,100))
#    plt.imshow(gradient)
#plt.imshow(WV3_edge)

#    plt.axis('off') # 关掉坐标轴为 off
#    plt.savefig("WV3_gradient")
#    plt.imsave('WV3_gradient.png', gradient, cmap="gray")
#plt.show()
#    plt.close()
    
    
    

    # process the watershed on gradient layer
    im_watersheds = skimage.segmentation.watershed(gradient, markers) 

    gc.collect()
    #return im_watersheds
    
    



    
    return im_watersheds
#    return im_watersheds

