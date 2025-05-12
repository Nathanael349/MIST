import numpy as np
import matplotlib.pyplot as plt
import skimage.io

# Read the image
img = skimage.io.imread('sample/outputs/stitched_image.tif')

# Remove the extra dimension if it exists
if len(img.shape) == 3 and img.shape[2] == 1:
    img = img.squeeze()

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Display original image
im1 = ax1.imshow(img, cmap='gray')
ax1.set_title('Original Image')
plt.colorbar(im1, ax=ax1)

# Display contrast-adjusted image
# Normalize to 0-1 range
img_norm = (img - np.min(img)) / (np.max(img) - np.min(img))
im2 = ax2.imshow(img_norm, cmap='gray')
ax2.set_title('Contrast Adjusted')
plt.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show() 