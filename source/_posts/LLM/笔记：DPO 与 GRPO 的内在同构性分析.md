---
categories:
  - Meachine Learning
tags:
  - LLM
mathjax: "true"
title: 笔记：DPO 与 GRPO 的内在同构性分析
date: 2026-04-27 00:35:07
---

## 1. 核心观点  

在利用对比学习的场景下，GRPO（Group Relative Policy Optimization）与 DPO（Direct Preference Optimization）在优化目标上具有本质的同构性。  

GRPO 可以被视为 DPO 的一种**基于集合（Set-wise）的广义形式**。它通过基于规则的统计方式（Advantage），将一组采样输出动态划分为“胜者集合（Win Set）”和“败者集合（Lose Set）”，从而将 DPO 中原本的 **Pair-wise（成对）** 对比扩展为了 **Pair-Set-Wise（成对集合）** 对比。  

## 2. 梯度视角的推导过程  

为了验证两者的同构性，我们对比去除了参考模型（Reference Model）项的 DPO 与 Group Size 为 2 的 GRPO。  

### 2.1 DPO 的梯度（简化版）  

标准的 DPO 损失函数旨在最大化正例 $y_w$ 与负例 $y_l$ 之间的概率差。假设去除参考模型 $\pi_{ref}$（或视为常数），损失函数简化为：  

$$\mathcal{L}_{DPO} \approx -\log \sigma \left( \beta \log \pi_\theta(y_w) - \beta \log \pi_\theta(y_l) \right)$$  

对参数 $\theta$ 求梯度，其更新方向为：  

$$\nabla_\theta \mathcal{L}_{DPO} \propto -\lambda \cdot \left( \underbrace{\nabla_\theta \log \pi_\theta(y_w)}_{\text{正向增强}} - \underbrace{\nabla_\theta \log \pi_\theta(y_l)}_{\text{负向抑制}} \right)$$  

其中 $\lambda$ 为由 Sigmoid 函数导数决定的动态权重系数。  

### 2.2 GRPO 的梯度  

GRPO 使用优势函数（Advantage）作为权重进行策略梯度更新。假设一个 Group 中有两个样本集合，$y_{win}$（正确，Reward=1）和 $y_{lose}$（错误，Reward=0）：  

1. **计算统计量**：均值 $\text{mean}$。  
    
2. **计算优势 (Advantage)**：  
    
    - $A_{win} = 1 - mean$  
        
    - $A_{lose} = 0 - mean$  
        
3. **计算梯度**：  
    

$$\nabla_\theta \mathcal{L}_{GRPO} \approx - \left( A_{win} \cdot \nabla_\theta \log \pi_\theta(y_{win}) + A_{lose} \cdot \nabla_\theta \log \pi_\theta(y_{lose}) \right)$$  

代入 $A$ 值：  

$$\nabla_\theta \mathcal{L}_{GRPO} \propto - \left( \nabla_\theta \log \pi_\theta(y_{win}) - \nabla_\theta \log \pi_\theta(y_{lose}) \right)$$  

### 2.3 结论  

对比上述两个公式可见，在二元对比的条件下，GRPO 与 DPO 的梯度方向完全一致。它们都遵循相同的优化范式：**提升正样本概率（PSR），降低负样本概率（NSR）** 。  

## 3. GRPO 对 DPO 的范式扩展：从 Pair 到 Group + 从预定义到verfiable  

虽然微观梯度一致，但 GRPO 通过引入 Group 机制，重新定义了对比的边界：  

### 3.1 重新定义 Win/Lose 集合  

- **DPO**：依赖外部显式构造的 $(y_w, y_l)$ 对，正负关系是固定的。  
    
- **GRPO**：依赖可验证的奖励。  
    
    - **Win Set**：$r = 1$ （优于平均水平的样本）  
        
    - **Lose Set**：$r = 0$ （劣于平均水平的样本）  
        
    - 这意味着样本的“好坏”完全依赖于数学估计器。  
        

### 3.2 对比维度的升维  

- **Pair-wise (DPO)**：样本 $A$ 必须优于样本 $B$。  
    
- **Pair-Set-wise (GRPO)**：通过对集合A和集合B的对比来进行提升。  
    

## 4. 总结  

在 Outcome-based 的蒸馏任务中，GRPO 并非一种全新的强化学习机制，而是 DPO 在多样本采样场景下的统计学变体。  

- **本质机制**：二者均通过正向与负向信号的组合来调整模型分布 。  
    
- **区别**：DPO 使用固定的配对和 Sigmoid 隐式加权；GRPO 使用动态的集合划分和标准化（Normalization）显式加权。GRPO 允许“多个胜者”并存，这在需要探索多样性解法的推理任务中具有更高的灵活性。  