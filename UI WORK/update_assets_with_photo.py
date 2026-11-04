"""
=============================================================================
      UPDATE CANDIDATE GRAPHICS WITH REAL PHOTO & OFFICIAL POSTER
 Uses real portrait of Pradhyumna Nagar, Rajendra Nagar, and official poster
 metadata to generate banners and icons.
=============================================================================
"""

import os
from PIL import Image, ImageDraw, ImageFont

CANDIDATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "candidate")
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
REGULAR_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Bold.ttf")

PHOTO_PATH = os.path.join(CANDIDATE_DIR, "candidate_photo.png")


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def generate_banner():
    """Generate 1080x420 mobile hero banner with real candidate photo."""
    width, height = 1080, 420
    # Gradient background inspired by official poster: Golden Yellow to Deep Saffron
    banner = Image.new("RGBA", (width, height), (255, 248, 225, 255))
    draw = ImageDraw.Draw(banner)

    # Top header bar: Deep Blue
    draw.rectangle([0, 0, width, 55], fill=(21, 101, 192))
    f_bar = get_font(BOLD_FONT_PATH, 28)
    draw.text((40, 27), "सबका साथ", font=f_bar, fill=(255, 255, 255), anchor="lm")
    draw.text((width - 40, 27), "सबका विकास", font=f_bar, fill=(255, 255, 255), anchor="rm")
    draw.text((width // 2, 27), "ग्राम पंचायत जयनगर", font=f_bar, fill=(255, 215, 0), anchor="mm")

    # Main content area: Saffron / Gold gradient effect
    draw.rectangle([0, 55, width, height - 45], fill=(255, 243, 205))

    # Paste real candidate photo on the left
    if os.path.exists(PHOTO_PATH):
        cand_img = Image.open(PHOTO_PATH).convert("RGBA")
        # Resize photo to fit banner height nicely (height ~320)
        p_height = 320
        aspect = cand_img.width / cand_img.height
        p_width = int(p_height * aspect)
        cand_resized = cand_img.resize((p_width, p_height), Image.Resampling.LANCZOS)
        # Position at bottom-left
        banner.paste(cand_resized, (35, height - 45 - p_height), cand_resized)

    # Right side text details
    text_x = 300

    f_post = get_font(BOLD_FONT_PATH, 38)
    draw.text((text_x, 90), "सरपंच पद हेतु", font=f_post, fill=(198, 40, 40), anchor="lm")

    f_sub = get_font(BOLD_FONT_PATH, 24)
    draw.text((text_x, 135), "शिक्षित, युवा, संघर्षशील, ईमानदार, सेवाभावी उम्मीदवार", font=f_sub, fill=(55, 71, 79), anchor="lm")

    # Candidate Name in large bold magenta/purple style matching the poster
    f_name = get_font(BOLD_FONT_PATH, 64)
    draw.text((text_x, 205), "प्रद्युम्न नागर", font=f_name, fill=(173, 20, 87), anchor="lm")

    f_mentor = get_font(BOLD_FONT_PATH, 28)
    draw.text((text_x + 460, 205), "राजेन्द्र नागर", font=f_mentor, fill=(21, 101, 192), anchor="lm")

    f_appeal = get_font(BOLD_FONT_PATH, 24)
    draw.text((text_x, 260), "को अपना अमूल्य मत एवं समर्थन देकर भारी मतों से विजयी बनावें", font=f_appeal, fill=(230, 81, 0), anchor="lm")

    f_phone = get_font(BOLD_FONT_PATH, 26)
    draw.text((text_x, 305), "📞 संपर्क: 9636556851", font=f_phone, fill=(27, 94, 32), anchor="lm")

    # Bottom footer: Village names (हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा)
    draw.rectangle([0, height - 45, width, height], fill=(21, 101, 192))
    f_footer = get_font(BOLD_FONT_PATH, 22)
    draw.text((width // 2, height - 23), "निवेदक: समस्त ग्राम पंचायत वासी — हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा", font=f_footer, fill=(255, 255, 255), anchor="mm")

    banner_rgb = banner.convert("RGB")
    out_path = os.path.join(CANDIDATE_DIR, "candidate_banner.png")
    banner_rgb.save(out_path, quality=95)
    print(f"Generated Banner: {out_path}")


def generate_app_icon():
    """Generate 512x512 app icon with real candidate photo."""
    size = (512, 512)
    icon = Image.new("RGBA", size, (21, 101, 192, 255))
    draw = ImageDraw.Draw(icon)

    # Gold ring
    draw.ellipse([15, 15, 497, 497], outline=(255, 215, 0, 255), width=8, fill=(255, 248, 225, 255))

    # Top title
    f_title = get_font(BOLD_FONT_PATH, 42)
    draw.text((256, 65), "जयनगर चुनाव", font=f_title, fill=(21, 101, 192), anchor="mm")

    # Center candidate photo circular cutout
    if os.path.exists(PHOTO_PATH):
        cand_img = Image.open(PHOTO_PATH).convert("RGBA")
        cand_resized = cand_img.resize((310, 415), Image.Resampling.LANCZOS)
        # Paste centered
        icon.paste(cand_resized, (105, 75), cand_resized)

    # Bottom ribbon banner
    draw.rounded_rectangle([45, 410, 467, 480], radius=16, fill=(173, 20, 87))
    f_name = get_font(BOLD_FONT_PATH, 38)
    draw.text((256, 445), "प्रद्युम्न नागर", font=f_name, fill=(255, 255, 255), anchor="mm")

    out_path = os.path.join(CANDIDATE_DIR, "app_icon.png")
    icon.save(out_path)
    print(f"Generated App Icon: {out_path}")


if __name__ == "__main__":
    generate_banner()
    generate_app_icon()
