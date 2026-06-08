"""
配置加载工具
支持 YAML 配置文件读取和点号路径访问

用法：
    from utils.config_loader import load_config, get

    # 加载全部配置
    config = load_config()

    # 按点号路径获取值
    psi_weights = get('psi.weights', config=config)
    sfd_weight = get('psi.weights.sfd', config=config)

    # 获取单值（带默认值）
    timeout = get('pipeline.timeout_seconds', default=300)
"""

import yaml
from pathlib import Path
from typing import Any, Optional


def load_config(path: str = 'config/pipeline_config.yaml') -> dict:
    """
    加载 YAML 配置文件

    参数：
        path: 配置文件路径（相对于项目根目录）
    返回：
        配置字典
    """
    config_path = Path(path)

    # 尝试从当前工作目录查找
    if not config_path.is_absolute():
        # 相对于项目根目录
        project_root = Path(__file__).parent.parent
        config_path = project_root / path

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get(key: str, default: Any = None, config: Optional[dict] = None) -> Any:
    """
    获取配置值：支持点号路径访问嵌套字典

    参数：
        key: 点号分隔的路径，如 'psi.weights.sfd'
        default: 默认值（当路径不存在时返回）
        config: 配置字典（如果不提供则自动加载）

    返回：
        配置值或默认值

    示例：
        >>> config = {'psi': {'weights': {'sfd': 0.5}}}
        >>> get('psi.weights.sfd', config=config)
        0.5
        >>> get('psi.weights.mmp', default=0.25, config=config)
        0.25
        >>> get('nonexistent.key', default='fallback', config=config)
        'fallback'
    """
    if config is None:
        config = load_config()

    keys = key.split('.')
    value = config

    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
            if value is None:
                return default
        else:
            return default

    return value if value is not None else default


def get_all(key_prefix: str, config: Optional[dict] = None) -> dict:
    """
    获取配置中以某前缀开头的所有子配置

    参数：
        key_prefix: 配置前缀，如 'psi.weights'
        config: 配置字典

    返回：
        子配置字典
    """
    if config is None:
        config = load_config()

    keys = key_prefix.split('.')
    value = config

    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return {}

    return value if isinstance(value, dict) else {}


# ============================================================
# 便捷访问函数
# ============================================================

def get_psi_weights() -> dict:
    """获取 PSI 权重配置"""
    config = load_config()
    return get('psi.weights', config=config)


def get_pipeline_config() -> dict:
    """获取 Pipeline 配置"""
    config = load_config()
    return get('pipeline', config=config)


def get_quality_thresholds() -> dict:
    """获取质量阈值配置"""
    config = load_config()
    return get('quality', config=config)


# ============================================================
# 测试入口
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("配置加载工具测试")
    print("=" * 50)

    try:
        # 测试加载
        config = load_config()
        print(f"\n✓ 配置文件加载成功")

        # 测试点号访问
        print(f"\nPSI权重: {get('psi.weights', config=config)}")
        print(f"SFD权重: {get('psi.weights.sfd', config=config)}")
        print(f"NLP模型: {get('nlp.sikubert_model', config=config)}")
        print(f"Pipeline阶段: {get('pipeline.stages', config=config)}")
        print(f"测试覆盖率: {get('quality.unit_test_coverage_minimum', config=config)}")

        # 测试默认值
        print(f"\n默认值测试: {get('nonexistent.key', default='default_value', config=config)}")

        print("\n" + "=" * 50)
        print("配置加载测试通过")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"\n✗ 配置文件未找到: {e}")
        print("请确保 config/pipeline_config.yaml 存在")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")