# -*- coding: utf-8 -*-
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


# ========== 4. 劫持 _ModelManager._get_model_local_path，仍复用官方 _get_model_local_path ==========
def _hijacked_get_model_local_path(self, model_name: str) -> pathlib.Path:
    target_dir = MY_MIRROR_ROOT / model_name
    # 本地命中
    if target_dir.exists() and (target_dir / "inference.yml").exists():
        return target_dir
    # 缺失 → 复用官方“挑最优 hoster + 下载”逻辑

    """这里应该加上一个选择位置"""
    """添加一个注册函数，将hijack的路径定向到镜像目录中"""

    return self._download_from_hoster(self._hosters, model_name)


_ModelManager._get_model_local_path = _hijacked_get_model_local_path

a: int = 0
