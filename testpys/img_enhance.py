import cv2
import numpy as np
import argparse
import os


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


def enhance_image_pipeline(
    image,
    shadow_removal_method = 'morphology',
    sharpen_method = 'unsharp_mask',
    enhance_contrast = True,
    enhance_saturation = True,
    white_balance = True):
    """
    图像增强综合流程
    参数:
        image: 输入图像
        shadow_removal_method: 阴影去除方法 ('morphology', 'hsv', 'none')
        sharpen_method: 锐化方法 ('laplacian', 'filter2d', 'unsharp_mask', 'none')
        enhance_contrast: 是否增强对比度
        enhance_saturation: 是否增强饱和度
        white_balance: 是否进行白平衡
    返回:
        增强后的图像
    """
    result = image.copy()

    # 1. 阴影去除
    if shadow_removal_method == 'morphology':
        result = remove_shadow_morphology(result)
    elif shadow_removal_method == 'hsv':
        result = remove_shadow_hsv(result)

    # 2. 锐化处理
    if sharpen_method == 'laplacian':
        result = sharpen_image_laplacian(result)
    elif sharpen_method == 'filter2d':
        result = sharpen_image_filter2d(result, 'standard')
    elif sharpen_method == 'unsharp_mask':
        result = unsharp_masking(result)

    # 3. 对比度增强
    if enhance_contrast:
        result = adjust_contrast_brightness(result, contrast = 1.2, brightness = 5)

    # 4. 饱和度增强
    if enhance_saturation:
        result = adjust_saturation(result, saturation_factor = 1.1)

    # 5. 白平衡
    if white_balance:
        result = auto_white_balance(result)

    return result


def main():
    """
    主函数：处理命令行参数并执行图像增强
    """
    parser = argparse.ArgumentParser(description = 'OpenCV图像增强脚本')
    parser.add_argument('input', help = '输入图像路径')
    parser.add_argument('-o', '--output', help = '输出图像路径')
    parser.add_argument('--sharpen', choices = ['laplacian', 'filter2d', 'unsharp_mask', 'none'],
        default = 'unsharp_mask', help = '锐化方法')
    parser.add_argument('--shadow', choices = ['morphology', 'hsv', 'none'],
        default = 'morphology', help = '阴影去除方法')
    parser.add_argument('--contrast', type = float, default = 1.2, help = '对比度增强系数')
    parser.add_argument('--brightness', type = int, default = 5, help = '亮度调整值')
    parser.add_argument('--saturation', type = float, default = 1.1, help = '饱和度增强系数')

    args = parser.parse_args()

    # 读取图像
    if not os.path.exists(args.input):
        print(f"错误：输入文件 '{args.input}' 不存在")
        return

    image = cv2.imread(args.input)
    if image is None:
        print(f"错误：无法读取图像文件 '{args.input}'")
        return

    print("开始处理图像...")

    # 使用综合流程处理图像
    enhanced_image = enhance_image_pipeline(
        image,
        shadow_removal_method = args.shadow,
        sharpen_method = args.sharpen,
        enhance_contrast = True,
        enhance_saturation = True,
        white_balance = True
    )

    # 保存或显示结果
    if args.output:
        cv2.imwrite(args.output, enhanced_image)
        print(f"处理完成！结果已保存至: {args.output}")
    else:
        # 显示原图和处理后的图像
        cv2.imshow('Original Image', image)
        cv2.imshow('Enhanced Image', enhanced_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# 使用示例函数
def example_usage():
    """
    示例使用方式
    """
    from ImgEnhance.iofunc import read_img, write_img
    # 读取图像
    image = read_img('12.jpg')

    # 方法1：单独使用各个功能
    # 去除阴影
    shadow_removed = remove_shadow_morphology(image)

    # 锐化图像
    sharpened = sharpen_image_laplacian(shadow_removed, 1)

    # 调整对比度和亮度
    contrast_adjusted = adjust_contrast_brightness(sharpened, contrast = 1.2, brightness = 10)

    # 增强饱和度
    final_result = adjust_saturation(contrast_adjusted, saturation_factor = 1.1)

    # 方法2：使用综合流程
    final_result_pipeline = enhance_image_pipeline(
        image,
        shadow_removal_method = 'morphology',
        sharpen_method = 'unsharp_mask',
        enhance_contrast = True,
        enhance_saturation = True,
        white_balance = True
    )

    # 保存结果
    write_img(path = 'enhanced_image.jpg', img_cv = final_result_pipeline)


if __name__ == "__main__":
    # 如果直接运行脚本，执行主函数
    # main()

    # 取消注释以下行来测试示例使用
    example_usage()
