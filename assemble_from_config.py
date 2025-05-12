import os
import numpy as np
import skimage.io


def assemble_image(config_filepath, images_dirpath, output_filepath):
    parent, fn = os.path.split(output_filepath)
    if not os.path.exists(parent):
        os.makedirs(parent)

    if not os.path.exists(config_filepath):
        raise RuntimeError('Missing configuration file: {}'.format(config_filepath))

    # load the positions for each image
    img_names = []
    pixel_x_position = []
    pixel_y_position = []
    with open(config_filepath, 'r') as fh:
        for line in fh:
            line = line.strip()
            # Skip header lines
            if line.startswith('#') or line.startswith('dim'):
                continue
            
            # Parse the filename and position
            if ';;' in line:
                parts = line.split(';;')
                if len(parts) == 2:
                    # Get filename
                    filename = parts[0]
                    img_names.append(filename)
                    
                    # Get position
                    pos_part = parts[1].strip('()')
                    pos_x, pos_y = map(float, pos_part.split(','))
                    pixel_x_position.append(int(pos_x))
                    pixel_y_position.append(int(pos_y))

    # verify that all images exist
    if not os.path.exists(images_dirpath):
        raise RuntimeError('Images directory does not exist: {}'.format(images_dirpath))

    for fn in img_names:
        if not os.path.exists(os.path.join(images_dirpath, fn)):
            raise RuntimeError('Image {} expected based on config file, but its missing from the image directory.'.format(fn))

    # compute how large of an output image will be required.
    first_tile = skimage.io.imread(os.path.join(images_dirpath, img_names[0]))
    tile_shape = first_tile.shape
    n_channels = 1
    if len(tile_shape) == 3:
        n_channels = tile_shape[2]
    tile_h = tile_shape[0]
    tile_w = tile_shape[1]

    stitched_img_h = tile_h + np.max(pixel_y_position)
    stitched_img_w = tile_w + np.max(pixel_x_position)

    # creating blank image
    print('Creating blank stitched image of size: ({}, {}, {})'.format(stitched_img_h, stitched_img_w, n_channels))
    stitched_img = np.zeros((stitched_img_h, stitched_img_w, n_channels), dtype=first_tile.dtype)

    for i in range(0, len(img_names)):
        fn = img_names[i]
        x = pixel_x_position[i]
        y = pixel_y_position[i]
        print('Img {}/{}. Placing {} at ({}, {})'.format(i+1, len(img_names), fn, x, y))
        tile = skimage.io.imread(os.path.join(images_dirpath, fn))
        if tile.shape != tile_shape:
            raise RuntimeError('All images must be the same shape. Image {} is {}, expected {}'.format(fn, tile.shape, tile_shape))
        if tile.dtype != first_tile.dtype:
            raise RuntimeError('Img {} has type: {}, expected {}.'.format(fn, tile.dtype, first_tile.dtype))

        # Fix: expand dims if grayscale
        if len(tile.shape) == 2:
            tile = np.expand_dims(tile, axis=2)

        stitched_img[y:y+tile_h, x:x+tile_w, :] = tile

    print('Saving stitched image to disk')
    skimage.io.imsave(output_filepath, stitched_img, plugin=None, check_contrast=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Script to assemble images from TileConfiguration')
    parser.add_argument('--config-filepath', type=str, required=True, help='Filepath to the TileConfiguration file.')
    parser.add_argument('--images-dirpath', type=str, required=True, help='Dirpath (directory) where the source images exists.')
    parser.add_argument('--output-filepath', type=str, required=True, help='Filepath where to save the resulting stitched image.')

    args = parser.parse_args()
    config_filepath = args.config_filepath
    images_dirpath = args.images_dirpath
    output_filepath = args.output_filepath

    assemble_image(config_filepath, images_dirpath, output_filepath) 