import os
import argparse
import tensorflow as tf
from tqdm import tqdm
from waymo_open_dataset import dataset_pb2 as open_dataset
from parsers import WAYMO_PARSERS_REGISTRY
from dataset_scripts.utils import Context, ParsersWrapper

tf.enable_eager_execution()


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-data-paths', '--data-paths', required=True, type=str, nargs='+')
    parser.add_argument('-parsers', '--parsers-names', required=True, type=str, nargs='+')
    parser.add_argument('-outs', '--out-files', type=str, nargs='+', default=list())
    parser.add_argument('-out-img-fld', '--out-images-folder', type=str, default='images/')
    parser.add_argument('-ifn', '--images-feature-name', type=str, default='camera')
    parser.add_argument('-no-si', '--no-save-images', dest='save_images', action='store_false')
    parser.add_argument('-img-root-fld', '--images-root-folder', type=str)
    parser.add_argument('-out-track-fld', '--out-track-folder', type=str, default='track/')
    parser.add_argument('-track-root-fld', '--track-root-folder', type=str)
    parser.add_argument('-gpu', '--gpu', type=int, default=0)
    return parser


def parse_waymo(tfrecord_files, parsers_names, **kwargs):
    context = Context(tfrecord_files=tfrecord_files, **kwargs)
    data_parsers = ParsersWrapper(parsers_names, WAYMO_PARSERS_REGISTRY, context)
    for i, tfrecord_file in tqdm(list(enumerate(tfrecord_files))):
        dataset = list(tf.data.TFRecordDataset(tfrecord_file, compression_type=''))
        context.update(tfrecord_file=tfrecord_file, last_tfrecord_file=(i==len(tfrecord_files)-1), new_tfrecord_file=True)
        for j, data in tqdm(list(enumerate(dataset))):
            frame = open_dataset.Frame()
            frame.ParseFromString(bytearray(data.numpy()))
            context.update(frame=frame, last_frame=(j==len(dataset)-1), new_frame=True)
            for k, image_data in enumerate(frame.images):
                context.update(image_data=image_data, last_image=(k==len(frame.images)-1))
                data_parsers.parse(context)
                context.update(new_tfrecord_file=False, new_frame=False)
    return data_parsers


def find_files(paths, extensions=None):
    def check_extension(file_name, extensions):
        if extensions is None:
            return True
        ext = os.path.splitext(file_name)[1]
        if ext in extensions:
            return True
        else:
            return False

    found_files = list()
    for path in paths:
        if os.path.isfile(path):
            if check_extension(path, extensions):
                found_files.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for _file in files:
                    if check_extension(_file, extensions):
                        found_files.append(os.path.join(root, _file))
        else:
            raise RuntimeError('Path {} does not exist'.format(path))
    return found_files


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    if args.images_root_folder is None:
        args.images_root_folder = args.out_images_folder
    kwargs = vars(args)
    data_paths = kwargs.pop('data_paths')
    parsers_names = kwargs.pop('parsers_names')
    out_files = kwargs.pop('out_files')
    gpu = kwargs.pop('gpu')
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu)
    tfrecord_files = find_files(data_paths, ['.tfrecord'])
    data_parsers = parse_waymo(tfrecord_files, parsers_names, **kwargs)
    data_parsers.save(out_files, Context(tfrecord_files=tfrecord_files, **kwargs))

