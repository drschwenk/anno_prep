import json
import glob
import io
import PIL.Image as Image


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
            elif anno_type in ['blobs', 'arrows', 'backgroundBlobs']:
                min_annotation[box_id] = {prop: box_val[prop] for prop in props_to_keep[:1]}
                bounding_rect = polygon_to_enclosing_box(box_val['polygon'])
                min_annotation[box_id]['rectangle'] = bounding_rect
    return min_annotation


def create_anno_for_tool(page_annotation):
    min_annotation = extract_min_annotation(page_annotation)

    for box_id, box_val in min_annotation.items():
        box_val['group_n'] = [[0, 0]]
        box_val['category'] = ['unlabeled']

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


def load_local_annotation(page_name, anno_dir):
    """
    loads annotation from disk
    :return: annotation json
    """
    base_path = './'
    file_path = base_path + anno_dir + page_name.replace('jpeg', 'json')
    try:
        with open(file_path, 'r') as f:
            local_annotations = json.load(f)
    except IOError as e:
        print(e)
        local_annotations = None
    return local_annotations


def record_image_size(pdf_page_image):
    page_image = Image.open(io.BytesIO(pdf_page_image))
    img_dim = page_image.size
    return img_dim


def add_anno_img_dim(img_dir, image_files, source_annotation_folder, dest_annotation_folder):
    """
    Adds a field to the box annotations for the vertical dimension of the page image
    :param img_dir: dir to read images from and set dim
    :param source_annotation_folder dir to read source annotations from
    :param dest_annotation_folder: destination for the new annotation files
    :return: None
    """
    img_dim_lookup = {}
    for img_n in image_files:
        img = img_dir + img_n
        anno_file_name = img_n.replace('png', 'png.json')
        try:
            existing_annotations = load_local_annotation(anno_file_name, source_annotation_folder)
            with open(img) as f:
                h_dim, v_dim = record_image_size(f.read())
                img_dim_lookup[img_n] = (h_dim, v_dim)
            try:
                for box_name, box in existing_annotations['question'].items():
                    box['v_dim'] = v_dim
                    box['h_dim'] = h_dim
            except KeyError:
                print(img)
            # file_path = dest_annotation_folder + anno_file_name
            # with open(file_path, 'wb') as f:
            #     json.dump(existing_annotations, f)
        except IOError as e:
            print(e)

    return img_dim_lookup

