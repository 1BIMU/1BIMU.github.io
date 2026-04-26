# CIFAR-100 实验总结: MC-SSO vs SSO vs Muon vs AdamW  

  

## 实验设置  

  

- 模型: SimpleCNN (3-block CNN, Conv2d + BN + ReLU + MaxPool)  

- 数据集: CIFAR-100 (100类, 32x32)  

- Epochs: 50  

- Batch size: 128  

- Seed: 42  

- 2D参数 (Conv/Linear weights): 使用对应优化器  

- 1D参数 (bias, BN): 使用 AdamW fallback (lr=1e-3, wd=5e-2)  

  

### 优化器超参数  

  
| 参数 | MC-SSO / SSO | Muon | AdamW |  
|------|-------------|------|-------|  
| LR | 0.02 | 0.02 | 1e-3 |  
| Momentum | 0.9 | 0.95 | - |  
| Nesterov | Yes | Yes | - |  
| Weight Decay | 0.05 | 0 | 0.05 |  
| NS Steps | 5 | 5 | - |  
| Power Iter Steps | 5 | - | - |  
| Radius Mode | spectral_mup | - | - |  
| Radius Scaler | 2.0 | - | - |  
| Scale Mode | align_adamw_rms | - | - |  
| Lambda Solver | max_iter=1, tol=1e-3 | - | - |  
| Scheduler | CosineAnnealingLR | CosineAnnealingLR | CosineAnnealingLR |  
  

## 最终结果  

  
| 优化器 | Best Test Acc | Final Train Acc | Final Test Acc | 每步耗时 |  
|--------|-------------|-----------------|----------------|---------|  
| Muon | **61.33%** | 67.73% | 61.24% | ~4.4s |  
| SSO | 57.69% | 54.61% | 57.69% | ~16s |  
| MC-SSO | 56.90% | 52.70% | 56.90% | ~16s |  
| AdamW | 55.20% | 46.41% | 55.00% | ~4.3s |  

## 遇到的问题及解决方案  

  

### 1. SSO/MC-SSO 准确率极低 (31-32%)  

  

**现象**: 初始实验中 SSO 和 MC-SSO 的 best test acc 仅为 31-32%, 远低于 Muon (62%) 和 AdamW (55%).  

  

**根因**: `apply_retract` 中的硬投影过于激进. `spectral_mup` 模式下 `radius_scaler=1.0` 产生的目标半径 R 远小于实际谱范数 σ, 导致每步权重被缩放 0.48-0.60 倍, 相当于每步丢失一半的权重信息.  

  

**解决**: 将 `radius_scaler` 从 1.0 提升到 2.0, 使投影更温和. SSO 从 31% 提升到 57.69%, MC-SSO 从 32% 提升到 56.90%.  

  

### 2. SSO/MC-SSO 训练速度 (74.6ms → 24.3ms/batch)  

  

**现象**: 初始实现中 SSO 每个 batch 耗时 74.6ms, 是 Muon 的 10 倍以上.  

  

**优化措施**:  

- Power iteration 步数: 10 → 5 (精度损失可忽略)  

- Newton-Schulz (msign) 步数: 8 → 5 (使用 Polar-Express 系数, 5步已足够收敛)  

- Lambda solver: max_iterations 10 → 1, tolerance 1e-6 → 1e-3 (lambda 修正对 Phi 的影响仅 ~1.25%)  

- Lambda 缓存: 将上一步的 lambda 作为下一步的初始猜测, 加速收敛  

  

最终每 batch 耗时从 74.6ms 降至 ~24.3ms.  

  

### 3. Power Iteration 精度问题  

  

**现象**: 尝试将 power iteration 改为 bf16 以加速, 但发现精度下降明显.  

  

**解决**: 保持 power iteration 在 fp32 下运行. msign 部分仍使用 bf16 (与 Megatron-LM 和 Muon 一致).  

  

### 4. MC-SSO 未能超越 SSO  

  

**现象**: MC-SSO (带切空间动量传输) 的表现略低于 vanilla SSO (56.90% vs 57.69%).  

  

**分析**: 在这个小型 CNN 上, 层的谱结构在步与步之间变化不大, 切空间投影的收益有限. 这一机制可能在更大模型 (如 Transformer) 上更有价值, 因为大模型的权重矩阵谱结构变化更剧烈.  

  

### 5. Python 版本问题  

  

**现象**: 默认 `python` 指向 Python 2.7, 不支持类型注解语法 (`int = 100`).  

  

**解决**: 使用项目 `.venv` 中的 `python3` (Python 3.10 + PyTorch 2.6 + CUDA).  

  

## 关键发现  

  

1. **Retraction 半径是 SSO 性能的关键旋钮** — 过小的半径会严重抑制学习, 需要根据模型规模仔细调节.  

2. **Lambda solver 的精度要求很低** — 1次迭代 + 宽松容差即可, 对最终精度几乎无影响, 但大幅节省计算.  

3. **SSO/MC-SSO 的正则化效果更强** — train-test gap 比 Muon 小 (SSO: 54.61/57.69 vs Muon: 67.73/61.24), 谱约束起到了隐式正则化作用.  

4. **收敛速度仍是主要劣势** — SSO/MC-SSO 前半段学习缓慢, 后半段随 cosine schedule 加速追赶, 但每步计算量仍是 Muon 的 ~3.6 倍.  