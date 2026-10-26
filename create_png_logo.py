from PIL import Image, ImageDraw

# Create 256x256 high-res RGBA image
img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Outer emerald green rounded emblem
draw.rounded_rectangle([(16, 16), (240, 240)], radius=55, fill=(6, 78, 59, 255), outline=(245, 158, 11, 255), width=4)

# Security Shield shape (Citizen Protection)
shield_coords = [
    (128, 50),
    (195, 78),
    (195, 138),
    (128, 185),
    (61, 138),
    (61, 78)
]
draw.polygon(shield_coords, fill=(16, 185, 129, 255), outline=(255, 255, 255, 255))

# Bangladesh Red Circle in center
draw.ellipse([(95, 92), (161, 158)], fill=(239, 68, 68, 255))

# AI Node Star / Diamond in center
draw.polygon([(128, 110), (135, 125), (150, 125), (138, 135), (142, 150), (128, 140), (114, 150), (118, 135), (106, 125), (121, 125)], fill=(255, 255, 255, 255))

img.save("/Users/tamimarahmanchoity/Desktop/CivicSphere-AI/assets/nagorik_logo.png", "PNG")
print("Saved nagorik_logo.png successfully")
