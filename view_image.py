import numpy as np
import matplotlib.pyplot as plt
import skimage.io

# Read both images
fluorescent_img = skimage.io.imread('sample/Small_Fluorescent_Test_Dataset/outputs/stitched_image.tif')
phase_img = skimage.io.imread('sample/Small_Phase_Test_Dataset/outputs/stitched_image.tif')

# Remove the extra dimension if it exists
if len(fluorescent_img.shape) == 3 and fluorescent_img.shape[2] == 1:
    fluorescent_img = fluorescent_img.squeeze()
if len(phase_img.shape) == 3 and phase_img.shape[2] == 1:
    phase_img = phase_img.squeeze()

# Create figure and axes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Create colorbars once
cbar1 = plt.colorbar(plt.cm.ScalarMappable(cmap='gray'), ax=ax1)
cbar2 = plt.colorbar(plt.cm.ScalarMappable(cmap='gray'), ax=ax2)

# Function to update the display
def update_display(image_type):
    ax1.clear()
    ax2.clear()
    
    if image_type == 'fluorescent':
        img = fluorescent_img
        title = 'Fluorescent Image'
    else:
        img = phase_img
        title = 'Phase Image'
    
    # Display original image
    im1 = ax1.imshow(img, cmap='gray')
    ax1.set_title(f'{title} - Original')
    cbar1.update_normal(im1)
    
    # Display contrast-adjusted image
    img_norm = (img - np.min(img)) / (np.max(img) - np.min(img))
    im2 = ax2.imshow(img_norm, cmap='gray')
    ax2.set_title(f'{title} - Contrast Adjusted')
    cbar2.update_normal(im2)
    
    plt.tight_layout()
    fig.canvas.draw()

# Add buttons
from matplotlib.widgets import Button

# Create axes for buttons
ax_button1 = plt.axes([0.2, 0.01, 0.2, 0.05])
ax_button2 = plt.axes([0.6, 0.01, 0.2, 0.05])

# Create buttons
button1 = Button(ax_button1, 'Show Fluorescent')
button2 = Button(ax_button2, 'Show Phase')

# Button callbacks
def show_fluorescent(event):
    update_display('fluorescent')

def show_phase(event):
    update_display('phase')

button1.on_clicked(show_fluorescent)
button2.on_clicked(show_phase)

# Show fluorescent image by default
update_display('fluorescent')
plt.show() 