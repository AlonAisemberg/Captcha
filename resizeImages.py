from PIL import Image
import os

input_folder = "rotten_r"   # folder with your original images
output_folder = "rotten" # folder to save resized images

os.makedirs(output_folder, exist_ok=True)

TARGET_SIZE = 160

for filename in os.listdir(input_folder):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        continue

    img_path = os.path.join(input_folder, filename)
    img = Image.open(img_path).convert("RGB")

    # Resize while keeping aspect ratio
    img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    # Create white background
    background = Image.new("RGB", (TARGET_SIZE, TARGET_SIZE), (255, 255, 255))

    # Calculate paste position (centered)
    paste_x = (TARGET_SIZE - img.width) // 2
    paste_y = (TARGET_SIZE - img.height) // 2
    background.paste(img, (paste_x, paste_y))

    # Save
    save_path = os.path.join(output_folder, filename)
    background.save(save_path, format="PNG")

print("Done! Images saved to:", output_folder)
