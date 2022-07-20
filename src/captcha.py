import random
import os
import argparse
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from typing import List


CHAR_LIST = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F',
    'G', 'H', 'J', 'K', 'L',
    'M', 'N', 'O', 'P', 'Q', 'R',
    'S', 'T', 'U', 'V', 'W', 'X',
    'Y', 'Z',
]


def get_noised_bg(w: int, h: int):
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))

    # the light spot
    count = int(w * h * 0.8)
    for _ in range(count):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        grayscale = random.randint(150, 230)
        rgb = (grayscale, grayscale, grayscale)
        img.putpixel((x, y), rgb)

    # the darker spot
    count = int(w * h * 0.05)
    for _ in range(count):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        grayscale = random.randint(5, 80)
        rgb = (grayscale, grayscale, grayscale)
        img.putpixel((x, y), rgb)
    return img


def get_text_img(w: int, h: int, text: str, font: str):
    N = len(text)
    fnt_size = random.randint(h - 10, h - 3)
    fnt = ImageFont.truetype(font, fnt_size)
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    color = (0, 0, 0, random.randint(200, 255))
    for i, c in enumerate(text):
        char_img = Image.new("RGBA", (fnt_size, fnt_size), (255, 255, 255, 0))
        textdraw = ImageDraw.Draw(char_img)

        textdraw.text((0, 0), c, font=fnt, fill=color)

        char_img = char_img.rotate(random.randint(-30, 30), expand=True)
        scaled_length = random.randint(int(fnt_size * 0.9), int(fnt_size * 1.1))

        char_img = char_img.resize((scaled_length, scaled_length))

        char_w = w // N
        x = i * char_w + random.randint(0, max(0, char_w - fnt_size))
        # x = max(0, min(w - char_img.width, x))
        # x = max(0, min(w - char_img.width//2, x))

        y = random.randint(0, max(0, int((h - char_img.height) / 2)))
        # print(anchor_x, x, y, char_img.size)
        img.paste(char_img, (x, y), char_img)

    return img


def get_arc_img(w: int, h: int):
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    color = (0, 0, 0, 255)
    xy = [
        (random.randint(-20, 0), 0),
        (random.randint(int(1.7 * w), int(2.2 * w)), random.randint(int(1.5 * h), 4 * h)),
    ]

    draw.ellipse(xy, outline=color, width=random.randint(5, 10))

    return img


def get_mask(img: Image):
    w, h = img.size


def set_alpha(img, value: int):
    w, h = img.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.getpixel((x, y))
            a = value if a > 0 else 0
            img.putpixel((x, y), (r, g, b, a))


def get_overlapping(w: int, h: int, bg: Image, img1: Image, img2: Image):
    tmp_img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    tmp_img.paste(bg, (0, 0), img1)

    overlapped = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    overlapped.paste(tmp_img, (0, 0), img2)
    return overlapped


def generate_text(text_len: int):
    assert text_len > 0
    global CHAR_LIST
    return ''.join(random.choices(CHAR_LIST, k=text_len))


def generate_captcha(font_list: List[str]):
    # get an image
    w = random.randint(90, 180)
    h = random.randint(30, 60)

    noised_bg = get_noised_bg(w, h)

    # get a font image
    text = generate_text(4)
    text_img = get_text_img(w, h, text, random.choice(font_list))

    arc_img = get_arc_img(w, h)

    # generate image
    arc_mask = arc_img.copy()
    text_mask = text_img.copy()

    # text_mask.putalpha(255)
    # arc_mask.putalpha(0)
    set_alpha(text_mask, random.randint(180, 220))
    set_alpha(arc_mask, random.randint(180, 220))

    # get overlapped mask
    overlapped = get_overlapping(w, h, noised_bg, arc_img, text_img)

    img = noised_bg.copy()
    img.paste(text_img, (0, 0), text_mask)
    img.paste(arc_img, (0, 0), arc_mask)

    img.paste(noised_bg, (0, 0), overlapped)
    return img, text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int)
    parser.add_argument('output', type=str, help='Path of output directory.')
    parser.add_argument('-f', '--font_dir', type=str, default='./fonts/')
    args = parser.parse_args()
    print(args)

    font_list = [os.path.join(args.font_dir, f) for f in os.listdir(args.font_dir) if f.endswith('ttf')]
    for _ in tqdm(range(args.number)):
        img, text = generate_captcha(font_list)
        img = img.convert('RGB')

        filename = os.path.join(args.output, f'{text}.jpeg')
        img.save(filename)
