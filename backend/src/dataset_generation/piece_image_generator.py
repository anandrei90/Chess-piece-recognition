import numpy as np
from PIL import Image
import os
from glob import glob
import sys

""" 
Script used to generate images showing a chess piece
placed on a chessboard square and/or empty chessboard squares.

NB: bishop from piece set #8 looks strange af
"""
####################### define directory paths as constants #######################

WORKING_DIR = sys.path[0]

# dir tree where empty squares will be saved
EMPTY_SQUARES_PATH = os.path.join(WORKING_DIR, "empty_squares")

# get (sorted) board image paths (i.e. paths to all png's in /boards dir)
BOARD_IMAGE_PATHS = glob(os.path.join(WORKING_DIR, "boards", "*"))
# BOARD_IMAGE_PATHS = sorted(BOARD_IMAGE_PATHS, key=lambda x: os.path.basename(x))

# dir where piece images are stored
PIECES_PATH = os.path.join(WORKING_DIR, "pieces")

# piece names (they are the same regardless of folder)
PIECE_NAMES = [name[:-4] for name in os.listdir(os.path.join(PIECES_PATH, "1"))]
# add empty square class to list
PIECE_NAMES.insert(0,'e')

# create data directory structure
DATA_PATHS = [os.path.join(WORKING_DIR, os.pardir, "data", name) for name in PIECE_NAMES]


####################### instantiate random number generator #######################

# create a random number generator object
# for reproducibilty purposes
rng = np.random.default_rng(seed=35)

####################### split board in 64 squares #######################

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
    reshaped = reshaped.swapaxes(1,2) # => (8,8,50,50,4)
    reshaped = reshaped.reshape(64,50,50,4)
    # convert to list of images
    list_of_squares = [Image.fromarray(reshaped[i,:,:,:]) for i in range(reshaped.shape[0])]
    
    return list_of_squares
    
####################### generate and save empty square images #######################

def generate_empty_squares():
    '''
    Function that splits each empty chess board image into its
    64 squares and saves the empty squares in a separate directory
    for each chess board style. Example: for chess board style no. 14,
    the empty square images will be saved in the directory
    ./dataset_generation/empty_squares/14, under the names 1.png,
    2.png, ..., 64.png.

    Parameters
    ----------
    None
   
    Returns
    -------
    None
    '''


    
    # save all 64 squares of each board in a separate dir per board
    for i, board_img in enumerate(BOARD_IMAGE_PATHS):
        
        # create a directory for each board style
        board_style_path = os.path.join(EMPTY_SQUARES_PATH, f"{i+1}")
        if not os.path.isdir(board_style_path):
            os.makedirs(board_style_path)
        
        # open board image, decompose it in squares
        with Image.open(board_img) as img:
            list_of_squares = split_board(img)
        
        # save each chess square image from a given board 
        # in the created dir
        for j, square in enumerate(list_of_squares):
            save_path = os.path.join(board_style_path, f'{j+1}.png')
            square.save(save_path)

####################### create folder structure for data #######################

def create_data_folder_structure():
    '''
    Function that generates the structure of the folder where
    the data is stored.

    Parameters
    ----------
    None
        
    Returns
    -------
    None
    ''' 

    for path in DATA_PATHS:
        if not os.path.isdir(path):
            os.makedirs(path)

####################### generate and save dataset images #######################

def generate_dataset(n_data_points, mode):
    '''
    Function that creates a chess piece/square dataset at
    src/data. The probabilities of generating a certain piece
    or an empty square are equal, i.e. P(empty square)=
    P(black_pawn) = P(white_queen) = P(white_pawn) = ... = 1/13.

    Parameters
    ----------
    n_data_points: positive int
        Number of images to be generated.
    mode: {“train”, “test”, “all”}
        Specifies which piece styles will be used in data generation.
        
    Returns
    -------
    None
    '''   
  
    # select range for random number generator such that
    # a specific subset of piece styles can be chosen
    if mode == 'train':
        range_slice = slice(0,16) # first 16 piece sets
    elif mode == 'test':
        range_slice = slice(16,32) # last 16 piece sets
    elif mode == 'all':
        range_slice = slice(0,32) # all 32 piece sets
    else:
        raise ValueError(f"{mode} is not a valid option for the mode parameter. \
                         Use train, test, or all instead.")

    # store all empty square paths in a list
    all_empty_squares = glob(os.path.join(EMPTY_SQUARES_PATH, "*", "*"))
    # store paths to every piece set in a list
    piece_sets = glob(os.path.join(PIECES_PATH, "*"))
    # select subset of piece sets according to selected mode
    piece_sets = sorted(piece_sets)[range_slice] # sorted for reproducibility

    # generate pieces superimposed on squares
    for i in range(int(n_data_points)):

        # randomly pick a piece or an empty square
        piece_path = rng.choice(DATA_PATHS)

        # path where image is going to be saved
        save_path = os.path.join(piece_path, f"{i}.png")

        # select random empty square
        empty_square = rng.choice(all_empty_squares)
        
        # create the empty square / piece image
        with Image.open(empty_square).convert('RGBA') as img:
            if piece_path[-1] == 'e':
                pass
            else:
                # randomly select a piece set
                piece_set = rng.choice(piece_sets)
                # last 3 chars of piece path are the piece name, e.g. r_w
                piece_name = piece_path[-3:]
                # open piece image
                piece_image_path = os.path.join(piece_set, piece_name + ".png")
                with Image.open(piece_image_path).convert('RGBA') as piece:
                    # paste piece on top of empty square
                    img.paste(piece, mask=piece)
                
            # save resulting image
            img.save(save_path)
     
####################### pack all functions together #######################
def main():
    generate_empty_squares()
    create_data_folder_structure()
    generate_dataset(n_data_points = 10000, mode = 'train')

if __name__ == "__main__":
    # 10000 images => 53.9 MB, ~5.8 sec
    main()
