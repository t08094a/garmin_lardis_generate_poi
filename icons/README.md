
inkscape --export-type=png -w 128 -h 128 *.svg

mogrify -format bmp -alpha set *.png
unter Windows:
magick mogrify -format bmp -alpha set *.png

rm *.png
