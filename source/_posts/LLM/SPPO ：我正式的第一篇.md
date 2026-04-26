---
categories:
  - Meachine Learning
tags:
  - LLM
mathjax: "true"
title: SPPO ：我的第一篇
date: 2025-11-10 22:08:13
---
关于这个工作，其实已经构思了很久了...  
一直觉得，GRPO明明是一个工程的近似产物，但是却在RLVR上面比PPO表现好那么多，实在是一个让人费解的问题。  
因此我开始深入思考原因。  

# GRPO和PPO的本质区别是什么？  
一个很粗浅的回答是：Advantage的区别。  
但是实际整个Framework被GRPO改了很大一部分。其实际的train_batch_size是$N_{samples} \times N_{batch_size}$  
但是真正要思考的问题是，差的是Advantage的哪部分呢？  
