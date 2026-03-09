"""
Générateur d'images pour les mini-événements du chat.
Style : fond sombre avec points lumineux, mot en blanc au centre.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_word_image(word: str, output_path: str) -> str:
    """Génère une image avec le mot affiché sur fond étoilé."""
    width, height = 600, 200
    img = Image.new("RGB", (width, height), color=(25, 35, 55))

    draw = ImageDraw.Draw(img)

    # Points lumineux (étoiles) en arrière-plan
    for _ in range(150):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        brightness = random.randint(150, 255)
        radius = random.randint(1, 2)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(brightness, brightness, brightness))

    # Texte au centre - essayer différentes polices
    font_size = 48
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (OSError, IOError):
            continue

    if font is None:
        font = ImageFont.load_default()

    # Obtenir la taille du texte
    bbox = draw.textbbox((0, 0), word, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Ombre légère pour lisibilité
    draw.text((x + 2, y + 2), word, font=font, fill=(15, 25, 45))
    draw.text((x, y), word, font=font, fill=(255, 255, 255))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
