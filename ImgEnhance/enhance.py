"""增强效果"""
import dataclasses
from typing import Any

import cv2
import numpy as np

from ImgEnhance.iofunc import read_img, write_img


class SentinelAny:
    """哨兵值"""
    pass


def overwrite_dict(mask: dict[str, Any], base: dict[str, Any], exclude: type | None = SentinelAny):
    """
    Args:
        mask:覆写字典
        base:基础字典
        exclude:排除方法
    """
    for mask_key, mask_value in mask.items():
        if exclude is None:
            if mask_value is not None:
                base[mask_key] = mask_value
            continue
        else:
            if not isinstance(mask_value, exclude):
                base[mask_key] = mask_value
            continue


class BaseImageEnhancement:
    """此模块用于管理图像增强，基类"""

    @dataclasses.dataclass
    class PipeData:
        img: cv2.Mat
        shadow_remove_method: str
        shadow_remove_method_args: tuple | dict
        sharpen_method: str
        sharpen_method_args: tuple | dict
        enhance_contrast: bool
        enhance_contrast_args: tuple | dict
        enhance_saturation: bool
        enhance_saturation_args: tuple | dict
        white_balance: bool
        white_balance_args: tuple | dict

    def __init__(
        self,
        shadow_remove_method: str = 'morphology',
        shadow_remove_method_args: tuple | dict = (9, 3),
        sharpen_method: str = 'unsharp_mask',
        sharpen_method_args: tuple | dict = ((5, 5), 1.0, 1.5),
        enhance_contrast = True,
        enhance_contrast_args: tuple | dict = (1.2, 5),
        enhance_saturation = True,
        enhance_saturation_args: tuple | dict = (1.1,),
        white_balance = True,
        white_balance_args: tuple | dict = None, ):
        """"""
        params = locals().copy()
        params.pop('self')
        self._params = params

    def enhance(
        self,
        img: str | np.ndarray = None,
        shadow_remove_method: str = None,
        shadow_remove_method_args: tuple | dict = None,
        sharpen_method: str = None,
        sharpen_method_args: tuple | dict = None,
        enhance_contrast = None,
        enhance_contrast_args: tuple | dict = None,
        enhance_saturation = None,
        enhance_saturation_args: tuple | dict = None,
        white_balance = None,
        white_balance_args: tuple | dict = None,
        *args, **kwargs):
        params = locals().copy()
        params.pop('self')
        params.pop('args')
        params.pop('kwargs')

        if img is None:
            raise Exception('Image cannot be None！')
        elif isinstance(img, str):
            self._params['img'] = read_img(img)
            params.pop('img')
        elif isinstance(img, np.ndarray):
            try:
                if len(img.shape) == 3:
                    self._params['img'] = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                else:
                    self._params['img'] = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            except Exception as e:
                print(f"读取图像错误: {e}")
                # 非禁用方式会使得窗口崩溃
            params.pop('img')
        else:
            raise Exception('Image must be np.ndarray or str')

        overwrite_dict(params, self._params, None)
        self._pipeline(**self._params)  # 解包传递
        pass

    def _pipeline(self, *args, **kwargs):
        """产线方法"""
        img: cv2.Mat = self._params['img'].copy()
        pipe = self.PipeData(**self._params)

        if pipe.shadow_remove_method == 'morphology':
            if isinstance(pipe.shadow_remove_method_args, dict):
                img = self.remove_shadow_morphology(img, **pipe.shadow_remove_method_args)
            elif isinstance(pipe.shadow_remove_method_args, tuple):
                img = self.remove_shadow_morphology(img, *pipe.shadow_remove_method_args)
        elif pipe.shadow_remove_method == 'hsv':
            if isinstance(pipe.shadow_remove_method_args, dict):
                img = self.remove_shadow_hsv(img, **pipe.shadow_remove_method_args)
            elif isinstance(pipe.shadow_remove_method_args, tuple):
                img = self.remove_shadow_hsv(img, *pipe.shadow_remove_method_args)

        if pipe.sharpen_method == 'unsharp_mask':
            if isinstance(pipe.sharpen_method_args, dict):
                img = self.unsharp_masking(img, **pipe.sharpen_method_args)
            elif isinstance(pipe.sharpen_method_args, tuple):
                img = self.unsharp_masking(img, *pipe.sharpen_method_args)
        elif pipe.sharpen_method == 'laplacian':
            if isinstance(pipe.sharpen_method_args, dict):
                img = self.sharpen_image_laplacian(img, **pipe.sharpen_method_args)
            elif isinstance(pipe.sharpen_method_args, tuple):
                img = self.sharpen_image_laplacian(img, *pipe.sharpen_method_args)
        elif pipe.sharpen_method == 'filter2d':
            if isinstance(pipe.sharpen_method_args, dict):
                img = self.sharpen_image_filter2d(img, **pipe.sharpen_method_args)
            elif isinstance(pipe.sharpen_method_args, tuple):
                img = self.sharpen_image_filter2d(img, *pipe.sharpen_method_args)

        if pipe.enhance_contrast:
            if isinstance(pipe.enhance_contrast_args, dict):
                img = self.adjust_contrast_brightness(img, **pipe.enhance_contrast_args)
            elif isinstance(pipe.enhance_contrast_args, tuple):
                img = self.adjust_contrast_brightness(img, *pipe.enhance_contrast_args)

        if pipe.enhance_saturation:
            if isinstance(pipe.enhance_saturation_args, dict):
                img = self.adjust_saturation(img, **pipe.enhance_saturation_args)
            elif isinstance(pipe.enhance_saturation_args, tuple):
                img = self.adjust_saturation(img, *pipe.enhance_saturation_args)

        if pipe.white_balance:
            img = self.auto_white_balance(img)

        return img

    @staticmethod
    def sharpen_image_laplacian(image, kernel_size = 3, scale = 0.03):
        """
        使用拉普拉斯算子进行图像锐化
        参数:
            image: 输入图像(BGR格式)
            kernel_size: 拉普拉斯核大小(1,3,5,7)
            scale: 计算值的可选比例因子
        返回:
            锐化后的图像
        """
        if kernel_size not in [1, 3, 5, 7]:
            kernel_size = 3

        # 转换为灰度图进行处理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 计算拉普拉斯变换
        laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize = kernel_size, scale = scale)
        laplacian_8u = cv2.convertScaleAbs(laplacian)

        # 将8位拉普拉斯图像转换为BGR
        laplacian_bgr = cv2.cvtColor(laplacian_8u, cv2.COLOR_GRAY2BGR)

        # 将拉普拉斯图像加到原始图像上
        sharpened = cv2.addWeighted(image, 1, laplacian_bgr, 1.5, 0)
        return sharpened

    @staticmethod
    def sharpen_image_filter2d(image, kernel_type = 'standard'):
        """
        使用自定义卷积核进行图像锐化
        参数:
            image: 输入图像
            kernel_type: 卷积核类型 ('standard', 'strong')
        返回:
            锐化后的图像
        """
        if kernel_type == 'standard':
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])
        elif kernel_type == 'strong':
            kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
        else:
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])

        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened


    @staticmethod
    def unsharp_masking(image, kernel_size = (5, 5), sigma = 1.0, strength = 1.5):
        """
        使用反锐化掩模(Unsharp Masking)进行锐化
        参数:
            image: 输入图像
            kernel_size: 高斯核大小
            sigma: 高斯核标准差
            strength: 锐化强度
        返回:
            锐化后的图像
        """
        # 高斯模糊
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)

        # 反锐化掩模
        sharpened = cv2.addWeighted(image, 1 + strength, blurred, -strength, 0)
        return sharpened


    @staticmethod
    def remove_shadow_morphology(image, iteration = 9, kernel_size = 3):
        """
        使用形态学方法去除阴影
        参数:
            image: 输入图像(BGR格式)
            iteration: 形态学操作迭代次数
            kernel_size: 结构元素大小
        返回:
            去除阴影后的图像
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 定义结构元素
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))

        # 闭运算操作
        close_mat = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, element, iterations = iteration)

        # 闭运算后的图减去原灰度图再取反
        calc_mat = ~(close_mat - gray)

        # 归一化处理
        remove_shadow_mat = cv2.normalize(calc_mat, None, 0, 200, cv2.NORM_MINMAX)

        # 如果是彩色图像，需要将结果转换回BGR
        if len(image.shape) == 3:
            remove_shadow_mat = cv2.cvtColor(remove_shadow_mat, cv2.COLOR_GRAY2BGR)

        return remove_shadow_mat


    @staticmethod
    def remove_shadow_hsv(image, saturation_thresh = 35, value_thresh = 45):
        """
        使用HSV颜色空间方法去除阴影
        参数:
            image: 输入图像(BGR格式)
            saturation_thresh: 饱和度阈值
            value_thresh: 明度阈值
        返回:
            去除阴影后的图像
        """
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 分离HSV通道
        h, s, v = cv2.split(hsv)

        # 阴影检测（低饱和度和低明度区域）
        shadow_mask = ((s < saturation_thresh) & (v < value_thresh)).astype(np.uint8) * 255

        # 形态学操作去除噪声
        kernel = np.ones((5, 5), np.uint8)
        shadow_mask = cv2.morphologyEx(shadow_mask, cv2.MORPH_CLOSE, kernel)

        # 使用图像修复来去除阴影
        result = cv2.inpaint(image, shadow_mask, inpaintRadius = 3, flags = cv2.INPAINT_TELEA)

        return result


    @staticmethod
    def adjust_contrast_brightness(image, contrast = 1.0, brightness = 0):
        """
        调整图像的对比度和亮度
        参数:
            image: 输入图像
            contrast: 对比度系数(>1增强，<1减弱)
            brightness: 亮度调整值
        返回:
            调整后的图像
        """
        adjusted = cv2.convertScaleAbs(image, alpha = contrast, beta = brightness)
        return adjusted


    @staticmethod
    def adjust_saturation(image, saturation_factor = 1.0):
        """
        调整图像饱和度
        参数:
            image: 输入图像(BGR格式)
            saturation_factor: 饱和度因子(>1增强，<1减弱)
        返回:
            调整后的图像
        """
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.float32)

        # 调整饱和度通道
        hsv[:, :, 1] = hsv[:, :, 1] * saturation_factor
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)

        # 转换回BGR
        hsv = hsv.astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return result


    @staticmethod
    def histogram_equalization_color(image):
        """
        彩色图像的直方图均衡化
        参数:
            image: 输入图像(BGR格式)
        返回:
            均衡化后的图像
        """
        # 转换到YUV颜色空间
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

        # 对Y通道进行直方图均衡化
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])

        # 转换回BGR颜色空间
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        return result


    @staticmethod
    def auto_white_balance(image):
        """
        自动白平衡
        参数:
            image: 输入图像
        返回:
            白平衡后的图像
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # 计算A和B通道的平均值
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])

        # 调整A和B通道
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)

        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result
