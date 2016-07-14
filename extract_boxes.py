import json


def polygon_to_enclosing_box(polygon):
    x_coords = [coord[0] for coord in polygon]
    y_coords = [coord[1] for coord in polygon]
    upper_left = [min(x_coords), min(y_coords)]
    lower_right = [max(x_coords), max(y_coords)]
    return [upper_left, lower_right]


def extract_min_annotation(page_annotation):
    props_to_keep = ['id', 'rectangle']
    min_annotation = {}
    for anno_type, annotations in page_annotation.items():
        for box_id, box_val in annotations.items():
            if anno_type == 'text':
                min_annotation[box_id] = {prop: box_val[prop] for prop in props_to_keep}
            elif anno_type == 'blobs':
                min_annotation[box_id] = {prop: box_val[prop] for prop in props_to_keep[:1]}
                bounding_rect = polygon_to_enclosing_box(box_val['polygon'])
                min_annotation[box_id]['rectangle'] = bounding_rect
    return min_annotation


def create_anno_for_tool(page_annotation):
    min_annotation = extract_min_annotation(page_annotation)

    for box_id, box_val in min_annotation.items():
        box_val['group_n'] = 0
        box_val['category'] = 'unlabeled'

    annotation_with_infrastructure = {}
    annotation_with_infrastructure['question'] = min_annotation

    return annotation_with_infrastructure


def write_annotations_for_tool(image_name, anno_dir='simpleAnnotations/', new_anno_dir='anno_w_infrastructure/'):
    anno_file = image_name + '.json'
    with open(anno_dir + anno_file) as f:
        page_annotations = json.load(f)

    anno_plus_infrastructure = create_anno_for_tool(page_annotations)

    with open(new_anno_dir + anno_file, 'w') as f:
        json.dump(anno_plus_infrastructure, f)

