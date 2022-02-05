```bash
inkscape --export-type=png -w 24 -h 24 --export-background=magenta *.svg
```

PNG Bilder in BMP umwandeln
```bash
mogrify -format bmp -alpha set *.png
```
unter Windows:
```bash
magick mogrify -format bmp -alpha set *.png
```

Aufräumen
```bash
rm *.png
```
