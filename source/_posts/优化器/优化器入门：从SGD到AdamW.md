---
categories:
  - Meachine Learning
tags:
  - 优化器
mathjax: "true"
title: 优化器入门：从SGD到AdamW
date: 2026-03-11 18:02:46
---


**核心比喻：** 优化器的目标是寻找损失函数（Loss）的最低点。我们可以把这个过程想象成一个**“蒙着眼睛下山的人”**，他只能通过脚底下的坡度（梯度）来决定下一步往哪走。  

---  

## 1. SGD (随机梯度下降) —— 朴实无华的探路者  

### 🌟 Motivation (动机)  

传统的梯度下降（GD）每次更新都要计算所有数据的梯度，数据量极大时算力根本吃不消。  

**改进：** 每次只随机抽取一小批数据（Mini-batch），计算这一小批的梯度来代表整体方向。  

**策略：** 当前哪里最陡峭，就往反方向走固定的步长。  

### 📐 核心公式  

$$\theta_{t} = \theta_{t-1} - \eta \cdot g_t$$  

- $\theta_{t}$：当前参数  
    
- $\eta$：学习率（下山的步长）  
    
- $g_t$：当前计算出的梯度  
    

### 💻 伪代码  

Python  

```  

# 初始化  
lr = 0.01  

# 更新过程  
def step(params, grads):  
    for i in range(len(params)):  
        params[i] = params[i] - lr * grads[i]  
```  

### ❌ 痛点 (为什么需要改进？)  

1. **峡谷震荡 (Zig-zagging)：** 在狭长的地形中，会在陡峭的两壁来回震荡，而在通向谷底的平缓方向上前进极慢。  
    
2. **容易卡死：** 遇到局部最优解的小坑，或者梯度为 0 的平坦鞍点，就会彻底停下。  
    

---  

## 2. SGD + Momentum (动量) —— 加上物理外挂的推车人  

### 🌟 Motivation (动机)  

为了解决 SGD 容易震荡和卡死的问题，引入物理学中的 **“惯性”**。就像推着一个沉重的铁球下山，即使遇到小坑也能凭惯性冲过去；在震荡的峡谷中，左右摇摆的力会互相抵消，从而径直向前。  

### 📐 核心公式  

引入“速度” $v_t$（带方向的一阶矩）：  

$$v_t = \beta \cdot v_{t-1} + g_t$$  

$$\theta_t = \theta_{t-1} - \eta \cdot v_t$$  

- $v_t$：当前累积的速度（包含历史方向）。  
    
- $\beta$：动量系数（通常为 0.9），表示保留多少过去的惯性。  
    

### 💻 伪代码  

Python  

```  

# 初始化  
lr = 0.01  
beta = 0.9  
velocities = [0, 0, ...] # 记录每个参数的速度  

# 更新过程  
def step(params, grads):  
    for i in range(len(params)):  
        # 1. 累加梯度，形成惯性  
        velocities[i] = beta * velocities[i] + grads[i]  
        # 2. 顺着惯性方向更新  
        params[i] = params[i] - lr * velocities[i]  
```  

### ❌ 痛点 (为什么需要改进？)  

**学习率一刀切。** 模型中有高频特征和低频特征，Momentum 对所有参数都使用相同的全局学习率 $\eta$。我们需要一种能“感知地形”，给不同参数分配不同步长的机制。  

---  

## 3. RMSprop (均方根传播) —— 穿上智能跑鞋  

_(注：这里跳过了 AdaGrad，因为 AdaGrad 简单累加所有历史梯度平方会导致学习率无限趋近于 0，最终“学不动”。RMSprop 是其完美的改进版。)_  

### 🌟 Motivation (动机)  

实现**自适应学习率（Adaptive Learning Rate）**。  

**核心设计哲学：**  

1. **用梯度的平方 $g_t^2$：** 消除正负号方向，只衡量波动的“剧烈程度（能量）”。并且平方能极大放大“异常极值（Spike）”，充当紧急刹车。  
    
2. **用滑动平均：** 引入遗忘机制，只关注最近一段时间的波动，防止学习率衰减到 0。  
    
3. **开根号 $\sqrt{\cdot}$：** 保证量纲（物理单位）的一致性，让全局学习率重新回归纯粹的“步长”意义。  
    

### 📐 核心公式  

引入“二阶矩”（梯度平方的滑动平均） $v_t$：  

$$v_t = \alpha \cdot v_{t-1} + (1 - \alpha) \cdot g_t^2$$  

$$\theta_t = \theta_{t-1} - \frac{\eta}{\sqrt{v_t + \epsilon}} \cdot g_t$$  

- $\alpha$：遗忘系数（通常为 0.9 或 0.99）。  
    
- $\epsilon$：防除零的小常数（如 1e-8）。  
    

### 💻 伪代码  

Python  

```  

# 初始化  
lr = 0.001  
alpha = 0.9  
epsilon = 1e-8  
v = [0, 0, ...] # 记录梯度的平方滑动平均  

# 更新过程  
def step(params, grads):  
    for i in range(len(params)):  
        # 1. 计算波动程度  
        v[i] = alpha * v[i] + (1 - alpha) * (grads[i] ** 2)  
        # 2. 波动大的地方分母大(步子小)，波动小的地方分母小(步子大)  
        params[i] = params[i] - (lr / (np.sqrt(v[i]) + epsilon)) * grads[i]  
```  

---  

## 4. Adam (自适应矩估计) —— 我全都要的集大成者  

### 🌟 Motivation (动机)  

既然 Momentum 提供了极佳的**方向（一阶矩）**，RMSprop 提供了极佳的**动态步长（二阶矩）**，为什么不把它们合二为一？  

**改进：** Adam 结合了动量和自适应学习率，并额外加入了**偏差校正（Bias Correction）**来解决冷启动时变量偏向于 0 的问题。  

### 📐 核心公式  

计算一阶矩（惯性）和二阶矩（波动）：  

$$m_t = \beta_1 \cdot m_{t-1} + (1 - \beta_1) \cdot g_t$$  

$$v_t = \beta_2 \cdot v_{t-1} + (1 - \beta_2) \cdot g_t^2$$  

偏差校正（放大初期的值）：  

$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}$$  

$$\hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$  

参数更新：  

$$\theta_t = \theta_{t-1} - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \cdot \hat{m}_t$$  

### 💻 伪代码  

Python  

```  

# 初始化  
lr = 0.001  
beta1, beta2 = 0.9, 0.999  
epsilon = 1e-8  
m = [0, 0, ...]  
v = [0, 0, ...]  
t = 0 # 时间步  

# 更新过程  
def step(params, grads):  
    t += 1  
    for i in range(len(params)):  
        # 1. 计算一阶矩和二阶矩  
        m[i] = beta1 * m[i] + (1 - beta1) * grads[i]  
        v[i] = beta2 * v[i] + (1 - beta2) * (grads[i] ** 2)  
        
        # 2. 偏差校正  
        m_hat = m[i] / (1 - beta1 ** t)  
        v_hat = v[i] / (1 - beta2 ** t)  
        
        # 3. 参数更新  
        params[i] = params[i] - lr * m_hat / (np.sqrt(v_hat) + epsilon)  
```  

### ❌ 痛点 (为什么需要改进？)  

在引入 L2 正则化（权重衰减）时，由于早期的代码实现偷懒，将正则化项直接塞进梯度 $g_t$ 中，导致惩罚项被 Adam 自带的分母 $\sqrt{v_t}$ 错误地缩放。结果是：在需要强泛化能力的任务中（如大模型训练），老 Adam 的表现往往不如老牌的 SGD + Momentum。  

---  

## 5. AdamW —— 拨乱反正的最强王者  

### 🌟 Motivation (动机)  

**解耦权重衰减（Decoupled Weight Decay）。**  

正如直觉所理解的那样：**Task Loss 走 Adam 复杂的自适应体系，而 L2 正则化走最简单粗暴的 SGD 体系。** 将权重衰减从梯度的计算流中强行拆解出来，防止其被 Adam 的动态学习率所扭曲。  

### 📐 核心公式  

只需在 Adam 最终的更新公式后，显式减去当前参数的一个比例即可：  

$$\theta_t = \theta_{t-1} - \underbrace{\eta \cdot \left( \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} \right)}_{\text{按照纯净梯度计算的 Adam 更新}} - \underbrace{\eta \cdot \lambda \cdot \theta_{t-1}}_{\text{单纯的权重衰减}}$$  

- $\lambda$：权重衰减系数（Weight Decay Factor）。  
    

### 💻 伪代码  

Python  

```  

# 初始化 (增加 weight_decay)  
lr = 0.001  
beta1, beta2 = 0.9, 0.999  
weight_decay = 0.01  
epsilon = 1e-8  
m, v, t = [0...], [0...], 0  

# 更新过程  
def step(params, grads_without_L2): # 强调传入纯净梯度  
    t += 1  
    for i in range(len(params)):  
        # 1. 完全按照纯净梯度走 Adam 的流程  
        m[i] = beta1 * m[i] + (1 - beta1) * grads_without_L2[i]  
        v[i] = beta2 * v[i] + (1 - beta2) * (grads_without_L2[i] ** 2)  
        
        m_hat = m[i] / (1 - beta1 ** t)  
        v_hat = v[i] / (1 - beta2 ** t)  
        
        adam_update = lr * m_hat / (np.sqrt(v_hat) + epsilon)  
        
        # 2. 解耦：单独计算权重衰减 (类似 SGD 的做法)  
        decay_update = lr * weight_decay * params[i]  
        
        # 3. 合并更新  
        params[i] = params[i] - adam_update - decay_update  
```  

---  

## 6. Shampoo —— 给梯度“洗头”的二阶魔法师  

### 🌟 Motivation (动机)  

Adam 及其变种（包括 AdamW）有一个致命盲区：**对角线近似假设**。它认为所有的参数都是完全独立、互不干涉的，只给每个参数单独算一个方差（自适应步长）。  

但在真实的线性层中，权重是以矩阵（2D）形式存在的，**行与行（输入特征）、列与列（输出特征）之间存在着极其强烈的协同绑定关系**。  

**改进：** Shampoo 试图引入**协方差矩阵**来解绑这种关系。由于完整的协方差矩阵极其庞大（例如 $10^{12}$ 个元素，根本算不动），Shampoo 提出了天才的**行列独立假设（Kronecker Factored Approximation）**，将大矩阵拆解为一个管行的“左矩阵”和一个管列的“右矩阵”。  

### 📐 核心公式  

假设当前梯度矩阵为 $G_t$（尺寸 $m \times n$）：  

**1. 统计行列的协同关系（二阶矩矩阵化）：**  

$$L_t = \beta L_{t-1} + (1 - \beta) G_t G_t^\top \quad \text{(左矩阵：输入特征相关性，} m \times m \text{)}$$  

$$R_t = \beta R_{t-1} + (1 - \beta) G_t^\top G_t \quad \text{(右矩阵：输出特征相关性，} n \times n \text{)}$$  

**2. 给梯度洗头（Preconditioning / 白化）：**  

为了消除这些绑定关系带来的畸形拉伸，分别对 $L_t$ 和 $R_t$ 求**逆四次方根**（通常需做特征值分解/SVD），然后从左右两边夹击原始梯度：  

$$\hat{G}_t = L_t^{-1/4} \cdot G_t \cdot R_t^{-1/4}$$  

经过这一步，原本崎岖的椭圆形损失地形，被强行“洗”成了各向同性的完美正圆形大锅底。  

### 💻 伪代码  

Python  

```  
import numpy as np  

# 初始化  
lr = 0.01  
beta = 0.9  
L_state, R_state = 0, 0  

def compute_inverse_root(matrix, power=-0.25):  
    # 极其耗时的操作：特征值分解 (EVD/SVD)  
    eigenvals, eigenvecs = np.linalg.eigh(matrix)  
    eigenvals = np.maximum(eigenvals, 1e-8)  
    inv_root_eigenvals = np.diag(eigenvals ** power)  
    return eigenvecs @ inv_root_eigenvals @ eigenvecs.T  

def step(weight_matrix, grad_matrix):  
    global L_state, R_state  
    
    # 1. 收集行与列的协同波动信息  
    L_state = beta * L_state + (1 - beta) * (grad_matrix @ grad_matrix.T)  
    R_state = beta * R_state + (1 - beta) * (grad_matrix.T @ grad_matrix)  
    
    # 2. 算逆四次方根 (工程中通常每隔 N 步才算一次，因为太慢)  
    L_inv = compute_inverse_root(L_state)  
    R_inv = compute_inverse_root(R_state)  
    
    # 3. 洗头：抽出解耦后的纯净梯度  
    preconditioned_grad = L_inv @ grad_matrix @ R_inv  
    
    # 4. 更新权重  
    weight_matrix = weight_matrix - lr * preconditioned_grad  
    return weight_matrix  
```  

### ❌ 痛点 (为什么需要改进？)  

**硬件极度不友好。** 现代 GPU 的 Tensor Core 是为极其快速的矩阵乘法（Matmul）而生的。Shampoo 核心的特征值分解（SVD/EVD）包含大量非线性迭代和除法，在 GPU 上运行极度缓慢，严重拖慢了大型语言模型（LLM）的训练吞吐量。  

---  

## 7. Muon (动量正交化) —— 极致的硬件暴力美学  

### 🌟 Motivation (动机)  

既然 Shampoo 费尽心机做 SVD，最终目的是剔除梯度矩阵里的拉伸量（奇异值 $\Sigma$），抽出那个最纯净的方向矩阵（即**正交矩阵** $U V^\top$）。  

**改进：** Muon（Momentum orthogonalized by Newton-Schulz）直接抛弃了缓慢的 SVD，利用古老的**牛顿-舒尔茨迭代（Newton-Schulz Iteration）**，纯靠极其高效的**矩阵乘法**，强行将梯度矩阵暴打成正交矩阵。  

在理论上，Muon 被证明是**谱范数（Spectral Norm，最大奇异值）约束下的最速下降法**，它保证了在任何特征方向上的拉伸都不会越界，从根本上防止了激活值爆炸。  

### 📐 核心公式  

首先累加一阶动量 $M_t$：  

$$M_t = \beta M_{t-1} + G_t$$  

将动量缩放后（设为 $X_0$），进行 5 步左右的 Newton-Schulz 迭代：  

$$X_{k+1} = 1.5 X_k - 0.5 X_k (X_k^\top X_k)$$  

这个极其优美的三次多项式迭代，能像“粉碎机”一样，把所有参差不齐的奇异值全部碾压成 $1$。  

最终得到的矩阵就是正交化后的更新方向（记为 $\hat{G}_t$）：  

$$W_t = W_{t-1} - \eta \cdot \left( \text{Scale} \cdot \hat{G}_t + \lambda W_{t-1} \right)$$  

_Scale 是为了对齐 Adam 的更新步长（如 $0.2 \times \sqrt{\max(n,m)}$），白嫖 Adam 的超参经验。_  

### 💻 伪代码  

Python  

```  
import torch  

# 初始化  
lr = 0.001  
momentum = 0.9  
weight_decay = 0.01  
ns_steps = 5  # 迭代 5 次足矣  
M_state = 0  

def step(weight_matrix, grad_matrix):  
    global M_state  
    
    # 1. 累加动量 (保留方向惯性)  
    M_state = momentum * M_state + grad_matrix  
    X = M_state.clone()  
    
    # 2. 缩放防爆 (除以近似范数，保证能收敛)  
    X = X / (torch.linalg.norm(X) + 1e-8)  
    
    # 3. 暴力美学：Newton-Schulz 迭代榨干奇异值 (纯 Tensor Core 狂欢)  
    for _ in range(ns_steps):  
        A = X @ X.T @ X  # 极其丝滑的连续矩阵乘法  
        X = 1.5 * X - 0.5 * A  
        
    orthogonalized_grad = X  
    
    # 4. 步长补偿与 Adam 对齐  
    scale = 0.2 * max(weight_matrix.shape) ** 0.5  
    
    # 5. 更新权重 (包含解耦的 weight decay)  
    weight_matrix = weight_matrix - lr * (scale * orthogonalized_grad + weight_decay * weight_matrix)  
    return weight_matrix  
```  

### ⚠️ 工程落地与避坑指南 (Hybrid 混合训练策略)  

在现代大模型（如 Kimi 2、Llama 变体）训练中，Muon 并非万能药，必须与 AdamW 混搭使用：  

1. **1D 参数（Bias, LayerNorm）必须用 AdamW：** Muon 依赖 2D 矩阵做正交化。1D 向量强行正交化等同于普通归一化，会破坏其固有的独立自适应步长。  
    
2. **稀疏层（Embedding）必须用 AdamW：** Embedding 的输入极度稀疏（One-hot），强行正交化会摧毁表征。  
    
3. **QKV 需解绑：** Transformer 中的 Q、K、V 矩阵应当独立进行 Muon 更新，切忌拼接成大矩阵后再做正交化。  
    
4. **微调（SFT/LoRA）慎用：** Muon 预训练会强行拉平权重矩阵的奇异值，打破“低秩假设”。在 Muon 训出的底座上跑 LoRA，效果往往大打折扣。  
    
