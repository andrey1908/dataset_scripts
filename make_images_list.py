import os
import argparse
from utils import find_files


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img-flds', '--images-folders', required=True, type=str, nargs='+')
    parser.add_argument('-root-fld', '--root-folder', type=str, default='./')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def make_images_list(images_folders, root_folder):
    found_files, unknown_extensions = find_files(images_folders, ['.jpg', '.png'], ['.txt'])
    print('Unknown extensions: {}'.format(unknown_extensions))
    found_files = list(map(lambda x: os.path.relpath(x, root_folder), found_files))
    return found_files


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    out_list = make_images_list(args.images_folders, args.root_folder)
    with open(args.out_file, 'w') as f:
        for i, line in enumerate(out_list):
            if i == len(out_list)-1:
                f.write(line)
            else:
                f.write(line+'\n')

