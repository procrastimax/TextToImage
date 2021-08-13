#!/usr/bin/python3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import argparse
import sys
import textwrap
import re
from typing import Dict

clean_word_re = re.compile("[^a-zA-Z]")


def parse_from_stdin() -> str:
    text: str = ""
    for line in sys.stdin:
        text += line
    return text


def parse_from_file(filename: str) -> str:
    with open(filename, "r") as f:
        file_text = f.read()
        return file_text


def generate_image_from_text(
    text: str,
    image_out_path: str,
    text_width: int = 50,
    font_size: int = 11,
    font: str = "./fonts/DejaVuSans.ttf",
    font_bold: str = "./fonts/DejaVuSans-Bold.ttf",
    col_bg: str = "#ffffff",
    col_fg: str = "#000000",
    margin: int = 6,
    highlighted_words: Dict[str, str] = {},
):

    img_font = ImageFont.truetype(font, font_size)
    img_font_bold = ImageFont.truetype(font_bold, font_size)

    # create test image to get width/ height
    testImg = Image.new("RGB", (1, 1))
    testDraw = ImageDraw.Draw(testImg)

    # get max_height/ weight for the splitted lines
    max_width: int = 0
    max_height: int = 0

    line_list = textwrap.wrap(text, text_width)
    # get example width/ height
    for line in line_list:
        img_width, img_height = testDraw.textsize(line, img_font_bold)
        if img_width > max_width:
            max_width = img_width
        if img_height > max_height:
            max_height = img_height

    img = Image.new(
        "RGB", (max_width + margin, (len(line_list) * max_height) + margin), col_bg
    )
    draw = ImageDraw.Draw(img)

    offset: float = margin / 2

    if len(highlighted_words) == 0:
        for line in line_list:
            draw.text((margin / 2, offset), line, font=img_font, fill=col_fg)
            offset += img_font.getsize(line)[1]
    else:
        # if we want to highlight words, we need to draw the text word by word and not line by line
        h_words = list(highlighted_words.keys())
        for line in line_list:
            word_list = line.split()  # hopefully this works
            text_margin = margin / 2
            for word in word_list:
                # clean word to remove punctuations
                clean_word = clean_word_re.sub("", word)

                if clean_word in h_words:
                    draw.text(
                        (text_margin, offset),
                        word,
                        font=img_font_bold,
                        fill=highlight_words[clean_word],
                    )
                    text_margin += img_font_bold.getsize(word + " ")[0]
                else:
                    draw.text((text_margin, offset), word, font=img_font, fill=col_fg)
                    text_margin += img_font.getsize(word + " ")[0]

            offset += img_font.getsize(line)[1]

    img.save(image_out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "A program to generate an image from a given text. Text can be provided either by a textfile or STDIN."
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=str,
        help="Filename from which the text shall be read. If no filename is specified, the text is read from STDIN.",
        default="",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Sets the filename of the output image.",
        default="output_img.png",
    )
    parser.add_argument(
        "-s",
        "--font-size",
        type=int,
        help="Sets the font size to be used to generate the image.",
        default=11,
    )
    parser.add_argument(
        "-m",
        "--margin",
        type=int,
        help="Sets the margin between the image-border and the text.",
        default=6,
    )
    parser.add_argument(
        "-f",
        "--font-path",
        type=str,
        help="Sets the path to the true-type-font (.ttf) that shall be used to generate the image. Default is the provided DejaVuSans.",
        default="./fonts/DejaVuSans.ttf",
    )
    parser.add_argument(
        "-fb",
        "--font-path-bold",
        type=str,
        help="Sets the path to the bold true-type-font (.ttf) that shall be used to generate highlighted words in the image. Default is the provided DejaVuSans-Bold.",
        default="./fonts/DejaVuSans-Bold.ttf",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        help="Sets the character width per line. Aka. how many characters shall be displayed for each line.",
        default=50,
    )
    parser.add_argument(
        "-fg",
        "--foreground-color",
        type=str,
        help="Sets the foreground (text) color of the generated image. (Default: black)",
        default="#000000",
    )
    parser.add_argument(
        "-bg",
        "--background-color",
        type=str,
        help="Sets the background color of the generated image. (Default: white)",
        default="#ffffff",
    )

    parser.add_argument(
        "-hw",
        "--highlight-words",
        type=str,
        help="A string list of words that shall be highlighted with the given color. Example: '-hw word1-#123456 word2-#654321 ...'",
        nargs="+",
        default=[],
    )

    args = parser.parse_args()

    img_text: str = ""
    if len(args.input_file) == 0:
        img_text = parse_from_stdin()
    else:
        img_text = parse_from_file(args.input_file)

    img_text = img_text.replace("\n", " ")
    img_text = img_text.replace("  ", " ")
    img_text = img_text.strip()

    highlight_list = args.highlight_words
    highlight_words: Dict[str, str] = {}
    # create dict from passed words and colors
    for entry in highlight_list:
        tmp_split = []
        if "-" in entry:
            tmp_split = entry.split("-")
            if len(tmp_split) == 0:
                print(f"{entry} does not contain a word with a length greater than 0!")
                continue

            if len(tmp_split) != 2:
                print(
                    f"{tmp_split} is not a properly format to define highlighted words! Format is: WORD-#HEXCODE"
                )
                continue

            # check if the color is properly formatted
            if not "#" in tmp_split[1] or len(tmp_split[1]) != 7:
                print(
                    f"{tmp_split[1]} is not a propery hex color to highlight {tmp_split[0]}"
                )
                continue
            highlight_words[tmp_split[0]] = tmp_split[1]

    margin = args.margin
    generate_image_from_text(
        text=img_text,
        image_out_path=args.output,
        text_width=args.width,
        font=args.font_path,
        font_bold=args.font_path_bold,
        font_size=args.font_size,
        margin=args.margin,
        col_bg=args.background_color,
        col_fg=args.foreground_color,
        highlighted_words=highlight_words,
    )
