# 致命性BUG

## [网络上的一种bug描述与解决方案，我这里没用](https://github.com/PaddlePaddle/PaddleOCR/issues/16606)
## 简单描述
部署离线 server 端的时候总需要在线验证`PP-LCNet_x1_0_doc_ori`，如果离线则提示`Creating model: ('PP-LCNet_x1_0_doc_ori', None) No available model hosting platforms detected. Please check your network connection.`   
### 原因
ppocr在加载本地模型的时候可以指定路径，但是内部子模块会再次加载，无法正常传递模型路径，会加载官方下载器，将模型下载到默认文件夹

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

直接劫持官方下载器，更改模型默认保存的路径，这样保留了自动下载功能，又能正常从默认路径下加载模型 
````python
"""
PaddleX 官方模型下载目录劫持器
author : lscatfish
usage:
    import paddlex_hijack      # 必须先导入
    import paddlex
"""
import os
import pathlib

# ========== 1. 你想把模型放在哪里 ==========
BASE_DIR = os.getcwd()
MY_MIRROR_ROOT = pathlib.Path(BASE_DIR) / "official_models"
MY_MIRROR_ROOT.mkdir(parents = True, exist_ok = True)

# ========== 2. 把环境变量、默认目录全部改掉 ==========
os.environ["PADDLE_PDX_CACHE_HOME"] = str(BASE_DIR)

from paddlex.inference.utils.official_models import (
    _ModelManager,
    _BosModelHoster,
    _HuggingFaceModelHoster,
    _ModelScopeModelHoster,
    _AIStudioModelHoster,
)

_ModelManager._save_dir = MY_MIRROR_ROOT  # 新生成的 Manager 会用到

# ========== 3. 强制给所有 hoster 类打补丁，让它们的 save_dir=MY_MIRROR_ROOT ==========
for hoster_cls in (
        _BosModelHoster,
        _HuggingFaceModelHoster,
        _ModelScopeModelHoster,
        _AIStudioModelHoster,
):
    # 把 __init__ 里 self._save_dir = save_dir 改成 self._save_dir = MY_MIRROR_ROOT
    _orig_init = hoster_cls.__init__


    def _new_init(self, save_dir, *, __orig_init = _orig_init):
        __orig_init(self, MY_MIRROR_ROOT)  # 硬塞我们的目录


    hoster_cls.__init__ = _new_init


# ========== 4. 劫持 _ModelManager._get_model_local_path，仍复用官方 _download_from_hoster ==========
def _hijacked_get_model_local_path(self, model_name: str) -> pathlib.Path:
    target_dir = MY_MIRROR_ROOT / model_name
    # 本地命中
    if target_dir.exists() and (target_dir / "inference.yml").exists():
        return target_dir
    # 缺失 → 复用官方“挑最优 hoster + 下载”逻辑
    return self._download_from_hoster(self._hosters, model_name)


_ModelManager._get_model_local_path = _hijacked_get_model_local_path

a: int = 0
````

### 运行效果

````
D:\Python\python.exe D:\code\SmartSheetPY\SmartSheetPY.py 
Active code page: 65001
加载ppocr的模型
INFO: Could not find files for the given pattern(s).
D:\Python\Lib\site-packages\paddle\utils\cpp_extension\extension_utils.py:718: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)
Creating model: ('PP-LCNet_x1_0_doc_ori', None)
WARNING: Logging before InitGoogleLogging() is written to STDERR
I1001 23:55:50.091296 16492 onednn_context.cc:81] oneDNN v3.6.2
Creating model: ('UVDoc', None)
Creating model: ('PP-DocLayout-L', None)
Creating model: ('PP-LCNet_x1_0_table_cls', None)
Creating model: ('SLANeXt_wired', None)
Creating model: ('SLANeXt_wireless', None)
Creating model: ('RT-DETR-L_wired_table_cell_det', None)
Creating model: ('RT-DETR-L_wireless_table_cell_det', None)
Creating model: ('PP-OCRv4_server_det', None)
Creating model: ('PP-OCRv4_server_rec_doc', None)
Creating model: ('PP-LCNet_x1_0_doc_ori', None)
模型预加载完成
ppocr模型加载完毕!!!
````