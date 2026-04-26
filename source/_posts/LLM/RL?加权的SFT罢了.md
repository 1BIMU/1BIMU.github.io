---
categories:
  - Meachine Learning
tags:
  - LLM
  - RL
mathjax: "true"
title: RL?加权的SFT罢了
date: 2025-10-15 09:22:24
---
# SFT  
SFT的loss可以写作：  
$$\nabla_\theta L_{SFT} = -\mathbb{E}_{s\sim D,a\sim D}[\nabla_\theta \log(\pi(a|s))]$$  
由于loss是梯度下降，从最大化的角度来说就是$$\nabla_\theta J(\theta)_{SFT} = \mathbb{E}_{s\sim D,a\sim D}[\nabla_\theta \log(\pi(a|s))]$$  
从直觉理解，就是在最大化来自数据集D的一个最大的概率。是一个经典的BC方法。  

# RL  

## PG  
从PG with baseline来看，最终的目标函数是最大化下面的目标：  
$$\nabla_\theta J(\theta) = \mathbb{E}_{s\sim D,a\sim \pi_\theta}[\nabla_\theta \log(\pi(a|s))\hat A(s,a)]$$  
从哲学角度思考，这样的目标是，通过$\hat A(s,a)$评价每个自采样的token，来改变每个token的梯度。从而能够达到自己拟合自己的结果  

## PPO  
PPO-CLIP的梯度最后可以优化到这样$$\nabla J^{CLIP}(\theta)=\mathbb{E}_t\left[\mathbb{I}\cdot\left(r_t(\theta)\cdot\nabla_\theta\log\pi_\theta(a_t|s_t)\cdot\hat{A}_t\right)\right]$$  
最后的梯度取会多一个重要性采样，以及指示函数所保证的，对于在正advantage下clip过高的梯度，在负advantage下clip过低的梯度，防止学习过于激进。  
（这里的指示函数的意思是没有被clip的意思，被clip梯度为0）  

# RL和SFT的根本区别  

- RL的动作来源于自己，这个动作和自己本身的分布相符，在更新的时候不会导致梯度过大过于尖锐，很难学。  
- RL的advantage作为token梯度的加权项，正确的选择了那些做得好的token。一定程度上给予他们较大的梯度，同时还有一个unlearning的效果，对于做的不好的token，他还有一个负方向的梯度。  
- CLIP机制带来的token masking的效果。可以屏蔽掉过低的梯度，防止学习过于激进  

