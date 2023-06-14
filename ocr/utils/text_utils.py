from CRAFT_pytorch.imgproc import resize_aspect_ratio, normalizeMeanVariance, cvt2HeatmapImg
from CRAFT_pytorch.craft_utils import getDetBoxes, adjustResultCoordinates

import torch
from torch.autograd import Variable
import numpy as np
import cv2
from PIL import Image

# test_net for CRAFT model
def test_net(net, image, text_threshold, link_threshold, low_text, poly, cuda=False, refine_net=None, canvas_size=1280, mag_ratio=1.5):
        # resize
        img_resized, target_ratio, _ = resize_aspect_ratio(image, canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=mag_ratio)
        ratio_h = ratio_w = 1 / target_ratio

        # preprocessing
        x = normalizeMeanVariance(img_resized)
        x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
        x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]
        if cuda:
            x = x.cuda()

        # forward pass
        with torch.no_grad():
            y, feature = net(x)

        # make score and link map
        score_text = y[0,:,:,0].cpu().data.numpy()
        score_link = y[0,:,:,1].cpu().data.numpy()

        # refine link
        if refine_net is not None:
            with torch.no_grad():
                y_refiner = refine_net(y, feature)
            score_link = y_refiner[0,:,:,0].cpu().data.numpy()

        # Post-processing
        boxes, polys = getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

        # coordinate adjustment
        boxes = adjustResultCoordinates(boxes, ratio_w, ratio_h)
        polys = adjustResultCoordinates(polys, ratio_w, ratio_h)
        for k in range(len(polys)):
            if polys[k] is None: polys[k] = boxes[k]

        # render results (optional)
        render_img = score_text.copy()
        render_img = np.hstack((render_img, score_link))
        ret_score_text = cvt2HeatmapImg(render_img)

        return boxes, polys, ret_score_text

# Get text bounding box from CRAFT
def get_text_bounding_box(img, net):
    if img.shape[0] == 2: img = img[0]
    if len(img.shape) == 2 : img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:   img = img[:,:,:3]
    img = np.array(img)

    text_threshold=0.7
    link_threshold=0.4
    low_text = 0.4
    poly = False
    refine_net = None

    boxes, _, _ = test_net(net, img, text_threshold, link_threshold, low_text, poly, refine_net)
    return boxes

# OCR
def ocr(img_array, detector):
    img_pil = Image.fromarray(img_array)
    s = detector.predict(img_pil)
    return s