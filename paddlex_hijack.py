"""
PaddleX 官方模型下载目录劫持器
author : you
usage  :
    import paddlex_hijack        # 先劫持
    import paddlex               # 再正常使用
"""
import os
import pathlib
from paddlex.inference.utils.official_models import _ModelManager, _BosModelHoster

# ========== 1. 你要放模型的根目录 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_MIRROR_ROOT = pathlib.Path(BASE_DIR)  # 改成你的路径
os.environ["PADDLE_PDX_CACHE_HOME"] = BASE_DIR
MY_MIRROR_ROOT.mkdir(parents = True, exist_ok = True)


# ========== 2. 兜底下载器（这里直接禁用，想保留下载可打开注释） ==========
class _OfflineBosHoster(_BosModelHoster):
    """本地有就用，没有就抛异常，绝不下载"""

    def _download(self, model_name: str, save_dir: pathlib.Path):
        raise FileNotFoundError(
            f"本地镜像缺失：{model_name} ，已禁止自动下载！\n"
            f"请将完整模型文件夹手动放到 {save_dir} 然后重试。"
        )


# ========== 3. 热替换 _ModelManager 的核心函数 ==========
def _hijacked_get_model_local_path(self, model_name: str) -> pathlib.Path:
    """永远先去 MY_MIRROR_ROOT 找模型"""
    target_dir = MY_MIRROR_ROOT / model_name
    if target_dir.exists() and (target_dir / "inference.yml").exists():
        # 本地命中
        return target_dir

    # 本地缺失 → 用我们自定义的 hoster 处理（这里会抛异常）
    hoster = _OfflineBosHoster(MY_MIRROR_ROOT)
    return hoster.get_model(model_name)


# ========== 4. 注入补丁 ==========
_ModelManager._get_model_local_path = _hijacked_get_model_local_path
_ModelManager._save_dir = MY_MIRROR_ROOT  # 顺带把默认目录也改掉


