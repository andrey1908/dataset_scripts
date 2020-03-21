import os
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img-flds', '--images-folders', required=True, type=str, nargs='+')
    parser.add_argument('-root-flds', '--root-folders', type=str, nargs='+')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def make_images_list(images_folders, root_folders):
    if len(images_folders) != len(root_folders):
        raise ValueError()
    out_list = list()
    next_images_folders = list()
    next_root_folders = list()
    for images_folder, root_folder in zip(images_folders, root_folders):
        items = os.listdir(images_folder)
        for item in items:
            item_path = os.path.join(images_folder, item)
            if os.path.isdir(item_path):
                next_images_folders.append(item_path)
                next_root_folders.append(os.path.join(root_folder, item))
            elif os.path.isfile(item_path):
                ext = item.split('.')[-1]
                if (ext == 'jpg'):
                    out_list.append(os.path.join(root_folder, item))
            else:
                raise RuntimeError()
    if len(next_images_folders) > 0:
        out_list += make_images_list(next_images_folders, next_root_folders)
    return out_list


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    if args.root_folders is None:
        args.root_folders = '' * len(args.images_foldres)
    out_list = make_images_list(args.images_folders, args.root_folders)
    with open(args.out_file, 'w') as f:
        for i, line in enumerate(out_list):
            if i == len(out_list)-1:
                f.write(line)
            else:
                f.write(line+'\n')
