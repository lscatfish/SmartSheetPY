import io
import os
import sys




os.system('chcp 65001')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8', line_buffering = True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding = 'utf-8', line_buffering = True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PADDLE_PDX_CACHE_HOME'] = BASE_DIR

import os, pathlib
from paddlex.inference.utils.official_models import _ModelManager, _BosModelHoster
from paddlex.utils import logging

logging.debug = True      # 打开 DEBUG

# 1. 本地镜像根目录（自己维护）
PRIVATE_MIRROR = pathlib.Path(os.path.join(BASE_DIR, 'official_models'))

# 3. 兜底下载器（复用官方 BOS 源）
_bos_hoster = _BosModelHoster(PRIVATE_MIRROR)

# 2. 彻底替换 _get_model_local_path：永远不走 hoster
def _offline_get_model_local_path(self, model_name):
    local_dir = PRIVATE_MIRROR / model_name
    if local_dir.exists():
        return local_dir
    # ② 镜像缺失 → 走官方下载（会自动保存到 CACHE_DIR）
    #logging.info(f'本地镜像缺失，正在从官方源下载 {model_name} …')
    return _bos_hoster.get_model(model_name)  # 会调用 _download → 官方地址



# 3. 热补丁
_ModelManager._get_model_local_path = _offline_get_model_local_path

# 4. 可选：把 save_dir 也指向同一目录，防止框架再创建默认路径
_ModelManager._save_dir = PRIVATE_MIRROR



from QingziClass.doqingziclass import DoQingziClass

qc = DoQingziClass()
qc.attSheet()


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
