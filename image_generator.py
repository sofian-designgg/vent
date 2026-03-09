"""
Générateur d'images pour les mini-événements du chat.
Style : fond sombre avec points lumineux, mot en GROS et bien visible au centre.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_word_image(word: str, output_path: str) -> str:
    """Génère une image avec le mot affiché en grand et très lisible sur fond étoilé."""
    width, height = 900, 350
    img = Image.new("RGB", (width, height), color=(20, 30, 50))

    draw = ImageDraw.Draw(img)

    # Points lumineux (étoiles) en arrière-plan - moins nombreux pour ne pas distraire
    for _ in range(120):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        brightness = random.randint(120, 200)
        radius = random.randint(1, 2)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(brightness, brightness, brightness))

    # Taille de police BEAUCOUP plus grande et bien lisible
    font_size = 120
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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

    # Contour épais noir pour max visibilité
    outline_width = 4
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), word, font=font, fill=(0, 0, 0))
    # Texte principal blanc bien visible
    draw.text((x, y), word, font=font, fill=(255, 255, 255))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
