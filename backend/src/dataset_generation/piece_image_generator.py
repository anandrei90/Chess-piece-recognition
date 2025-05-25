import numpy as np
from PIL import Image
import os
import sys

""" 
Script used to generate images showing a chess piece
placed on a chessboard square and/or empty chessboard squares.
"""
# get the dir where the script is
WORKING_DIR = sys.path[0]

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
    

def generate_empty_squares():
    '''
    Function that ...
        
    Parameters
    ----------
    None
   
    Returns
    -------
    None
    '''
    # set dir where empty squares are saved
    empty_squares_dir = os.path.join(WORKING_DIR, "empty_squares")
    if not os.path.isdir(empty_squares_dir):
        os.mkdir(empty_squares_dir)
    # get image paths from boards directory
    boards_dir = os.path.join(WORKING_DIR, "boards")
    board_image_names = os.listdir(boards_dir)
    board_image_paths = [os.path.join(boards_dir, name) for name in board_image_names]

    # save all 64 squares of each board in a separate dir
    for i, board_img in enumerate(board_image_paths):
        with Image.open(board_img) as img:
            list_of_squares = split_board(img)
            # print(list_of_squares[0])
            for j, square in enumerate(list_of_squares):
                dir = os.path.join(empty_squares_dir, f"{i+1}")
                if not os.path.isdir(dir):
                    os.mkdir(dir)
                save_path = os.path.join(dir, f'{j+1}.png')
                square.save(save_path)


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

if __name__ == "__main__":
    generate_empty_squares()