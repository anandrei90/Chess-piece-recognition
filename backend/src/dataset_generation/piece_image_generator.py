import numpy as np
from PIL import Image
import os 

""" 
Script used to generate images showing a chess piece
placed on a chessboard square and/or empty chessboard squares.
"""
# create a random number generator object
# for reproducibilty purposes

rng = np.random.default_rng(seed=35)

def split_board(board_img):
    '''
    Function that splits a 400x400 pixel chess board
    image into 64 individual 50*50 pixel squares. 
        
    Parameters
    ----------
    
    board_img: pillow image
        400 x 400 pixel chess board images.
    
    Returns
    -------
    List of 64 50*50 pixel RGBA chessboard square images.
    '''
    
    # convert to RGBA
    board_img = board_img.convert('RGBA')
    # convert image to array with shape = (400,400,4)  
    image_arr = np.asarray(board_img)
    # check if array has the right size
    if image_arr.shape != (400,400,4):
        raise ValueError("Image does not have the correct shape (400x400 pixels, RGBA).")
    # reshape array to (64,50,50,4)
    reshaped = image_arr.reshape(8,50,8,50,4)
    reshaped = reshaped.swapaxes(1,2)
    reshaped = reshaped.reshape(64,50,50,4)
    # convert to list of images
    list_of_squares = [Image.fromarray(reshaped[i,:,:,:]) for i in range(reshaped.shape[0])]
    
    return list_of_squares
    


def save_empty_squares(img_list, save_path):
    '''
    Function that saves several images at a given
    path. 
        
    Parameters
    ----------
    
    img_list: list of pillow images
        List of 50*50 pixel chessboard square images.
    save_path: string
        Path where images are saved.
    '''
    pass



def overlay_images(front_img, back_img):
    '''
    Function overlaying two 50x50 pixel images. 
        
    Parameters
    ----------
    
    front_img: pillow image
        Foreground image (chess piece in our case).
    back_img: pillow image
        Background image (chess square in our case).
        
    Returns
    -------
    50x50 pixel image consisting of a chess piece overlayed
    on a chess board square.
    '''   
    
    pass

