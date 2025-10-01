# 致命性BUG

## [网络上的一种bug描述与解决方案，我这里没用](https://github.com/PaddlePaddle/PaddleOCR/issues/16606)

## 本地运行记录

````
D:\Python\python.exe D:\code\SmartSheetPY\SmartSheetPY.py 
Active code page: 65001
加载ppocr的模型
INFO: Could not find files for the given pattern(s).
D:\Python\Lib\site-packages\paddle\utils\cpp_extension\extension_utils.py:718: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)
Creating model: ('PP-LCNet_x1_0_doc_ori', '.\\model_nature\\PP-LCNet_x1_0_doc_ori')
WARNING: Logging before InitGoogleLogging() is written to STDERR
I1001 16:48:53.392244 19784 onednn_context.cc:81] oneDNN v3.6.2
Creating model: ('UVDoc', '.\\model_nature\\UVDoc')
Creating model: ('PP-DocLayout-L', '.\\model_nature\\PP-DocLayout-L')
Creating model: ('PP-LCNet_x1_0_table_cls', '.\\model_nature\\PP-LCNet_x1_0_table_cls')
Creating model: ('SLANeXt_wired', '.\\model_nature\\SLANeXt_wired')
Creating model: ('SLANeXt_wireless', '.\\model_nature\\SLANeXt_wireless')
Creating model: ('RT-DETR-L_wired_table_cell_det', '.\\model_nature\\RT-DETR-L_wired_table_cell_det')
Creating model: ('RT-DETR-L_wireless_table_cell_det', '.\\model_nature\\RT-DETR-L_wireless_table_cell_det')
Creating model: ('PP-OCRv4_server_det', '.\\model_nature\\PP-OCRv4_server_det')
Creating model: ('PP-OCRv4_server_rec_doc', '.\\model_nature\\PP-OCRv4_server_rec_doc')
Creating model: ('PP-LCNet_x1_0_doc_ori', None)
Using official model (PP-LCNet_x1_0_doc_ori), the model files will be automatically downloaded and saved in `C:\Users\Sicheng Liu\.paddlex\official_models\PP-LCNet_x1_0_doc_ori`.
Processing 5 items:   0%|          | 0.00/5.00 [00:00<?, ?it/s]
Downloading [config.json]:   0%|          | 0.00/2.50k [00:00<?, ?B/s]

Downloading [README.md]:   0%|          | 0.00/6.67k [00:00<?, ?B/s]


Downloading [inference.json]:   0%|          | 0.00/102k [00:00<?, ?B/s]

Downloading [README.md]: 100%|██████████| 6.67k/6.67k [00:02<00:00, 2.75kB/s]
Processing 5 items:  20%|██        | 1.00/5.00 [00:03<00:13, 3.48s/it]


Downloading [inference.json]: 100%|██████████| 102k/102k [00:02<00:00, 41.2kB/s]
Processing 5 items:  40%|████      | 2.00/5.00 [00:03<00:05, 1.70s/it]

Downloading [inference.pdiparams]:   0%|          | 0.00/6.44M [00:00<?, ?B/s]
Downloading [config.json]: 100%|██████████| 2.50k/2.50k [00:03<00:00, 741B/s]
Processing 5 items:  60%|██████    | 3.00/5.00 [00:04<00:02, 1.15s/it]
Downloading [inference.yml]:   0%|          | 0.00/766 [00:00<?, ?B/s]

Downloading [inference.pdiparams]:  16%|█▌        | 1.00M/6.44M [00:02<00:12, 448kB/s]

Downloading [inference.pdiparams]: 100%|██████████| 6.44M/6.44M [00:02<00:00, 2.66MB/s]
Processing 5 items:  80%|████████  | 4.00/5.00 [00:06<00:01, 1.67s/it]
Downloading [inference.yml]: 100%|██████████| 766/766 [00:02<00:00, 262B/s]
Processing 5 items: 100%|██████████| 5.00/5.00 [00:07<00:00, 1.55s/it]
模型预加载完成
ppocr模型加载完毕!!!
````

# 我的解决方案

直接劫持官方下载器，不联网下载
````python
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PADDLE_PDX_CACHE_HOME'] = BASE_DIR

import os, pathlib
from paddlex.inference.utils.official_models import _ModelManager

# 1. 本地镜像根目录（自己维护）
PRIVATE_MIRROR = pathlib.Path(os.path.join(BASE_DIR, 'official_models'))


# 2. 彻底替换 _get_model_local_path：永远不走 hoster
def _offline_get_model_local_path(self, model_name):
    local_dir = PRIVATE_MIRROR / model_name
    if not local_dir.exists():
        raise FileNotFoundError(
            f'离线模式：本地镜像 {local_dir} 不存在，'
            f'请将官方 tar 解压到 {PRIVATE_MIRROR} 并保证文件夹名与模型名一致。'
        )
    # 直接返回本地路径，框架后续会直接加载
    return local_dir


# 3. 热补丁
_ModelManager._get_model_local_path = _offline_get_model_local_path

# 4. 可选：把 save_dir 也指向同一目录，防止框架再创建默认路径
_ModelManager._save_dir = PRIVATE_MIRROR
````

### 运行效果

````
D:\Python\python.exe D:\code\SmartSheetPY\SmartSheetPY.py 
Active code page: 65001
No model hoster is available! Please check your network connection to one of the following model hosts:
HuggingFace (https://huggingface.co),
ModelScope (https://modelscope.cn),
AIStudio (https://aistudio.baidu.com), or
BOS (https://paddle-model-ecology.bj.bcebos.com).
Otherwise, only local models can be used.
加载ppocr的模型
INFO: Could not find files for the given pattern(s).
D:\Python\Lib\site-packages\paddle\utils\cpp_extension\extension_utils.py:718: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)
Creating model: ('PP-LCNet_x1_0_doc_ori', '.\\official_models\\PP-LCNet_x1_0_doc_ori')
WARNING: Logging before InitGoogleLogging() is written to STDERR
I1001 22:11:24.324975  1728 onednn_context.cc:81] oneDNN v3.6.2
Creating model: ('UVDoc', '.\\official_models\\UVDoc')
Creating model: ('PP-DocLayout-L', '.\\official_models\\PP-DocLayout-L')
Creating model: ('PP-LCNet_x1_0_table_cls', '.\\official_models\\PP-LCNet_x1_0_table_cls')
Creating model: ('SLANeXt_wired', '.\\official_models\\SLANeXt_wired')
Creating model: ('SLANeXt_wireless', '.\\official_models\\SLANeXt_wireless')
Creating model: ('RT-DETR-L_wired_table_cell_det', '.\\official_models\\RT-DETR-L_wired_table_cell_det')
Creating model: ('RT-DETR-L_wireless_table_cell_det', '.\\official_models\\RT-DETR-L_wireless_table_cell_det')
Creating model: ('PP-OCRv4_server_det', '.\\official_models\\PP-OCRv4_server_det')
Creating model: ('PP-OCRv4_server_rec_doc', '.\\official_models\\PP-OCRv4_server_rec_doc')
Creating model: ('PP-LCNet_x1_0_doc_ori', None)
模型预加载完成
ppocr模型加载完毕!!!
````