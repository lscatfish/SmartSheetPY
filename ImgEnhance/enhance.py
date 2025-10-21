"""增强效果"""
import cv2
import numpy as np

from .iofunc import read_img, write_img


class ImageEnhancement:
    """此模块用于管理图像增强"""

    def __init__(self, path, ):
        """"""

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