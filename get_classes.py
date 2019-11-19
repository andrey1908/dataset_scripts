import xml.etree.ElementTree as xml
import json
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-file', '--file-name', type=str, required=True)
    parser.add_argument('-out', '--out-file', type=str)
    parser.add_argument('-sep', '--separator', type=str, default=' ')
    return parser


def get_classes_from_xml(xml_file, out_file=None, separator=' '):
    tree = xml.parse(xml_file)
    root = tree.getroot()
    labels = root.find('meta').find('task').find('labels')
    labels_names = list()
    for label in labels:
        labels_names.append(label.find('name').text)
    if out_file is not None:
        with open(out_file, 'w') as f:
            for label_name in labels_names:
                f.write(label_name + separator)
    return labels_names


def get_classes_from_json(json_file, out_file=None, separator=' '):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    categories = json_dict['categories']
    categories = list(zip(*sorted(zip([category['id'] for category in categories], categories))))[1]
    classes = list()
    for category in categories:
        classes.append(category['name'])
    if out_file is not None:
        with open(out_file, 'w') as f:
            for cl in classes:
                f.write(cl + separator)
    return classes


def get_classes(file_name, out_file=None, separator=' '):
    if file_name.endswith('.xml'):
        return get_classes_from_xml(file_name, out_file, separator)
    elif file_name.endswith('.json'):
        return get_classes_from_json(file_name, out_file, separator)
    else:
        print('Unrecognized format.')
    return None


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    labels_names = get_classes(**vars(args))
    for label_name in labels_names:
        print(label_name, end='\n')

