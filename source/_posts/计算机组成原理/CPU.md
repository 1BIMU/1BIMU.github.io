---
title: CPU
date: 2025-05-08 15:48:49
categories:
  - 计算机
tags:
  - 计算机组成原理
mathjax: "true"
---

## 具体功能  
- 指令控制：程序的顺序控制  
- 操作控制：控制部件正确执行  
- 时间控制：控制操作信号的持续时间，时间顺序  
- 数据加工：算术逻辑运算  
- 中断处理：异常情况进行处理  

## CPU模型  

![](/IMG/Pasted%20image%2020250612212536.png)  

## CPU寄存器  

### 用户可见寄存器  
用于减少访存次数，由汇编程序员调用  

### 用户不可见寄存器  
控制部件使用，控制CPU的操作  

### 运算器寄存器  
![](/IMG/image-1.png)  

### 存储器寄存器  
![图片描述](/IMG/image-3.png)  

## 指令模型  

### 指令周期  
![图片描述](/IMG/image-5.png)  
如上所示，一条完整的指令周期，至少需要分别经历取指阶段和执行阶段  
对于间址周期，不一定每次都采用，而是只有需要间接寻址的指令，才需要这个周期  

#### 取指周期  
核心任务：根据PC中的内容，从主存中取出指令代码，放置于IR寄存器，PC自加1  
数据流大概如下：  
1、从PC发地址到存储器  
2、从CU发出读命令  
3、从存储器拿到数据，存到IR  
4、PC自加一  

#### 间址周期  
核心任务：==取操作数有效地址==。  
数据流：  
1、IR/MDR的地址到MAR  
2、CU发出读命令到主存  
3、主存数据流向MDR  

#### 执行周期  
核心任务：取操作数，根据IR中的指令字的操作码通过ALU产生结果，无固定数据流  

#### 中断周期  
核心任务：处理中断请求。  
假设断点存入堆栈，SP指向栈帧地址，进栈操作先修改栈顶指针，后存入数据。  
数据流：  
1、先将栈顶指针-1，然后将SP中的地址存入主存（保存当前栈空间，后续用栈的话，只会增加空间然后用）  
2、CU发出写命令，将SP地址写入主存  
3、PC地址存入主存  
4、最后将中断服务程序的开始地址给到PC  

### 指令执行方案  

#### 单周期处理器  
特点：  
1、每条指令在一个CPU周期内完成  
2、串行执行  

#### 多周期处理器  
1、每条指令为期选择不同的执行步骤，需要几个周期，就给几个  
2、串行执行  

#### 流水线处理器  
1、并行执行  

# 控制器  

## 结构与功能  
![图片描述](/IMG/image-6.png)  
控制器的核心功能：  
1、从主存中取出一条指令，并指出下一条指令在主存中的位置    
2、对指令进行译码，产生相应的控制信号    
3、指挥并控制CPU、主存、输入输出设备之间的数据流动方向    

## 硬布线控制器  

### 主要构成  
硬布线控制器的主要构成是通过逻辑门电路和触发器构成的。根据指令要求，当前时序和外部状态  

### 输入输出流  
输入：  
- 指令经过译码产生的指令信息  
- 时钟脉冲  
- 执行单元的反馈标志  
输出：  
- 具体的控制信号  

### 特点  
速度主要由电路延迟决定，CPU核心部件往往用硬布线实现。控制信号一般先由逻辑式列出，经过化简后用电路实现，因此，电路往往比较杂乱且难以修改。  

## 微程序控制器  

### 基本概念  
将指令编写成一个微程序，每个微程序包含若干微指令，每条微指令对应若干微操作命令，因此，执行一条微指令的过程就是执行一个微程序的过程。微程序基本存储在一个控制存储器中。  
- 微命令：控制部件向执行部件发出的控制命令称为微命令，是构成控制序列的最小单位。例如：打开某个控制门的电位信号。当然，有些微命令是互斥的，比如同时对一个双端口的存储器打开写入信号  
- 微操作：执行部件收到微命令后执行的操作称为微操作  
- 微指令：若干微命令的集合，一般包含两部分信息：①操作控制字段：用于产生某一步操作所需要的各种操作控制信号    ②顺序控制字段：用于控制下一条要执行的微指令地址  
- 微周期：从存储器取出并执行一条微指令所需的全部时间，通常为一个时间周期  

### 软硬件构成  

#### 控制存储器(CM)  
用于存放微程序，在CPU内部，用ROM实现，存放微指令的控制存储器的单元地址称为微地址  

#### 微程序的概念  
微程序可以看作是对指令的一种实现，是机器指令的实时解释器，由计算机设计者事先编制好存放于控制存储器中。对于程序员来说，微程序的设计是透明的。  

### 寄存器  
![寄存器](/IMG/Pasted%20image%2020250507182103.png)  

### 微程序控制器的组成和工作过程  

### 组成  
![微程序控制器的组成](/IMG/Pasted%20image%2020250507182229.png)  
1、起始和转移地址形成部件：用于产生初始和后继地址  
2、微指令地址寄存器：接收微地址形成部件送来的微地址，为读取指令做准备（类似于IR）  
3、控制存储器：微程序控制器的核心部件，用于存放各指令对应的微程序  
4、微指令寄存器：位数等于微指令字长。（类似于PC寄存器）    

### 工作过程  
1、执行取指令公共操作。将**取指微程序**(注意，这里的意思是一个单独的特定的微程序，一般位于CM的0号单元)的入口送入$\mu PC$，然后从控制存储器中读出相应的微指令并送入$\mu IR$中。其目的是将取出的机器指令存入IR中。  
2、将机器指令的操作码字段，经过微地址形成部件，产生对应的微程序的入口地址，送入$\mu PC$  
3、从CM中逐条取出对应的微指令并执行  
4、执行完微程序后，回到取指程序的入口地址，继续取下一条指令  

### 微指令的编码方式  
目标：在保证速度的前提下，尽量缩短微指令的字长  

#### 直接编码  
![直接编码](/IMG/Pasted%20image%2020250508143958.png)  
直接编码的好处在于，无需进行译码，只需要将微命令的对应位置设为1即可，每个微命令对应数据通路的一个微操作  
缺点：微指令字长过长，n个微命令就要求微指令的字长有n位，控制存储器容量极大  

#### 字段直接编码  
分段原则：将相容性的微命令分在不同字段，把互斥性的命令分为一个字段，这样确保同一时刻只能执行相容性的微命令，同时可以利用译码器进行压缩，缩短字长。  
![字段直接编码](/IMG/Pasted%20image%2020250508144941.png)  
一般来说，每个小段还要留出一个状态，表示本字段不发出任何命令，通常用0填充，代表不发出任何命令。  

#### 字段间接编码  
简单来说，就是一个字段中的微命令，可能需要依靠其他字段的某些微命令来解释，这种方式可以进一步缩短字长，但是削弱了并行执行的能力，因此，通常作为直接编码的一种辅助手段。  

### 微指令的地址形成方式  
1、断定方式：由微指令的后继地址字段直接指出。  
2、根据机器指令的操作码形成。即微程序指令的首地址的获取方式  
3、增量计数器法：即$(\mu PC) = (\mu PC)+1$  
4、根据各种标志决定下一条微指令分支转移的地址（涉及到执行部件）  
5、由硬件直接产生微程序的入口，比如取指微指令，由专门的硬件电路产生。  

### 微指令的格式  
微指令的格式和微指令的编码方式有关。  

#### 水平微指令  
前面讲过的直接编码，字段直接编码，字段间接编码都属于水平型微指令，其基本格式如下图所示：  
![水平微指令](/IMG/Pasted%20image%2020250508150003.png)  
优点：微程序短，并行能力强，执行速度快  
缺点：微指令较长，编写微程序较麻烦。  

#### 垂直微指令  
![垂直微指令](/IMG/Pasted%20image%2020250508150721.png)  
采用类似机器指令操作码的方式，在微指令字段中设置微操作码字段，一条微指令通常只能执行一种微命令。（说白了就是一次一条控制信息）  
优点：微指令短，便于编写，简单、规整。  
缺点：微程序长，执行速度慢，效率低。  

## 控制器总结  
![对比](/IMG/Pasted%20image%2020250508151012.png)  

# 指令流水线  

## 基本概念  
从两方面提高处理机的并行性能：  
1、时间上的并行  
2、空间上的并行  

### 具体措施  
将一条指令的执行过程分为五个阶段，每个阶段视为一个流水段  
- 取指IF：从指令存储或Cache中取指令  
- 译码ID：操作控制器对指令进行译码，同时从寄存器堆中取操作数  
- 执行EX：执行运算操作或计算地址  
- 访存MEM：对存储器进行读/写操作  
- 写回WB：将指令执行结果写回寄存器堆  
则流水线过程如下：  
![流水线](/IMG/Pasted%20image%2020250508164451.png)  
可以看出，在理想情况下，每个时钟周期都有一条指令进入流水线，每个时钟周期都有一条指令完成，每条指令的CPI=1  

### 对指令集的要求  
- 指令长度尽量一致  
- 指令格式尽量规整  
- 采用Load或者Store类型指令，其余指令不可访存，方便处理在同一周期  
- 数据按边界对齐  

## 流水线的实现  

### 设计原则  
1、流水段个数以最复杂指令所用功能段个数为准(木桶效应)  
2、流水段的长度以最复杂的操作所花的时间为准。  
由此可见，流水线方式并不能缩短单条指令的执行时间，但对于整个程序来说,执行效率得到了大幅提高  

### 流水线的逻辑结构  
每个流水段后面都要增加一个流水段寄存器，用于锁存本段处理完的所有数据，以保证本段的执行结果能在下个周期给下一流水线使用。  
为了确保流水线的正常运行，采用统一的时钟周期，每来一个时钟，各段处理完的数据都将锁存到段尾的流水线寄存器中，作为后段的输入，前段也会收到前段通过流水段奇存器传递过来的数据。  
![流水线的逻辑结构](/IMG/Pasted%20image%2020250508165820.png)  

### 流水线的时空图  
时空图可以直观的描述流水线的运行情况，横坐标表示时间，纵坐标表示空间，即当前指令所处的功能部件。  
![时空图1](/IMG/Pasted%20image%2020250508170021.png)  
![时空图2](/IMG/Pasted%20image%2020250508170055.png)  
从第一张图，我们可以看出，10T时刻共计输出了6条指令  
但是如果正常运行，那么10T最多能输出2条指令  
可见，流水线提高了3倍的CPU速度  

## 流水线的冒险  
为了方便下面的讲解，我先列出三类指令在各个流水段的操作  
![图片描述](/IMG/Pasted%20image%2020250508170803.png)  

### 结构冒险  
概念：不同指令在同一时刻争用同一功能部件而形成的冲突  
本质原因：不同指令在不同的执行阶段会对同一个部件进行访问  
例子：Load的MEM阶段会访问存储，且大部分指令的IF阶段都会访问存储  

解决结构冲突的办法：  
1、停顿法：前一指令访存时，使后一个相关指令暂停一个周期。  
2、对于访问冲突问题，单独设置数据存储器和指令存储器。访问不同的存储器以防止结构冲突  

### 数据冒险  
概念：后面指令用到前面指令的结果时，前面指令的结果还没产生。  
例子：考虑下面这条指令：![eg](/IMG/Pasted%20image%2020250508173000.png)  
在这个指令中，I1指令的目的操作数是I2的源操作数。于是，在时空图中表现如下  
![数据冒险](/IMG/Pasted%20image%2020250508173125.png)  
因此会发生先读后写的冲突。    
解决数据冲突的办法：  
1、停顿法：把遇到数据相关的指令及其后续指令都暂停一至几个时钟周期,直到数拥相关间题消失后再维续执行  
2、转发旁路技术：设置相关转发通路，不等前一条指令把计算结果写回寄存器，下一条指令也不再从寄存器读，而将数据通路中生成的中间数据直接转发到ALU的输入。  
![转发旁路](/IMG/Pasted%20image%2020250508173439.png)  
3、load-use数据冒险的处理：如果load指令后面紧跟运算类指令，由于load的执行过程不会用到ALU，就很难实现旁路转发技术。把这种情况单独独立出来成为load-use数据冒险。  
解决办法：还是只能阻塞，可以把use的指令阻塞一个周期就行。  

### 控制冒险  
概念：遇到改变指令执行顺序的情况，例如执行转移或返回指令、发生中断或异常时，会改变PC值，从而造成断流，也称控制冲突。  
例子：比如说bne指令(branch if not equal)，这种指令需要比较两个操作数的大小，根据EX阶段的结果，来决定MEM阶段是否修改PC的值。对于这样的指令，不执行完它我们是没办法往下执行流水线的。  
解决办法：  
1、阻塞法：插入nop指令（什么都不做），我们把阻塞的时间延时周期称为延时损失时间片C，我们只要插入C条nop指令就可以了。  
2、分支预测法：对转移指令进行分支预测，==尽早生成转移目标地址==。分支预测分为简单(静态)预测和动态预测。若静态预测的条件总是不满是，则按序维续执行分支指令的后续指令。动态预测根据程序转移的历史情况，进行动态预测调整，有较高的预测准确率。  

## 流水线的性能指标  

### 吞吐率  
公式：$$TP = \frac{n}{T_k} = \frac{n}{(k+n-1)\triangle t}$$  
解释：其中，n是任务数，$T_k$是处理完n个任务所用的总时间，$\triangle t$为时钟周期，k为流水线的段数。总思想是，单位时间完成的任务数  

## 加速比  
公式：  
$$\begin{equation}  
S = \frac{T_0}{T_k} = \frac{kn\triangle t}{(k+n-1)\triangle t} = \frac{kn}{k+n-1}  
\end{equation}$$  
解释：思想是：完成同一批任务，不使用流水线技术和使用流水线技术用时之比。  
其中，n是任务数，$T_0$是不适用流水线技术的总时间$T_k$是使用流水线技术的总时间，$\triangle t$为时钟周期，k为流水线的段数。  

