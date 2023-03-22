# Dataset scripts
This repository contains python3 scripts to work with annotation files (mainly in COCO format).

Before using make sure that dataset_scripts folder is in your PYTHONPATH environment variable.

## Converters

Not all converters are described.
___

**converters/coco2darknet.py**

Converts COCO annotations to the format used to train networks in darknet repository.
```bash
-json, --json-file                      - json file with COCO annotations
-img-root-fld, --images-root-folder     - path to images folder
-out-list, --out-list-file              - output file with list of images files
-out-anns-fld, --out-annotations-folder - output folder to save converted annotations to
-root-fld, --root-folder [default './'] - paths to images in output file '-out-list' are set
                                          relative to the directory specified in this parameter
```
___

## Dataset tools

Not all dataset tools are described.
___

**coco_nms.py**

NMS (non-maximum suppression) algorithm.

Before using this script compile nms.c into shared library nms.so:
```bash
gcc nms.c -shared -fPIC -o nms.so
```

Usage:
```bash
-json, --json-file - json file with COCO annotations
-thr, --threshold  - IoU (intersection over union) threshold for NMS algorithm
-out, --out-file   - output COCO annotation file
```
___

**dataset_info.py**

Short summary about COCO annotation file.
```bash
-json, --json-file - json file with COCO annotations
```
___

**draw_boxes.py**

Draw bounding boxes form COCO annotations on images.
```bash
-json, --json-file                                     - json file with COCO annotations (this file may contain
                                                         only boxes without images paths and categories; in that case
                                                         json file with images paths and categories should be
                                                         specified in parameter '-img-json' (see below))
-img-fld, --images-folder                              - path to images folder
-out-fld, --out-folder                                 - output folder to save images with drawn boxes to
-imgs-to-draw, --images-files-to-draw [optional]       - images files to draw boxes on (relative to the current directory)
-num, --images-number [optional]                       - number of images to draw boxes on (has on effect
                                                         if '-imgs-to-draw' is specified)
-rnd, --random [optional]                              - used in combination with '-num': select random images
                                                         to draw on, otherwise first images are selected
-owb, --only-with-boxes [optional]                     - used in combination with '-num': do not select images
                                                         that have no boxes
-img-json, --images-json-file [optional]               - json file with images paths and categories if '-json'
                                                         does not contains that information
-preserve-files-tree, --preserve-files-tree [optional] - preserve images files tree when saving images with drawn boxes,
                                                         otherwise all images are saved in output directory '-out-fld'
                                                         and if there are images with the same name, one of them is renamed
-thr, --threshold [default 0.]                         - filter out boxes with score less than '-thr' (has no effect
                                                         if annotations do not contain 'score' field)
```
If both *-imgs-to-draw* and *-num* are not specified then all the images are used to draw boxes on.
___

**mark_coco_annotations.py**

Add a field to COCO annotations with specified value.
```bash
-json, --json-file - json file with COCO annotations
-f, --field        - field name to add
-v, --value        - value to add. eval() is applied to this parameter
--force [optional] - rewrite field if it already exists. Without this flag
                     runtime error will be raised if the field alread exists
-out, --out-file   - output COCO annotation file
```
___

**metrics_eval.py**

Evaluates AP and mAP metrics for detection results.
```bash
-ann, --annotations-file            - json file with COCO gt (shoud contain images paths and categories)
-det, --detections-file             - json file with detection results in COCO format (should contain only
                                      detection results without images paths and categories)
-area, --area [default 0**2 1e5**2] - remove boxes with area beyond this range
-shape, --shape [default None None] - used in combination with '-area': before computing box area,
                                      image containing that box is scaled keeping aspect ratio so that
                                      this image is fitted into the (width, height) box specified
                                      in this parameter. The box on the image is scaled with the image
                                      and after that box area is computed
```
___

**remove_empty_images.py**

Removes images that contain no labels from COCO annotation file.
```bash
-json, --json-file - json file with COCO annotations
-out, --out-file   - output COCO annotation file
```
___

**replace_classes.py**

Merges, removes, adds and renames categories in COCO annotation file (see usage example after parameters description).
```bash
-json, --json-file                               - json file with COCO annotations
-new-cats, --new-categories-names                - new categories names
-old-cat-name-to-new, --old-category-name-to-new - how to convert old category names to new ones.
                                                   See example below. If special name convert_all_categories
                                                   (or conv_all_cats) is specified, then '-new-cats' should
                                                   contain only one category and all old categories
                                                   are converted into that new one.
-out, --out-file                                 - output COCO annotation file
```
For example, we have annotation file annotations.json with categories **person**, **car** and **van**, and we want to convert **person** to **pedestrian**, **car** and **van** to **vehicle**. To do this we can use:
```bash
python replace_classes.py
    -json annotations.json
    -new-cats pedestrian vehicle
    -old-cat-name-to-new 'person->pedestrian car->vehicle van->vehicle'
    -out new_annotations.json
```
___

**split_coco.py**

Splits COCO annotation file into two files. Before splitting images are shuffled.
```bash
-json, --json-file              - json file with COCO annotations
-train, --train-out-file        - output COCO annotation file for training
-test, --test-out-file          - output COCO annotation file for testing
-sr, --split-rate [default 0.8] - share of images in output training file
```
___

**unite_coco.py**

Merges multiple COCO annotation files into one. Categories with the same name are merged into one. Images with the same field 'file_name' are merged.
```bash
-jsons, --json-files - multiple json files with COCO annotations
-out, --out-file     - output COCO annotation file
```
___

**unite_datasets.py**

Merges multiple COCO annotation files into one and copies (or makes hard links) images into one directory. Categories with the same name are merged into one. If there are images with the same name, one of them is renamed.
```bash
-jsons, --json-files              - multiple json files with COCO annotations
-img-flds, --images-folders       - multiple paths to images folders for each file in '-jsons' parameter
-out, --out-file                  - output COCO annotation file
-out-img-fld, --out-images-folder - output folder for images for merged dataset
-ml, --make-links [optional]      - make hard links for images instead of copying them
-co, --copy-ok [optional]         - used in combination with '-ml': if could not make hard link
                                    for the image, then do not raise runtime error and simply copy that image
```
