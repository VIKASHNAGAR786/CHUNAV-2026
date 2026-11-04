"""
=============================================================================
             CAMPAIGN GRAPHICS & ASSET GENERATOR
 Generates high-res candidate banners, badges, and app icons using Pillow.
=============================================================================
"""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CANDIDATE_DIR = os.path.join(ASSETS_DIR, "candidate")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
os.makedirs(CANDIDATE_DIR, exist_ok=True)

REGULAR_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Bold.ttf")


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def create_app_icon():
    """Create 512x512 rounded election app icon."""
    size = (512, 512)
    img = Image.new("RGBA", size, (24, 76, 120, 255))  # Royal Blue
    draw = ImageDraw.Draw(img)

    # Gradient circle overlay
    draw.ellipse([20, 20, 492, 492], outline=(255, 183, 77, 255), width=8)

    f_large = get_font(BOLD_FONT_PATH, 72)
    f_sub = get_font(BOLD_FONT_PATH, 42)
    f_year = get_font(BOLD_FONT_PATH, 54)

    draw.text((256, 140), "जैनगर", font=f_large, fill=(255, 255, 255), anchor="mm")
    draw.text((256, 230), "चुनाव", font=f_large, fill=(255, 193, 7), anchor="mm")
    draw.text((256, 310), "2026", font=f_year, fill=(255, 255, 255), anchor="mm")

    # Bottom badge
    draw.rounded_rectangle([70, 380, 442, 450], radius=15, fill=(255, 152, 0, 255))
    draw.text((256, 415), "प्रद्युम्न नागर", font=f_sub, fill=(255, 255, 255), anchor="mm")

    icon_path = os.path.join(CANDIDATE_DIR, "app_icon.png")
    img.save(icon_path)
    print(f"Generated App Icon: {icon_path}")


def create_candidate_banner():
    """Create wide mobile banner (1080x420) for Home screen."""
    width, height = 1080, 420
    # Gradient Deep Saffron to Royal Blue
    img = Image.new("RGB", (width, height), (230, 81, 0))
    draw = ImageDraw.Draw(img)

    # Right side slant block
    draw.polygon([(450, 0), (width, 0), (width, height), (380, height)], fill=(21, 101, 192))

    f_title = get_font(BOLD_FONT_PATH, 54)
    f_role = get_font(BOLD_FONT_PATH, 34)
    f_slogan = get_font(REGULAR_FONT_PATH, 30)
    f_panchayat = get_font(BOLD_FONT_PATH, 32)

    # Left side (Saffron area): Candidate & Panchayat
    draw.text((40, 60), "ग्राम पंचायत जैनगर", font=f_panchayat, fill=(255, 243, 224))
    draw.text((40, 130), "प्रद्युम्न नागर", font=f_title, fill=(255, 255, 255))
    draw.text((40, 215), "प्रधान / सरपंच पद प्रत्याशी", font=f_role, fill=(255, 235, 59))
    draw.text((40, 280), "« आपका विश्वास, हमारा संकल्प »", font=f_slogan, fill=(255, 255, 255))

    # Right side (Blue area): Core priorities
    draw.text((470, 60), "विकास का नया विज़न 2026", font=f_title, fill=(255, 215, 0))
    draw.text((470, 140), "✔ हर घर शुद्ध पेयजल (नल-जल)", font=f_slogan, fill=(255, 255, 255))
    draw.text((470, 195), "✔ पक्की सड़कें व ढकी नालियाँ", font=f_slogan, fill=(255, 255, 255))
    draw.text((470, 250), "✔ आधुनिक स्कूल व डिजिटल शिक्षा", font=f_slogan, fill=(255, 255, 255))
    draw.text((470, 305), "✔ 100% पारदर्शी पंचायत प्रशासन", font=f_slogan, fill=(255, 255, 255))

    # Bottom bar
    draw.rectangle([0, height - 40, width, height], fill=(13, 71, 161))
    draw.text((width // 2, height - 20), "सेवा, समर्पण और सर्वांगीण ग्राम विकास का वादा", font=get_font(BOLD_FONT_PATH, 24), fill=(255, 255, 255), anchor="mm")

    banner_path = os.path.join(CANDIDATE_DIR, "candidate_banner.png")
    img.save(banner_path)
    print(f"Generated Banner: {banner_path}")


def create_candidate_photo():
    """Create stylized candidate portrait avatar (400x400)."""
    size = (400, 400)
    img = Image.new("RGBA", size, (245, 245, 245, 255))
    draw = ImageDraw.Draw(img)

    # Outer circle
    draw.ellipse([15, 15, 385, 385], fill=(255, 255, 255), outline=(230, 81, 0), width=8)

    # Stylized Avatar Icon
    # Head
    draw.ellipse([140, 70, 260, 190], fill=(255, 179, 0))
    # Tilak
    draw.rectangle([196, 95, 204, 135], fill=(198, 40, 40))
    # Torso
    draw.chord([60, 180, 340, 420], 180, 360, fill=(21, 101, 192))

    # Name label overlay
    draw.rounded_rectangle([40, 300, 360, 370], radius=15, fill=(230, 81, 0))
    f_name = get_font(BOLD_FONT_PATH, 34)
    draw.text((200, 335), "प्रद्युम्न नागर", font=f_name, fill=(255, 255, 255), anchor="mm")

    avatar_path = os.path.join(CANDIDATE_DIR, "candidate_photo.png")
    img.save(avatar_path)
    print(f"Generated Candidate Photo: {avatar_path}")


if __name__ == "__main__":
    create_app_icon()
    create_candidate_banner()
    create_candidate_photo()
