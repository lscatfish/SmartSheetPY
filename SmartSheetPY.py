import paddlex_hijack

"""调用一个a，避免idea把第一行优化删除"""
a = paddlex_hijack.a

import io
import os
import sys

os.system('chcp 65001')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8', line_buffering = True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding = 'utf-8', line_buffering = True)

from QingziClass.doqingziclass import DoQingziClass

qc = DoQingziClass()
qc.signforqcSheet()


# from paddleocr import PaddleOCR
#
# # 初始化 PaddleOCR 实例
# ocr = PaddleOCR(
#     use_doc_orientation_classify = False,
#     use_doc_unwarping = False,
#     use_textline_orientation = False)
#
# # 对示例图像执行 OCR 推理
# result = ocr.predict(
#     input = r"C:\Users\Sicheng Liu\.paddlex\predict_input\general_ocr_002.png")
#
# # 可视化结果并保存 json 结果
# for res in result:
#     res.print()
#     res.save_to_img("output")
#     res.save_to_json("output")

# from pathlib import Path
# from paddleocr import PPStructureV3
#
# pipeline = PPStructureV3(
#     use_doc_orientation_classify=False,
#     use_doc_unwarping=False
# )
#
# # For Image
# output = pipeline.predict(
#     input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/pp_structure_v3_demo.png",
#     )
#
# # 可视化结果并保存 json 结果
# for res in output:
#     res.print()
#     res.save_to_json(save_path="output")
#     res.save_to_markdown(save_path="output")


# p = "D:/code/SmartSheetPY/input/att_imgs/青社班1.jpeg"
#
# ocr= PPOCRImgByModel()
# ocr.predict(p)
# print(ocr.result_this)
