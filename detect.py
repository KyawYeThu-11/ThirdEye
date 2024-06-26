import numpy as np
import cv2
import time
import tensorflow as tf

from yad2k.utils.utils import draw_boxes, get_colors_for_classes, scale_boxes, read_classes, read_anchors, preprocess_image
# from tensorflow.keras.models import load_model
from tensorflow.keras.layers import TFSMLayer
from yad2k.models.keras_yolo import yolo_head

# detect 80 classes and use 5 anchor boxes. 
class_names = read_classes("model_data/coco_classes.txt")
anchors = read_anchors("model_data/yolo_anchors.txt")
# The car detection dataset has 720x1280 images, which are pre-processed into 608x608 images to be the same as yolo_model input layer size
model_image_size = (608, 608) 
# yolo_model = load_model("model_data/", compile=False)
yolo_model = TFSMLayer("model_data/", call_endpoint="serving_default")


def yolo_filter_boxes(boxes, box_confidence, box_class_probs, threshold = 0.6):
    """Filters YOLO boxes by thresholding on object and class confidence.
    
    Arguments:
        boxes -- tensor of shape (19, 19, 5, 4)
        box_confidence -- tensor of shape (19, 19, 5, 1)
        box_class_probs -- tensor of shape (19, 19, 5, 80)
        threshold -- real value, if [ highest class probability score < threshold],
                     then get rid of the corresponding box

    Returns:
        scores -- tensor of shape (None,), containing the class probability score for selected boxes
        boxes -- tensor of shape (None, 4), containing (b_x, b_y, b_h, b_w) coordinates of selected boxes
        classes -- tensor of shape (None,), containing the index of the class detected by the selected boxes

    Note: "None" is here because you don't know the exact number of selected boxes, as it depends on the threshold. 
    For example, the actual output size of scores would be (10,) if there are 10 boxes.
    """
    box_scores = box_confidence * box_class_probs
    # box_scores.shape = (19, 19, 5, 80)

    box_classes = tf.math.argmax(box_scores, axis=-1)
    box_class_scores = tf.math.reduce_max(box_scores, axis=-1)

    filtering_mask = box_class_scores >= threshold

    scores = tf.boolean_mask(box_class_scores, filtering_mask, axis=None)
    boxes = tf.boolean_mask(boxes, filtering_mask, axis=None)
    classes = tf.boolean_mask(box_classes, filtering_mask, axis=None)
    # scores.shape = (1789,)
    # boxes.shape = (1789, 4)
    # classes.shape = (1789,)

    return scores, boxes, classes

def yolo_non_max_suppression(scores, boxes, classes, max_boxes = 10, iou_threshold = 0.5):
    """
    Applies Non-max suppression (NMS) to set of boxes
    
    Arguments:
    scores -- tensor of shape (None,), output of yolo_filter_boxes()
    boxes -- tensor of shape (None, 4), output of yolo_filter_boxes() that have been scaled to the image size (see later)
    classes -- tensor of shape (None,), output of yolo_filter_boxes()
    max_boxes -- integer, maximum number of predicted boxes you'd like
    iou_threshold -- real value, "intersection over union" threshold used for NMS filtering
    
    Returns:
    scores -- tensor of shape (None, ), predicted score for each box
    boxes -- tensor of shape (None, 4), predicted box coordinates
    classes -- tensor of shape (None, ), predicted class for each box
    
    Note: The "None" dimension of the output tensors has obviously to be less than max_boxes. Note also that this
    function will transpose the shapes of scores, boxes, classes. This is made for convenience.
    """
    nms_indices = tf.image.non_max_suppression(boxes, scores, max_boxes, iou_threshold)
    scores = tf.gather(scores, nms_indices)
    boxes = tf.gather(boxes, nms_indices)
    classes = tf.gather(classes, nms_indices)

    return scores, boxes, classes

def yolo_boxes_to_corners(box_xy, box_wh):
    """Convert YOLO box predictions to bounding box corners."""
    box_mins = box_xy - (box_wh / 2.)
    box_maxes = box_xy + (box_wh / 2.)

    return tf.keras.backend.concatenate([
        box_mins[..., 1:2],  # y_min
        box_mins[..., 0:1],  # x_min
        box_maxes[..., 1:2],  # y_max
        box_maxes[..., 0:1]  # x_max
    ])

def yolo_eval(yolo_outputs, image_shape = (720, 1280), max_boxes=10, score_threshold = 0.6, iou_threshold=0.5):
    """
    Converts the output of YOLO encoding (a lot of boxes) to your predicted boxes along with their scores, box coordinates and classes.
    
    Arguments:
    yolo_outputs -- output of the encoding model (for image_shape of (608, 608, 3)), contains 4 tensors:
                    box_xy: tensor of shape (None, 19, 19, 5, 2)
                    box_wh: tensor of shape (None, 19, 19, 5, 2)
                    box_confidence: tensor of shape (None, 19, 19, 5, 1)
                    box_class_probs: tensor of shape (None, 19, 19, 5, 80)
    image_shape -- tensor of shape (2,) containing the input shape, in this notebook we use (608., 608.) (has to be float32 dtype)
    max_boxes -- integer, maximum number of predicted boxes you'd like
    score_threshold -- real value, if [ highest class probability score < threshold], then get rid of the corresponding box
    iou_threshold -- real value, "intersection over union" threshold used for NMS filtering
    
    Returns:
    scores -- tensor of shape (None, ), predicted score for each box
    boxes -- tensor of shape (None, 4), predicted box coordinates
    classes -- tensor of shape (None,), predicted class for each box
    """
    box_xy, box_wh, box_confidence, box_class_probs = yolo_outputs

    boxes = yolo_boxes_to_corners(box_xy, box_wh)

    scores, boxes, classes = yolo_filter_boxes(boxes, box_confidence, box_class_probs, iou_threshold)

    boxes = scale_boxes(boxes, image_shape)

    scores, boxes, classes = yolo_non_max_suppression(scores, boxes, classes, max_boxes, iou_threshold)

    return scores, boxes, classes

def predict(numpy_image):
    """
    Runs the graph to predict boxes for "image_file". Prints and plots the predictions.
    
    Arguments:
    image_file -- name of an image stored in the "images" folder.
    
    Returns:
    out_scores -- tensor of shape (None, ), scores of the predicted boxes
    out_boxes -- tensor of shape (None, 4), coordinates of the predicted boxes
    out_classes -- tensor of shape (None, ), class index of the predicted boxes
    
    Note: "None" actually represents the number of predicted boxes, it varies between 0 and max_boxes. 
    """

    # Preprocess your image
    image, image_data = preprocess_image(numpy_image, model_image_size = (608, 608))
    
    yolo_model_outputs = yolo_model(image_data)
    
    # yolo_outputs = yolo_head(yolo_model_outputs, anchors, len(class_names))
    yolo_outputs = yolo_head(yolo_model_outputs['conv2d_22'], anchors, len(class_names))
        
    out_scores, out_boxes, out_classes = yolo_eval(yolo_outputs, [image.size[1],  image.size[0]], 10, 0.3, 0.5)

    # Generate colors for drawing bounding boxes.
    colors = get_colors_for_classes(len(class_names))

    # Draw bounding boxes on the image file
    output_image = draw_boxes(image, out_boxes, out_classes, class_names, out_scores)

    return output_image

### Implementation with pure openCV (only works in local) ###
def open_webcam():
    """Start capturing the video using the webcam and make predictions"""
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        start_time = time.perf_counter()
        ret, input_frame = cap.read()
        
        if not ret:
            break

        output_frame = predict(input_frame)
        end_time = time.perf_counter()
        fps = 1/np.round(end_time - start_time, 3)
        cv2.putText(output_frame, "Press Q to quick", (450, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (33, 80, 209), 1)
        cv2.putText(output_frame, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (27, 60, 133), 1)
        cv2.imshow("img", output_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()