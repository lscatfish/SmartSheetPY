# -*- coding: utf-8 -*-
"""输入输出功能"""
import os

import cv2
import numpy as np
from PIL import Image


def read_img(path):
    """读取图像并转换为OpenCV格式"""
    try:
        pil_img = Image.open(path)
        img_array = np.array(pil_img)
        if len(img_array.shape) == 3:
            image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            image = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        return image
    except Exception as e:
        # print(f"读取图像错误: {e}")
        return None


def write_img(img_cv, path):
    """保存OpenCV图像"""
    try:
        # 转换通道顺序：BGR → RGB
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        # 转换为PIL的Image对象
        img_pil = Image.fromarray(img_rgb)
        # 保存图像
        img_pil.save(path)
        return os.path.exists(path)
    except Exception as e:
        # print(f"保存图像错误: {e}")
        return False
