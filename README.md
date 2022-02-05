## Garmin Fleet 770 with [LARDIS:ONE](https://lardis-one.de/)
At fire department we use the LARDIS:ONE connected to our TETRA radio. With this additional system we are able to get operation details automatically and navigation starts also automatically to the operation target.
At navigation map, we are able to display custom POIs. For use these POIs are fire hydrants, fire water ponds, suction points, water tanks and fire departments.


## Creating icons for Point of Interests (POIs)
After a lot of testing I came to the following result of icon properties:
- size: 48x48
- format: BMP (Microsoft Windows bitmap image)
- depth: 8 bit
- colorspace: sRGB
- type: Palette
- background color which should be displayed as transparent: magenta
- compression: RLE (but is actually not supported by GPSBabel)

### Convert the source SVG images
We first convert our source SVG files to intermediate format PNG with [inkscape](https://inkscape.org/).

```bash
inkscape --export-type=png -w 48 -h 48 --export-background=magenta *.svg
```

Now we can convert the PNG images with the help of [imagemagick](https://imagemagick.org/) to the needed target format:

```bash
mogrify -format bmp -type palette +compress *.png
```

At last, we clean up our intermediate format:
```bash
rm *.png
```

### Additional links
- [Creating Custom POI Files for BaseCamp](https://support.garmin.com/de-DE/?faq=0c2IHhAhvg6ttRP3u7yZ46)
- [Creating Custom POI Files](https://support.garmin.com/en-US/?faq=5IgMIBdkJN5M7CzMmytjs6)
- [Creating Icons for Custom POIs](https://support.garmin.com/en-US/?faq=gtDjiglxSO5nLNr3BP8m36)


## GPSBabel
[GPSBabel](https://github.com/GPSBabel/gpsbabel) has actually some restrictions, so we have to modify it. First create a clone by `git clone git@github.com:GPSBabel/gpsbabel.git`.
Then modify the file "garmin_gpi.cc" with:

```diff
diff --git a/garmin_gpi.cc b/garmin_gpi.cc
index 123d08dc..eb28ad77 100644
--- a/garmin_gpi.cc
+++ b/garmin_gpi.cc
@@ -1315,12 +1315,12 @@ load_bitmap_from_file(const char* fname, unsigned char** data, int* data_sz)
 #endif
 
   /* sort out unsupported files */
-  if (!((src_h.width <= 24) && (src_h.height <= 24) &&
+  if (!((src_h.width <= 48) && (src_h.height <= 48) &&
         (src_h.width > 0) && (src_h.height > 0))) {
     fatal(MYNAME ": Unsupported format (%dx%d)!\n", src_h.width, src_h.height);
   }
   if (!((src_h.bpp == 8) || (src_h.bpp == 24) || (src_h.bpp == 32))) {
-    fatal(MYNAME ": Unsupported color depth (%d)!\n", src_h.bpp);
+    //fatal(MYNAME ": Unsupported color depth (%d)!\n", src_h.bpp);
   }
   if (!(src_h.compression_type == 0)) {
     fatal(MYNAME ": Sorry, we don't support compressed bitmaps.\n");
```

compile with `qmake`, `make` and execute it directly:

```bash
./gpsbabel -w -i gpx -f PATH_TO_INPUT_FILE.gpx -o garmin_gpi,bitmap=PATH_TO_IMAGE.bmp,category=Gerätehäuser,sleep=2,unique=0,writecodec=utf8 -F OUTPUT_PATH.gpi
```

## Upload GPI to garmin device
After uploading the GPI file(s) to the garmin device in folder `/garmin/POI` the device must be rebooted.
Make sure you have activated _"POIs along the route"_ to see your uploaded POIs while navigating.
Now you have to drive some meters so garmin while analyse your route otherwise you wouldn't see them.
