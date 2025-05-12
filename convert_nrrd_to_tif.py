import os
import SimpleITK as sitk
import argparse
import shutil
import numpy as np

def convert_nrrd_to_tif(input_dir, output_dir, file_prefix='img'):
    """
    Convert NRRD files to TIFF format and organize them in a grid pattern
    for MIST processing.
    
    Args:
        input_dir: Directory containing NRRD files
        output_dir: Directory where TIF files will be saved
        file_prefix: Prefix for output filenames
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all NRRD files
    nrrd_files = [f for f in os.listdir(input_dir) if f.endswith('.nrrd') and f.startswith('tile_')]
    nrrd_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    # Read TileConfiguration.txt to get grid dimensions
    tile_config_path = os.path.join(input_dir, 'TileConfiguration.txt')
    if os.path.exists(tile_config_path):
        with open(tile_config_path, 'r') as f:
            lines = f.readlines()
            
        # Find max row and col for determining grid dimensions
        max_row = 0
        max_col = 0
        grid_positions = {}
        
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('dim'):
                parts = line.strip().split(';;')
                if len(parts) >= 2:
                    filename = parts[0]
                    pos_str = parts[1].strip('()')
                    x, y = map(float, pos_str.split(','))
                    
                    # Store position for each file
                    grid_positions[filename] = (x, y)
        
        # Determine grid layout (assuming the grid is in the form of rows x columns)
        # Find unique X and Y positions
        unique_x = sorted(list(set([pos[0] for pos in grid_positions.values()])))
        unique_y = sorted(list(set([pos[1] for pos in grid_positions.values()])))
        
        grid_width = len(unique_x)
        grid_height = len(unique_y)
        
        print(f"Detected grid: {grid_height} rows x {grid_width} columns")
        
        # Convert each file and save with row-column naming convention
        for nrrd_file in nrrd_files:
            file_path = os.path.join(input_dir, nrrd_file)
            
            # Determine row and column from position
            if nrrd_file in grid_positions:
                x, y = grid_positions[nrrd_file]
                col = unique_x.index(x)
                row = unique_y.index(y)
            else:
                # If not in tile configuration, derive from filename
                idx = int(nrrd_file.split('_')[1].split('.')[0])
                row = idx // grid_width
                col = idx % grid_width
            
            # Read NRRD file
            print(f"Converting {nrrd_file} to row {row}, col {col}")
            try:
                image = sitk.ReadImage(file_path)
                
                # Convert to numpy array
                array = sitk.GetArrayFromImage(image)
                
                # If it's a 3D image with single slice, get first slice
                if len(array.shape) == 3 and array.shape[0] == 1:
                    array = array[0]
                
                # Create new TIF image
                new_image = sitk.GetImageFromArray(array)
                
                # Copy metadata
                for key in image.GetMetaDataKeys():
                    new_image.SetMetaData(key, image.GetMetaData(key))
                
                # Save as TIF with row-column naming convention
                output_filename = f"{file_prefix}_r{row:03d}_c{col:03d}.tif"
                output_path = os.path.join(output_dir, output_filename)
                sitk.WriteImage(new_image, output_path)
                print(f"Saved {output_path}")
                
            except Exception as e:
                print(f"Error converting {nrrd_file}: {str(e)}")
    else:
        print("TileConfiguration.txt not found, using basic grid layout")
        # Assume grid is square or close to it
        grid_size = int(np.ceil(np.sqrt(len(nrrd_files))))
        
        for i, nrrd_file in enumerate(nrrd_files):
            file_path = os.path.join(input_dir, nrrd_file)
            
            # Determine row and column
            row = i // grid_size
            col = i % grid_size
            
            # Read NRRD file
            print(f"Converting {nrrd_file} to row {row}, col {col}")
            try:
                image = sitk.ReadImage(file_path)
                
                # Convert to numpy array
                array = sitk.GetArrayFromImage(image)
                
                # If it's a 3D image with single slice, get first slice
                if len(array.shape) == 3 and array.shape[0] == 1:
                    array = array[0]
                
                # Create new TIF image
                new_image = sitk.GetImageFromArray(array)
                
                # Copy metadata
                for key in image.GetMetaDataKeys():
                    new_image.SetMetaData(key, image.GetMetaData(key))
                
                # Save as TIF with row-column naming convention
                output_filename = f"{file_prefix}_r{row:03d}_c{col:03d}.tif"
                output_path = os.path.join(output_dir, output_filename)
                sitk.WriteImage(new_image, output_path)
                print(f"Saved {output_path}")
                
            except Exception as e:
                print(f"Error converting {nrrd_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert NRRD files to TIF format for MIST processing')
    parser.add_argument('--input-dir', type=str, required=True, help='Directory containing NRRD files')
    parser.add_argument('--output-dir', type=str, required=True, help='Directory where TIF files will be saved')
    parser.add_argument('--file-prefix', type=str, default='img', help='Prefix for output filenames')
    
    args = parser.parse_args()
    convert_nrrd_to_tif(args.input_dir, args.output_dir, args.file_prefix) 