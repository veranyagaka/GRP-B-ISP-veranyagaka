from PIL import Image
import os

def downsample_xray(input_path, output_path=None, downsample_factor=2, display=True):
    """
    Downsamples an image and upsamples it back to original size to simulate a low-resolution image.

    Args:
        input_path (str): Path to the input image file.
        output_path (str, optional): Path to save the resulting image. Defaults to same directory.
        downsample_factor (int): Factor to reduce resolution by (e.g., 2, 4).
        display (bool): If True, displays the final image.
    """
    # Load the image
    img = Image.open(input_path).convert("L")  # Convert to grayscale for X-rays
    original_size = img.size  # (width, height)
    print(f"✅ Original size: {original_size}")

    # Downsample and upsample back using bicubic interpolation
    low_res = img.resize(
        (original_size[0] // downsample_factor, original_size[1] // downsample_factor),
        Image.BICUBIC
    )
    simulated_low_res = low_res.resize(original_size, Image.BICUBIC)

    # Define save path if not provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_downsampled{ext}"

    # Save the result
    simulated_low_res.save(output_path)
    print(f"💾 Saved downsampled image to: {output_path}")

    # Display for visual verification
    if display:
        simulated_low_res.show()

    return simulated_low_res


if __name__ == "__main__":
    # Example usage
    input_image = "normal_sample.jpeg"   # <-- change to your own image file
    downsampled_img = downsample_xray(input_image, downsample_factor=2)
