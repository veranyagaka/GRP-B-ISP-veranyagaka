from PIL import Image
import os
import sys

def downsample_xray(input_path, output_path=None, downsample_factor=2, display=False):
    """
    Downsamples an image and upsamples it back to simulate low resolution.
    """

    # Load image
    img = Image.open(input_path).convert("L")
    original_size = img.size
    print(f"✅ Original size: {original_size}")

    # Downsample + upsample
    low_res = img.resize(
        (original_size[0] // downsample_factor, original_size[1] // downsample_factor),
        Image.BICUBIC
    )
    simulated_low_res = low_res.resize(original_size, Image.BICUBIC)

    # Auto output path if none provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_downsampled{ext}"

    # Save
    simulated_low_res.save(output_path)
    print(f"💾 Saved downsampled image to: {output_path}")

    # Optional display
    if display:
        simulated_low_res.show()

    return simulated_low_res


if __name__ == "__main__":
    # Ensure at least one argument
    if len(sys.argv) < 2:
        print("Usage: python3 downsample.py <image_path> [downsample_factor] [output_path]")
        sys.exit(1)

    input_path = sys.argv[1]

    # Optional downsample factor
    downsample_factor = int(sys.argv[2]) if len(sys.argv) >= 3 else 2

    # Optional output path
    output_path = sys.argv[3] if len(sys.argv) >= 4 else None

    # Run function
    downsample_xray(
        input_path=input_path,
        output_path=output_path,
        downsample_factor=downsample_factor,
        display=False
    )
