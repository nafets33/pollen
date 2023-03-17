# https://medium.com/grabngoinfo/creat-beautiful-ai-art-using-python-kerascv-stablediffusion-on-google-colab-628ded302047
# Model
from tensorflow import keras
import  keras_cv
keras.mixed_precision.set_global_policy("mixed_float16")

# Visualization
import matplotlib.pyplot as plt

# Save the image
from PIL import Image

# Create a model
model = keras_cv.models.StableDiffusion(img_height=512, 
                                        img_width=512,
                                        jit_compile=True)

def plot_images(images):
    # Set figure size
    plt.figure(figsize=(20, 20))
    # Loop through each image
    for i in range(len(images)):
        # Subplot setup
        ax = plt.subplot(1, len(images), i + 1)
        # Plot each image
        plt.imshow(images[i])
        # Do not show axis
        plt.axis("off")


# Create images from text
images = model.text_to_image(prompt="A painting of a city by vincent van gogh, highly detailed, sharp focused, impressionism, oil painting",
                             batch_size=2)

# Plot the images
plot_images(images)