import numpy as np
from PIL import Image
import os
import sys
import time

""" 
Script used to generate images showing a chess piece
placed on a chessboard square and/or empty chessboard squares.

NB: bishop from piece set #8 looks strange af
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
    Function that splits each empty chess board image into its
    64 squares and saves the empty squares in a separate directory
    per chess board style. Example: for chess board style no. 14,
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

    # create dir where empty squares are saved
    empty_squares_path = os.path.join(WORKING_DIR, "empty_squares")
    if not os.path.isdir(empty_squares_path):
        os.mkdir(empty_squares_path)
    
    # get image paths from boards directory
    boards_path = os.path.join(WORKING_DIR, "boards")
    board_image_paths = [os.path.join(boards_path, name) for name in os.listdir(boards_path)]
    
    # sort board image paths
    board_image_paths = sorted(board_image_paths, key=lambda x: os.path.basename(x))
    
    # save all 64 squares of each board in a separate dir per board
    for i, board_img in enumerate(board_image_paths):
        
        # create a directory for each board style
        board_style_path = os.path.join(empty_squares_path, f"{i+1}")
        if not os.path.isdir(board_style_path):
            os.mkdir(board_style_path)
        
        # open board image, decompose it in squares
        with Image.open(board_img) as img:
            list_of_squares = split_board(img)
        
        # save each chess square image from a given board 
        # in the created dir
        for j, square in enumerate(list_of_squares):
            save_path = os.path.join(dir, f'{j+1}.png')
            square.save(save_path)


def generate_dataset(n_data_points, mode):
    '''
    Function that creates a chess piece/square dataset at
    src/data. The probabilities of generating a certain piece
    or an empty square are equal, i.e. P(empty square)=
    P(black_pawn) = P(white_queen) = P(white_pawn) = ... = 1/13.

    Parameters
    ----------
    mode: {“train”, “test”, “mixed”}
        Specifies which piece styles will be used in data generation.
        
    Returns
    -------
    None
    '''   
    
    # specify piece and empty square dir
    pieces_path = os.path.join(WORKING_DIR, "pieces")
    empty_squares_path = os.path.join(WORKING_DIR, "empty_squares")

    # piece names (they are the same regardless of folder, 
    # so just choose first folder)
    piece_names = os.listdir(os.path.join(pieces_path, "1"))
    # remove .png from the end
    piece_names = [name[:-4] for name in piece_names]

    # create data directory structure
    dir_up = os.path.dirname(WORKING_DIR) # go up one level
    # data directories for pieces
    data_paths_pieces = [os.path.join(dir_up, "data", name) for name in piece_names]
    for path in data_paths_pieces:
        if not os.path.isdir(path):
            os.makedirs(path)
    # data directories for empty squares
    data_path_empty_squares = os.path.join(dir_up, "data", "e")
    if not os.path.isdir(data_path_empty_squares):
            os.makedirs(data_path_empty_squares)
      
    # select range for random number generator such that
    # a specific subset of piece styles can be chosen
    if mode == 'train':
        range_tuple = (1,17) # first 16 board sets
    elif mode == 'test':
        range_tuple = (17,33) # last 16 board sets
    elif mode == 'mixed':
        range_tuple = (1,33) # all 32 board sets
    else:
        raise ValueError(f"{mode} is not a valid option for the mode parameter. \
                         Use train, test, or mixed instead.")

    # generate pieces superimposed on squares
    for i in range(int(n_data_points)):
        
        # generate random integers to select piece & board style
        piece_set_id = str(rng.integers(*range_tuple))
        board_id = str(rng.integers(1,29)) # 28 board sets
        
        # open square image
        square_id = str(rng.integers(1,65)) # 64 sqaures/board
        square_path = os.path.join(empty_squares_path, board_id, f'{square_id}.png')
        square_img = Image.open(square_path).convert('RGBA')

        # create piece + square or empty square image
        # use prob(empty_square) = prob(a_given_piece) = 1/13
        decider = 13 * rng.uniform()
        if decider > 1:
            # open piece image
            # select randomly a piece (12 piece types)
            piece_id = rng.integers(len(piece_names))
            piece_name = piece_names[piece_id]
            piece_path = os.path.join(pieces_path, piece_set_id, piece_name + '.png')
            piece_img = Image.open(piece_path).convert('RGBA')
            # specify path where image should be saved
            save_path = data_paths_pieces[piece_id]
            save_path = os.path.join(save_path, f'{i}.png')
            # paste piece on top of empty square
            square_img.paste(piece_img, mask=piece_img)
        else:
            # empty square saved in data/e
            save_path = os.path.join(data_path_empty_squares, f'{i}.png')

        square_img.save(save_path)


    # example code to superimpose piece on square
    #image = Image.open(square_path).convert('RGBA')
    #piece_img = Image.open(piece_path).convert('RGBA')
    #
    #image.save(save_path)



if __name__ == "__main__":
    # generate_empty_squares()

    # 10000 images => 53.9 MB
    start = time.time()
    generate_dataset(n_data_points = 10000, mode = 'train')
    print(time.time() - start) 
    # 0.8 - 0.9 sec for 1000 images
    # ~5.8 sec for 10000 images