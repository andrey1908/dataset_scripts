import argparse
import os
from PIL import Image, ImageFile
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img-list', '--images-list-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', type=str, default='')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def image_file2label_file(image_file):
    label_file = image_file.split('/')
    if len(label_file) == 1:
        label_file = label_file[0]
    else:
        label_file[-2] = 'labels'
        label_file = '/'.join(label_file)

    label_file = label_file.split('.')
    label_file[-1] = 'txt'
    label_file = '.'.join(label_file)
    return label_file


def find_truncated_images_in_list(images_list, images_folder):
    truncated_images_files = list()
    new_images_list = list()
    for image_file in tqdm(images_list):
        image_path = os.path.join(images_folder, image_file)
        if not os.path.isfile(image_path):
            raise RuntimeError()
        try:
            im = Image.open(image_path)
            im = im.convert("L")  # There might be a faster way to get exception if image is truncated
        except:
            truncated_images_files.append(image_file)
        else:
            new_images_list.append(image_file)
    return new_images_list, truncated_images_files


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.images_list_file, 'r') as f:
        images_list = f.readlines()
    for i in range(len(images_list)):
        if images_list[i][-1] == '\n':
            images_list[i] = images_list[i][:-1]
    new_images_list, truncated_images_files = find_truncated_images_in_list(images_list, args.images_folder)
    with open(args.out_file, 'w') as f:
        for i, line in enumerate(new_images_list):
            if i == len(new_images_list)-1:
                f.write(line)
            else:
                f.write(line+'\n')
    print('')
    for truncated_image_file in truncated_images_files:
        print(truncated_image_file)

