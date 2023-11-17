# Copyright (c) OpenMMLab. All rights reserved.
import torch
import torch.nn as nn
import torch.nn.functional as F

from mmseg.core import add_prefix
from mmseg.ops import resize
from .. import builder
from ..builder import SEGMENTORS
from .base import BaseSegmentor

import numpy as np
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
from dataclasses import dataclass
import pandas as pd
from scipy import stats as scipy_stats
@dataclass
class UniformDistributionTest:
    # Code borrowed from: https://stats.stackexchange.com/questions/547841/test-for-uniformity-in-python
    """
    Test if the passed series is uniformly distributed using different tests.

    returns
        - True if test pass,
        - False if test fails,
        - None if test can not be performed
    """

    s: pd.Series = None
    result: dict = None
    default_significance_level: float = 0.1
    expected_min: float = None
    expected_max: float = None
    scale_factor: float = None

    def kolmogorov_smirnov_uniformity_test(self, low: float = None, high: float = None):
        low = low or self.expected_min
        high = high or self.expected_max
        # Using the parameters loc and scale, one obtains the uniform distribution on [loc, loc + scale].
        _stats, p = scipy_stats.kstest(self.s, scipy_stats.uniform(loc=low, scale=high - low).cdf)
        return p, p > self.default_significance_level

    def chi_square_uniformity_test(self):
        pass


@SEGMENTORS.register_module()
class EncoderDecoder(BaseSegmentor):
    """Encoder Decoder segmentors.

    EncoderDecoder typically consists of backbone, decode_head, auxiliary_head.
    Note that auxiliary_head is only used for deep supervision during training,
    which could be dumped during inference.
    """

    def __init__(self,
                 backbone,
                 decode_head,
                 neck=None,
                 auxiliary_head=None,
                 train_cfg=None,
                 test_cfg=None,
                 pretrained=None,
                 init_cfg=None):
        super(EncoderDecoder, self).__init__(init_cfg)
        if pretrained is not None:
            assert backbone.get('pretrained') is None, \
                'both backbone and segmentor set pretrained weight'
            backbone.pretrained = pretrained
        self.backbone = builder.build_backbone(backbone)
        if neck is not None:
            self.neck = builder.build_neck(neck)
        self._init_decode_head(decode_head)
        self._init_auxiliary_head(auxiliary_head)

        self.train_cfg = train_cfg
        self.test_cfg = test_cfg

        assert self.with_decode_head

    def _init_decode_head(self, decode_head):
        """Initialize ``decode_head``"""
        self.decode_head = builder.build_head(decode_head)
        self.align_corners = self.decode_head.align_corners
        self.num_classes = self.decode_head.num_classes
        self.out_channels = self.decode_head.out_channels

    def _init_auxiliary_head(self, auxiliary_head):
        """Initialize ``auxiliary_head``"""
        if auxiliary_head is not None:
            if isinstance(auxiliary_head, list):
                self.auxiliary_head = nn.ModuleList()
                for head_cfg in auxiliary_head:
                    self.auxiliary_head.append(builder.build_head(head_cfg))
            else:
                self.auxiliary_head = builder.build_head(auxiliary_head)
    
    def extract_feat(self, img):
        """Extract features from images."""
        x = self.backbone(img)
        if self.with_neck:
            x = self.neck(x)
        return x
    
    def encode_decode(self, img, img_metas):
        """Encode images with backbone and decode into a semantic segmentation
        map of the same size as input."""
        x = self.extract_feat(img)    
        out = self._decode_head_forward_test(x, img_metas)
        out = resize(
            input=out,
            size=img.shape[2:],
            mode='bilinear',
            align_corners=self.align_corners)
        return out

    def _decode_head_forward_train(self, x, img_metas, gt_semantic_seg):
        """Run forward function and calculate loss for decode head in
        training."""
        losses = dict()
        loss_decode = self.decode_head.forward_train(x, img_metas,
                                                     gt_semantic_seg,
                                                     self.train_cfg)

        losses.update(add_prefix(loss_decode, 'decode'))
        return losses

    def _decode_head_forward_test(self, x, img_metas):
        """Run forward function and calculate loss for decode head in
        inference."""
        seg_logits = self.decode_head.forward_test(x, img_metas, self.test_cfg)
        return seg_logits

    def _auxiliary_head_forward_train(self, x, img_metas, gt_semantic_seg):
        """Run forward function and calculate loss for auxiliary head in
        training."""
        losses = dict()
        if isinstance(self.auxiliary_head, nn.ModuleList):
            for idx, aux_head in enumerate(self.auxiliary_head):
                loss_aux = aux_head.forward_train(x, img_metas,
                                                  gt_semantic_seg,
                                                  self.train_cfg)
                losses.update(add_prefix(loss_aux, f'aux_{idx}'))
        else:
            loss_aux = self.auxiliary_head.forward_train(
                x, img_metas, gt_semantic_seg, self.train_cfg)
            losses.update(add_prefix(loss_aux, 'aux'))

        return losses

    def forward_dummy(self, img):
        """Dummy forward function."""
        seg_logit = self.encode_decode(img, None)

        return seg_logit

    def forward_train(self, img, img_metas, gt_semantic_seg):
        """Forward function for training.

        Args:
            img (Tensor): Input images.
            img_metas (list[dict]): List of image info dict where each dict
                has: 'img_shape', 'scale_factor', 'flip', and may also contain
                'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'.
                For details on the values of these keys see
                `mmseg/datasets/pipelines/formatting.py:Collect`.
            gt_semantic_seg (Tensor): Semantic segmentation masks
                used if the architecture supports semantic segmentation task.

        Returns:
            dict[str, Tensor]: a dictionary of loss components
        """

        x = self.extract_feat(img)

        losses = dict()

        loss_decode = self._decode_head_forward_train(x, img_metas,
                                                      gt_semantic_seg)
        losses.update(loss_decode)

        if self.with_auxiliary_head:
            loss_aux = self._auxiliary_head_forward_train(
                x, img_metas, gt_semantic_seg)
            losses.update(loss_aux)

        return losses

    # TODO refactor
    def slide_inference(self, img, img_meta, rescale):
        """Inference by sliding-window with overlap.

        If h_crop > h_img or w_crop > w_img, the small patch will be used to
        decode without padding.
        """

        h_stride, w_stride = self.test_cfg.stride
        h_crop, w_crop = self.test_cfg.crop_size
        batch_size, _, h_img, w_img = img.size()
        out_channels = self.out_channels
        h_grids = max(h_img - h_crop + h_stride - 1, 0) // h_stride + 1
        w_grids = max(w_img - w_crop + w_stride - 1, 0) // w_stride + 1
        preds = img.new_zeros((batch_size, out_channels, h_img, w_img))
        count_mat = img.new_zeros((batch_size, 1, h_img, w_img))
        for h_idx in range(h_grids):
            for w_idx in range(w_grids):
                y1 = h_idx * h_stride
                x1 = w_idx * w_stride
                y2 = min(y1 + h_crop, h_img)
                x2 = min(x1 + w_crop, w_img)
                y1 = max(y2 - h_crop, 0)
                x1 = max(x2 - w_crop, 0)
                crop_img = img[:, :, y1:y2, x1:x2]
                crop_seg_logit = self.encode_decode(crop_img, img_meta)
                preds += F.pad(crop_seg_logit,
                               (int(x1), int(preds.shape[3] - x2), int(y1),
                                int(preds.shape[2] - y2)))

                count_mat[:, :, y1:y2, x1:x2] += 1
        assert (count_mat == 0).sum() == 0
        if torch.onnx.is_in_onnx_export():
            # cast count_mat to constant while exporting to ONNX
            count_mat = torch.from_numpy(
                count_mat.cpu().detach().numpy()).to(device=img.device)
        preds = preds / count_mat
        if rescale:
            # remove padding area
            resize_shape = img_meta[0]['img_shape'][:2]
            preds = preds[:, :, :resize_shape[0], :resize_shape[1]]
            preds = resize(
                preds,
                size=img_meta[0]['ori_shape'][:2],
                mode='bilinear',
                align_corners=self.align_corners,
                warning=False)
        return preds

    def whole_inference(self, img, img_meta, rescale):
        """Inference with full image."""

        seg_logit = self.encode_decode(img, img_meta)
        if rescale:
            # support dynamic shape for onnx
            if torch.onnx.is_in_onnx_export():
                size = img.shape[2:]
            else:
                # remove padding area
                resize_shape = img_meta[0]['img_shape'][:2]
                seg_logit = seg_logit[:, :, :resize_shape[0], :resize_shape[1]]
                size = img_meta[0]['ori_shape'][:2]
            seg_logit = resize(
                seg_logit,
                size=size,
                mode='bilinear',
                align_corners=self.align_corners,
                warning=False)

        return seg_logit

    def inference(self, img, img_meta, rescale):
        """Inference with slide/whole style.

        Args:
            img (Tensor): The input image of shape (N, 3, H, W).
            img_meta (dict): Image info dict where each dict has: 'img_shape',
                'scale_factor', 'flip', and may also contain
                'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'.
                For details on the values of these keys see
                `mmseg/datasets/pipelines/formatting.py:Collect`.
            rescale (bool): Whether rescale back to original shape.

        Returns:
            Tensor: The output segmentation map.
        """

        assert self.test_cfg.mode in ['slide', 'whole']
        ori_shape = img_meta[0]['ori_shape']
        assert all(_['ori_shape'] == ori_shape for _ in img_meta)
        if self.test_cfg.mode == 'slide':
            seg_logit = self.slide_inference(img, img_meta, rescale)
        else:
            seg_logit = self.whole_inference(img, img_meta, rescale)
        if self.out_channels == 1:
            output = F.sigmoid(seg_logit)
        else:
            output = F.softmax(seg_logit, dim=1)
        flip = img_meta[0]['flip']
        if flip:
            flip_direction = img_meta[0]['flip_direction']
            assert flip_direction in ['horizontal', 'vertical']
            if flip_direction == 'horizontal':
                output = output.flip(dims=(3, ))
            elif flip_direction == 'vertical':
                output = output.flip(dims=(2, ))

        return output
    
    def simple_test(self, img, img_meta, rescale=True, threshold=0.5,
                    coarse_fine_predictions=True,
                    ):
                      
        """Simple test with single image."""
                      
        seg_logit = self.inference(img, img_meta, rescale)

        if self.out_channels == 1:
            seg_pred = (seg_logit >
                        self.decode_head.threshold).to(seg_logit).squeeze(1)
        else:
            seg_pred = seg_logit.argmax(dim=1)

        # NOTE: ADDED CODE PART OF THIS CVPR2024 WORK ~ this is the threshold to output probability to create the pseudolabels in selftraining
        # Current default value is set to 0.5 so only probability of 50% is stored as pixel label output. This needs to be passed as a flag to indicate required threshold value
        thresh_mask = np.zeros((seg_logit.shape[2], seg_logit.shape[3])).astype(np.uint8)
        # This returns the selected max values by argmax
        seg_val = seg_logit.max(dim=1).values[0].cpu().detach().numpy()
        thresh_mask[seg_val > threshold] = 1
        seg_pred[0][thresh_mask == 0] = 255
        
        # NOTE: ADDED CODE ~ Computing aggregated coarse & fine-grained maps at inference stage.
        # Two outputs are obtained: fine & coarse
        if coarse_fine_predictions == True:

            no_classes = 81

            # Lists of class hierarchy correspondences:      
            non_hier_class = [0, 4, 5, 42, 51, 52, 64, 67, 77, 78]
            lead_hier_class = [1, 2, 3, 7, 14, 15, 28, 29, 31, 34, 41, 47, 58, 60, 61, 65, 71]
            sub_hier_class = [6, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 32, 33, 35, 36, 37, 38,
                               39, 40, 41, 43, 44, 45, 46, 47, 48, 49, 50, 53, 54, 55, 56, 57, 59, 62, 63, 66,
                               68, 69, 70, 72, 73, 74, 75, 76, 79, 80]

            class_hierarchy_map = {
                0: 0,  # 'windows': 'windows'
                1: [18, 19, 43, 44],  # 'duct':'duct'
                2: [16, 17, 62, 73],  # 'pipe':'pipe'
                3: [20, 21, 22, 23, 24, 25, 26, 27, 79, 80],  # 'wall':'wall'
                4: 4,  # 'objects':'objects'
                5: 5,  # 'sky':'sky'
                7: [6, 7],  # 'person:other':'person'
                14: [8, 9, 10, 11, 12, 13, 14, 32, 33, 70],  # 'ceiling':'ceiling'
                15: [15,53,54,55,56,57],  # 'floor':'floor'
                28: [68, 74, 75, 76],
                29: [29, 30],
                31: [31,36],
                34: [34, 35],
                41: [37,38,39,40,41],
                42: 42,
                47: [45,46,47,48,49,50],
                51: 51,
                52: 52,
                58: [58,59],
                60: [60,63],
                61: [61, 69],
                64: 64,
                65: [65, 66],
                67: 67,
                71: [71, 72],
                77: 77,
                78: 78
            }

            # Create the coarse logit probability map
            seg_logit_coarse = torch.zeros((1, no_classes, seg_logit.shape[2], seg_logit.shape[3]), device=seg_logit.device)
            # Non hierarchical labels
            seg_logit_coarse[:, non_hier_class, :, :] = seg_logit[:, non_hier_class, :, :]

            # Hierarchical labels
            for i in lead_hier_class:
                seg_logit_coarse[:, i, :, :] = torch.sum(seg_logit[:, class_hierarchy_map[i], :, :], dim=1, keepdim=True) + seg_logit[:, i, :, :]
                
            # Coarse output
            seg_pred_coarse = seg_logit_coarse.argmax(dim=1)

            # Create the fine logit probabillity map based on the argmax selection in seg_pred_coarse
            # E.g. if coarse argmax = duct, possible classes to choose are now duct:insulated & duct:uninsulated
            # Base prediction for fine-grained based on the coarse_prediction
            seg_pred_fine = torch.clone(seg_pred_coarse).to(seg_logit.device)
            
            # If none of the predicted classes are in the hierarchical representation, add a single pixel with a hier class for the sake of continuing the loop
            non_hier_indicator = 0
            for val in torch.unique(seg_pred_fine):
                if val in non_hier_class:
                    non_hier_indicator += 1
            if non_hier_indicator == len(torch.unique(seg_pred_fine)):
                seg_pred_fine[0,0,0] = 6
            
            for class_pred in range(0, no_classes):  # parsing through all 81 classes
                if class_pred in non_hier_class:  # if current class is in the non_hier_class list, then keep the original values
                    continue

                if class_pred in sub_hier_class:  # if current class is in the sub_hier_class list, then ignore, as it will be dictated by the class mapping
                    continue

                if class_pred in lead_hier_class:  # only compute the subclasses when working on a lead_hier_class
                    # thanks to the sorting of our classes, we can leverage continuous indexes to contain all subclasses of a coarse class
                    bottom_idx = np.min(class_hierarchy_map[class_pred])
                    top_idx = np.max(class_hierarchy_map[class_pred])

                    if len(seg_pred_fine[seg_pred_fine == class_pred]) == 0:
                        continue
                    else:
                        mask = torch.where(seg_pred_fine == class_pred, 1, 0)
                        sub_class_results = seg_logit[:, bottom_idx:top_idx+1, :, :].argmax(dim=1) + bottom_idx
                        seg_pred_fine[mask.to(torch.bool)] = sub_class_results[mask.to(torch.bool)]
                      
            if torch.onnx.is_in_onnx_export():
                # our inference backend only support 4D output
                seg_pred = seg_pred.unsqueeze(0)
                seg_pred_coarse = seg_pred_coarse.unsqueeze(0)
                seg_pred_fine = seg_pred_fine.unsqueeze(0)
              
                return seg_pred, seg_pred_coarse, seg_pred_fine

            seg_pred = seg_pred.cpu().numpy()
            seg_pred_coarse = seg_pred_coarse.cpu().numpy()
            seg_pred_fine = seg_pred_fine.cpu().numpy()
            
          # unravel batch dim
            seg_pred = list(seg_pred)
            seg_pred_coarse = list(seg_pred_coarse)
            seg_pred_fine = list(seg_pred_fine)
          
            return seg_pred, seg_pred_coarse, seg_pred_fine
        # END ADDED CODE

        else:
            if torch.onnx.is_in_onnx_export():
                # our inference backend only support 4D output
                seg_pred = seg_pred.unsqueeze(0)
                return seg_pred
            seg_pred = seg_pred.cpu().numpy()
            # unravel batch dim
            seg_pred = list(seg_pred)
            return seg_pred
            

    def simple_test_logits(self, img, img_metas, rescale=True):
        """Test without augmentations.

        Return numpy seg_map logits.
        """
        seg_logit = self.inference(img[0], img_metas[0], rescale)
        seg_logit = seg_logit.cpu().numpy()
        return seg_logit

    def aug_test(self, imgs, img_metas, rescale=True):
        """Test with augmentations.

        Only rescale=True is supported.
        """
        # aug_test rescale all imgs back to ori_shape for now
        assert rescale
        # to save memory, we get augmented seg logit inplace
        seg_logit = self.inference(imgs[0], img_metas[0], rescale)
        for i in range(1, len(imgs)):
            cur_seg_logit = self.inference(imgs[i], img_metas[i], rescale)
            seg_logit += cur_seg_logit
        seg_logit /= len(imgs)
        if self.out_channels == 1:
            seg_pred = (seg_logit >
                        self.decode_head.threshold).to(seg_logit).squeeze(1)
        else:
            seg_pred = seg_logit.argmax(dim=1)
        seg_pred = seg_pred.cpu().numpy()
        # unravel batch dim
        seg_pred = list(seg_pred)
        return seg_pred

    def aug_test_logits(self, img, img_metas, rescale=True):
        """Test with augmentations.

        Return seg_map logits. Only rescale=True is supported.
        """
        # aug_test rescale all imgs back to ori_shape for now
        assert rescale

        imgs = img
        seg_logit = self.inference(imgs[0], img_metas[0], rescale)
        for i in range(1, len(imgs)):
            cur_seg_logit = self.inference(imgs[i], img_metas[i], rescale)
            seg_logit += cur_seg_logit

        seg_logit /= len(imgs)
        seg_logit = seg_logit.cpu().numpy()
        return seg_logit
