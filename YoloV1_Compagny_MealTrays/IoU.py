import torch
from configparser import ConfigParser
import os, sys

current_folder = os.path.dirname(locals().get("__file__"))
config_file = os.path.join(current_folder, "config.ini")
sys.path.append(config_file)

config = ConfigParser()
config.read("config.ini")
S = config.getint("MODEL", "GRID_SIZE")

def relative2absolute(tensor)->torch.Tensor:
    """
    TODO

    Returns:
        box_prediction_absolute (torch.Tensor of shape (N,5))
            Contains the 4 predicted coordinates xmin, ymin, 
            xmax, ymax and confidence_score for each image.
    """
    assert len(tensor.shape) == 4, "Error: box_prediction is torch.Tensor of shape (N,S,S,_)"
    assert tensor.shape[-1] >= 4, "Error: box_prediction should contain a least one box -> (N,S,S,4+)"

    SIZEHW = 448
    CELL_SIZE = 1/S
    box = tensor.clone()
    
    ### xyrcell to xyr_img
    box[...,0] = box[...,0] * CELL_SIZE + torch.arange(0,S) * CELL_SIZE
    box[...,1] = box[...,1] * CELL_SIZE + torch.arange(0,S).reshape(S,1) * CELL_SIZE

    ### xyr_img to xy_abs
    box[...,0] = (box[...,0] - box[...,2]/2) * SIZEHW
    box[...,1] = (box[...,1] - box[...,3]/2) * SIZEHW

    ### whr_img to wh_abs
    box[...,2] = box[...,0] + box[...,2] * SIZEHW 
    box[...,3] = box[...,1] + box[...,3] * SIZEHW
    
    box[...,:4] = torch.floor(box[...,:4])

    return box


def intersection_over_union(box_1:torch.Tensor, box_2:torch.Tensor)->torch.Tensor:
    """
    Compute IoU between 2 boxes.
    Boxes should be [xmin, ymin, xmax, ymax, _] with absolute coordinates.

    Args:
        box_1 (torch.Tensor of shape (N,4))
        box_2 (torch.Tensor of shape (N,4))

    Return:
        iou (torch.Tensor of shape (N,1))
    """
    assert box_1.shape[-1] == 4, "Error: box_1 is torch.Tensor of shape (N,4)"
    assert box_2.shape[-1] == 4, "Error: box_2 is torch.Tensor of shape (N,4)"

    xmin_1, ymin_1, xmax_1, ymax_1 = box_1[:,:4].permute(1,0)
    xmin_2, ymin_2, xmax_2, ymax_2 = box_2[:,:4].permute(1,0)

    smoothing_factor = 1e-10
    zero = torch.Tensor([0])
    
    ### x, y overlaps btw 1 and 2
    xmin_overlap = torch.maximum(xmin_1, xmin_2)
    xmax_overlap = torch.minimum(xmax_1, xmax_2)
    ymin_overlap = torch.maximum(ymin_1, ymin_2)
    ymax_overlap = torch.minimum(ymax_1, ymax_2)

    ### Areas
    box_true_area = (xmax_1 - xmin_1) * (ymax_1 - ymin_1)
    box_pred_area = (xmax_2 - xmin_2) * (ymax_2 - ymin_2)

    ### Intersection area and union area
    overlap_area = torch.maximum((xmax_overlap - xmin_overlap), zero) * \
        torch.maximum((ymax_overlap - ymin_overlap), zero)
    union_area = (box_true_area + box_pred_area) - overlap_area
    
    ### Compute IoU
    iou = (overlap_area + smoothing_factor) / (union_area + smoothing_factor)
    return iou