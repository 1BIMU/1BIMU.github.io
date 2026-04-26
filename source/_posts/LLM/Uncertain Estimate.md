---
categories:
  - Meachine Learning
tags:
  - LLM
mathjax: "true"
title: Uncertain Estimate
date: 2026-04-27 00:35:26
---


### 1. 无监督UQ方法 (Unsupervised UQ Methods)  

这类方法不需要额外的标注数据，直接利用模型在推理时产生的信息来评估不确定性。  

#### A. 基于信息论的方法 (Information-Theoretic)  

这类方法主要分析模型输出的概率分布。  

*   **序列概率 (Sequence Probability)**  
    *   **思想**: 最直接的方法，认为一个好的、可信的回答，其整个序列的生成概率应该更高。  
    *   **公式**: 置信度 $C_{SP}$ 是序列对数概率的总和：  
        $$C_{SP}(y^{*},x) = \log P(y^{*}|x) = \sum_{j=1}^{L} \log P(y_{j}^{*}|y_{<j}^{*},x)$$  
    *   **缺点**: 这个指标天然偏爱较短的序列。  

*   **困惑度 (Perplexity)**  
    *   **思想**: 通过对序列长度进行归一化，来缓解序列概率对长度的偏见。  
    *   **公式**: 对序列的对数概率按长度取平均：  
        $$C_{PPL}(y^{*},x) = \frac{1}{L} \sum_{j=1}^{L} \log P(y_{j}^{*}|y_{<j}^{*},x)$$  

*   **平均词元熵 (Mean Token Entropy, MTE)**  
    *   **思想**: 如果模型在某个位置上对下一个词元的预测分布很分散（熵很高），说明它不确定要生成哪个词，因此整体不确定性也高。  
    *   **公式**: 计算每个位置上词汇表分布的熵，然后取平均值：  
        $$C_{MTE}(y^{*},x) = \frac{1}{L} \sum_{j=1}^{L} \sum_{t\in\mathcal{V}} P(y_{j}^{*}=t|y_{<j}^{*},x) \log P(y_{j}^{*}=t|y_{<j}^{*},x)$$  

*   **蒙特卡洛序列熵 (Monte-Carlo Sequence Entropy, MCSE)**  
    *   **思想**: 直接计算整个输出空间 $P(y|x)$ 的熵是不可行的，因此通过从模型中采样N个序列来近似计算。  
    *   **公式**: 对采样出的每个序列的负对数概率求平均：  
        $$U_{MCSE}(x) = -\frac{1}{N} \sum_{i=1}^{N} \log P(y^{i}|x)$$  
    *   同样有长度归一化的版本 MCNSE。  

#### B. 基于一致性的方法 (Consistency-based)  

这类方法通过生成多个候选答案，然后评估它们之间的一致性来判断不确定性。  

*   **频率评分 (Frequency Scoring)**  
    *   **思想**: 一个可信的答案应该会得到其他多个采样答案的支持（蕴含），而很少被反驳（矛盾）。  
    *   **公式**: 计算蕴含关系的样本数减去矛盾关系的样本数：  
        $$C_{FreqScore}(y^{*},x) = \sum_{j=1}^{N} 1[\text{NLI}(y^{*},y^{j}) = \text{'e'}] - \sum_{j=1}^{N} 1[\text{NLI}(y^{*},y^{j}) = \text{'c'}]$$  

*   **语义熵 (Semantic Entropy)**  
    *   **思想**: 直接比较词法相似度可能会误判，更好的方法是先将语义相似的句子聚类，再计算这些“语义簇”上的熵。  
    *   **公式**: 对每个语义簇 $\mathcal{C}_{m}$ 的总概率进行加权求和：  
        $$U_{SE} = -\frac{1}{N} \sum_{m=1}^{M} |\mathcal{C}_{m}| \log \hat{P}_{m}(x), \quad \text{其中 } \hat{P}_{m}(x) = \sum_{y\in\mathcal{C}_{m}} P(y|x)$$  

#### C. 混合方法 (Hybrid Methods)  

*   **CoCoA**  
    *   **思想**: 将基于信息论的置信度 (Confidence) 与基于一致性的置信度 (Consistency) 结合起来，因为它们能从不同角度互补。  
    *   **公式**: 将两种置信度简单相乘：  
        $$C_{CoCoA}(y^{*},x) = C_{inf}(y^{*},x) \cdot C_{cons}(y^{*},x)$$  

#### D. 言语化不确定性 (Verbalized Uncertainty)  

*   **思想**: 最直接的方式，直接向模型提问，让它评估自己答案的正确性。  
*   **P(True)**  
    *   **方法**: 给定问题和模型生成的答案，构造一个新的提示（Prompt）问模型这个答案是“True”还是“False”，然后计算模型生成“True”这个词元的概率。  
    *   **公式**：  
        $$C_{PTrue}(y^{*}) = P(\text{"True"}|x,y^{*})$$  

---  

### 2. 自省式UQ方法 (Introspective Methods)  

这类方法是白盒（White-box）方法，需要访问模型的内部状态，如隐藏层表示和注意力权重。  

*   **马氏距离 (Mahalanobis Distance, MD)**  
    *   **思想**: 在模型的隐藏特征空间中，正确/可信的回答应该聚集在一起。通过计算一个新回答的隐藏状态与这个“可信集群”中心的马氏距离，可以判断其是否异常（不确定）。  
    *   **公式**：  
        $$U_{MD}(x,l) = (h_{l}(x)-\mu)^{T}\Sigma^{-1}(h_{l}(x)-\mu)$$  
        其中 $h_l(x)$ 是第 $l$ 层的隐藏状态，$ \mu $ 和 $\Sigma$ 是从参考数据中计算出的均值和协方差矩阵。  

*   **循环注意力UQ (Recurrent Attention-based UQ, RAUQ)**  
    *   **思想**: 模型在生成幻觉时，其注意力模式会与生成正确内容时不同。RAUQ利用注意力权重，将前一个词元的不确定性传播到当前词元。  
    *   **公式**: 其核心是循环计算置信度 $c_l(y_i)$：  
        $$c_l(y_i) = \begin{cases} P(y_i | x), & \text{if } i=1 \\ \phi \cdot P(y_i | y_{<i}, x) + (1 - \phi) \cdot a_{l, h_l, i, i-1} \cdot c_l(y_{i-1}), & \text{if } i>1 \end{cases}$$  
        这个公式结合了当前词元的生成概率和由注意力权重 $a$ 调节的前一词元的置信度 $c_l(y_{i-1})$。  

---  

### 3. 数据驱动的监督UQ方法 (Data-Driven UQ Methods)  

这类方法通过在一个标注了“幻觉/非幻觉”的数据集上进行训练，学习一个专门用于预测不确定性的模型。  

*   **SAPLMA**  
    *   **思想**: 直接在LLM的解码器隐藏层激活值上训练一个分类器，来预测模型何时是不确定的。  