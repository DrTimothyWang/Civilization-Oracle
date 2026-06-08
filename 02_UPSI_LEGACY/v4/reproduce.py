#!/usr/bin/env python3
"""
Civilization-Oracle v4.0 - 一键复现脚本
======================================

从零开始复现 v4.0 完整结果：
1. 收集 96 个十年的真实 LLM 数据
2. 计算 PSI（v4.0 唯一公式）
3. 跑 individual-level 统计
4. 生成 4 张 Figure
5. 打印统计报告

用法:
    python reproduce.py              # 完整流程（耗时约 5-10 分钟）
    python reproduce.py --skip-api   # 跳过 API 调用（使用已有数据）
"""
import sys
import os
import subprocess
import argparse
import time

V4_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name, description):
    """运行 v4 子脚本"""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"  脚本: {script_name}")
    print(f"{'='*70}")
    script_path = os.path.join(V4_DIR, script_name)
    t0 = time.time()
    result = subprocess.run([sys.executable, script_path], cwd=V4_DIR)
    elapsed = time.time() - t0
    if result.returncode == 0:
        print(f"\n[✓] {description} 完成 ({elapsed:.1f}s)")
    else:
        print(f"\n[✗] {description} 失败 (returncode={result.returncode})")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-api", action="store_true", help="跳过 API 数据收集")
    parser.add_argument("--skip-figures", action="store_true", help="跳过 Figure 生成")
    args = parser.parse_args()

    print("=" * 70)
    print("Civilization-Oracle v4.0 - 一键复现")
    print("=" * 70)

    steps = [
        # 步骤 1: 数据收集（如果需要）
        ("run_data_v4.py", "Step 1: 收集 96 个十年的真实 LLM 数据") if not args.skip_api else None,
        # 步骤 2: PSI 计算
        ("compute_psi_v4.py", "Step 2: 计算 v4.0 PSI"),
        # 步骤 3: 统计
        ("statistics_v4.py", "Step 3: individual-level 统计"),
        # 步骤 4: Figure
        ("figures_v4.py", "Step 4: 生成 4 张 Figure") if not args.skip_figures else None,
    ]
    steps = [s for s in steps if s is not None]

    for script, desc in steps:
        if not run_script(script, desc):
            print(f"\n[!] {script} 失败，终止")
            return 1

    print("\n" + "=" * 70)
    print("🎉 v4.0 完整复现完成！")
    print("=" * 70)
    print("\n输出文件：")
    print(f"  数据: v4/data/decade_raw.json (96 窗真实 LLM 调用)")
    print(f"  PSI:  v4/data/psi_v4_results.json")
    print(f"  统计: v4/data/statistics_v4.json")
    print(f"  Figure: v4/figures/Figure1-4.png")
    print(f"  论文: v4/paper_v4_full.md")
    print(f"  报告: v4/FINAL_REPORT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
