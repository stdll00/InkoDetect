import pathlib
import random

import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import ops as utils_ops

TF_MODEL_PATH = "/tensorflow/"
# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile


def load_model(model_name):
    base_url = 'http://download.tensorflow.org/models/object_detection/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(
        fname=model_name,
        origin=base_url + model_file,
        untar=True)

    model_dir = pathlib.Path(model_dir) / "saved_model"

    model = tf.saved_model.load(str(model_dir))

    return model


PATH_TO_LABELS = TF_MODEL_PATH + 'models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
detection_model = load_model(model_name)


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    try:
        input_tensor = tf.convert_to_tensor(image)
    except ValueError:
        # sometimes not working.
        return
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                           tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def show_inference(image_np):
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    # image_np = np.array(Image.open(image_path))
    # Actual detection.

    output_dict = run_inference_for_single_image(detection_model, image_np)
    # Visualization of the results of a detection.
    if category_index[output_dict['detection_classes'][0]]['name'] != 'bird' \
            or output_dict['detection_scores'][0] < 0.5:
        if random.randint(0, 9) < 1:
            print(0, "          ", output_dict['detection_scores'][:5], output_dict['detection_classes'][:5])
        return 0
    if category_index[output_dict['detection_classes'][1]]['name'] != 'bird' \
            or output_dict['detection_scores'][1] < 0.5:
        print(1, output_dict['detection_scores'][1], output_dict['detection_scores'][:5],
              output_dict['detection_classes'][:5])
        return 1
    return 2

    # vis_util.visualize_boxes_and_labels_on_image_array(
    #     image_np,
    #     output_dict['detection_boxes'],
    #     output_dict['detection_classes'],
    #     output_dict['detection_scores'],
    #     category_index,
    #     instance_masks=output_dict.get('detection_masks_reframed', None),
    #     use_normalized_coordinates=True,
    #     line_thickness=8)
    #
    # display(Image.fromarray(image_np))
