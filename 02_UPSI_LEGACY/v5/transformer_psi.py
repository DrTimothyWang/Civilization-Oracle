#!/usr/bin/env python3
"""
v5.0 阶段51: Transformer PSI 预测
- 用 Transformer Encoder 学习 PSI 时序模式
- 预测未来 5/20/60 天 PSI<-0.5 概率
- 对比: 简单 baseline (历史均值)
"""
import json
import statistics
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from datetime import datetime

DATA4 = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")

with open(DATA4 / "market_psi_v4.json", encoding="utf-8") as f:
    fin = json.load(f)
with open(DATA4 / "global_market_data.json", encoding="utf-8") as f:
    raw = json.load(f)


def returns(p):
    return [p[i]/p[i-1] - 1 for i in range(1, len(p))]

def rolling_mmp(p, w=60):
    return [p[i]/max(p[i-w:i+1]) - 1 for i in range(w, len(p))]

def rolling_vol(r, w=20):
    return [statistics.stdev(r[i-w:i]) * (252**0.5) for i in range(w, len(r))]


# 用标普 500 1927-2026
bars = sorted(raw["US.SP500"], key=lambda x: x[0])
prices = [b[1] for b in bars]
dates = [b[0] for b in bars]
rets = returns(prices)
mmp = rolling_mmp(prices, 60)
sfd = rolling_vol(rets, 20)
L = min(len(mmp), len(sfd))
psi = [(mmp[i] + sfd[i])/2 for i in range(L)]
mu = statistics.mean(psi)
sd = statistics.stdev(psi)
psi_z = [(p - mu) / sd for p in psi]
offset = len(prices) - L
aligned_dates = dates[offset:]

print(f"[data] {len(psi_z)} PSI z-score 样本, {aligned_dates[0]} ~ {aligned_dates[-1]}")

# 准备序列数据
SEQ_LEN = 60  # 用过去 60 天预测未来
HORIZON = 20  # 预测未来 20 天是否 PSI<-0.5

X, y = [], []
for i in range(SEQ_LEN, len(psi_z) - HORIZON):
    # 输入: 过去 60 天 PSI
    X.append(psi_z[i-SEQ_LEN:i])
    # 输出: 未来 20 天是否至少有一天 PSI<-0.5
    future = psi_z[i:i+HORIZON]
    y.append(1 if any(p < -0.5 for p in future) else 0)
X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)
print(f"[data] {len(X)} 序列, 阳性率: {y.mean():.2%}")

# 划分: 前 80% 训练, 后 20% 测试
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 简单 baseline: 预测 PSI<-0.5 如果过去 60 天平均 < 0
baseline_pred = (X_test.mean(axis=1) < 0).astype(float)
baseline_acc = ((baseline_pred == y_test).mean(), )
baseline_recall = (baseline_pred[y_test == 1].mean() if (y_test == 1).any() else 0)
baseline_precision = (y_test[baseline_pred == 1].mean() if (baseline_pred == 1).any() else 0)
print(f"\n[baseline] acc={baseline_acc[0]:.2%}, recall={baseline_recall:.2%}, precision={baseline_precision:.2%}")

# Transformer 模型
class PSI_Transformer(nn.Module):
    def __init__(self, seq_len=60, d_model=32, nhead=4, num_layers=2):
        super().__init__()
        self.proj = nn.Linear(1, d_model)
        self.pos = nn.Parameter(torch.randn(1, seq_len, d_model) * 0.1)
        enc_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=64, batch_first=True)
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=num_layers)
        self.head = nn.Sequential(
            nn.Linear(d_model, 32), nn.ReLU(),
            nn.Linear(32, 1), nn.Sigmoid()
        )

    def forward(self, x):
        # x: (B, seq_len)
        x = x.unsqueeze(-1)  # (B, seq_len, 1)
        x = self.proj(x) + self.pos
        x = self.encoder(x)
        return self.head(x[:, -1, :]).squeeze(-1)


# 训练
device = "cpu"
model = PSI_Transformer().to(device)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.BCELoss()

X_train_t = torch.from_numpy(X_train)
y_train_t = torch.from_numpy(y_train)
X_test_t = torch.from_numpy(X_test)
y_test_t = torch.from_numpy(y_test)

BATCH = 64
print("\n[training] Transformer PSI 预测器")
for epoch in range(15):
    perm = torch.randperm(len(X_train_t))
    epoch_loss = 0
    for i in range(0, len(X_train_t), BATCH):
        idx = perm[i:i+BATCH]
        xb = X_train_t[idx]
        yb = y_train_t[idx]
        pred = model(xb)
        loss = loss_fn(pred, yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        epoch_loss += loss.item() * len(xb)
    if (epoch + 1) % 3 == 0:
        with torch.no_grad():
            test_pred = model(X_test_t)
            test_pred_bin = (test_pred > 0.5).float()
            acc = (test_pred_bin == y_test_t).float().mean()
            tp = ((test_pred_bin == 1) & (y_test_t == 1)).sum()
            fp = ((test_pred_bin == 1) & (y_test_t == 0)).sum()
            fn = ((test_pred_bin == 0) & (y_test_t == 1)).sum()
            prec = tp / max(tp + fp, 1)
            rec = tp / max(tp + fn, 1)
        print(f"  epoch {epoch+1}: train loss={epoch_loss/len(X_train_t):.4f}, test acc={acc:.2%}, P={prec:.2%}, R={rec:.2%}")

# 评估
with torch.no_grad():
    test_pred = model(X_test_t)
    test_pred_bin = (test_pred > 0.5).float()
    acc = (test_pred_bin == y_test_t).float().mean()
    tp = ((test_pred_bin == 1) & (y_test_t == 1)).sum().item()
    fp = ((test_pred_bin == 1) & (y_test_t == 0)).sum().item()
    fn = ((test_pred_bin == 0) & (y_test_t == 1)).sum().item()
    tn = ((test_pred_bin == 0) & (y_test_t == 0)).sum().item()
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-10)

print(f"\n[结果]")
print(f"  Test Accuracy:  {acc:.2%}")
print(f"  Precision:      {prec:.2%}")
print(f"  Recall:         {rec:.2%}")
print(f"  F1 Score:       {f1:.2%}")
print(f"  Confusion:")
print(f"    TP={tp}, FP={fp}")
print(f"    FN={fn}, TN={tn}")

# 找重要序列
# 看哪些 60 天序列被错误预测
errors = []
for i, (true, pred) in enumerate(zip(y_test, test_pred.numpy())):
    if abs(true - pred) > 0.5:
        errors.append((i, true, pred))
print(f"\n  错误样本: {len(errors)}/{len(y_test)} ({len(errors)/len(y_test):.1%})")

# 保存结果
out = {
    "model": "Transformer (60-day seq -> 20-day risk)",
    "data": "S&P 500 PSI 1927-2026",
    "n_samples": len(X),
    "positive_rate": float(y.mean()),
    "test_metrics": {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
    },
    "baseline_metrics": {
        "accuracy": baseline_acc[0],
        "recall": float(baseline_recall),
        "precision": float(baseline_precision),
    },
    "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
}
with open(OUT / "transformer_psi_v5.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\n✅ 保存 {OUT}/transformer_psi_v5.json")
