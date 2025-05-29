# 1 实验内容和实验环境  

  

## 1.1 实验环境  

  

<table>  

<tr>  

<td>名称<br/></td><td>参数<br/></td></tr>  

<tr>  

<td>操作系统<br/></td><td>Windows 11 专业版<br/></td></tr>  

<tr>  

<td>软件<br/></td><td>WireShark 4.4.6<br/></td></tr>  

</table>  

  

## 1.2 实验内容  

  

1）捕获在使用网络过程中产生的分组（packet）： IP 数据包、ICMP 报文、DHCP 报文、TCP 报文  

  

段。  

  

2）分析各种分组的格式，说明各种分组在建立网络连接和通信过程中的作用。  

  

3）分析 IP 数据报分片的结构：理解长度大于 1500 字节 IP 数据报分片传输的结构  

  

4）分析 TCP 建立连接、拆除连接和数据通信的过程。  

  

# 2 实验步骤和协议分析  

  

## 2.1 DHCP 报文  

  

### 2.1.1 捕获方法  

  

在过滤器中填写 udp port 67，开始监控。  

  

打开 cmd，使用命令：C:>ipconfig /release，释放主机的 IP 地址  

  

此时得到第一条 DHCP 消息  

  

![](/IMG/As3eb6XQ0ouZvhxxMj7cmmLGnQe.png)  

  

然后输入 C:>ipconfig /renew，重新分配 IP 地址，得到后四条 DHCP 消息  

  

![](static/PdDTbOwP8oEy6xxSPmmccVdhnZg.png)  

  

### 2.1.2 报文内容分析  

  

首先我们看 release 的内容，其报文内容如下所示  

  

![](static/Kp33b3vKQoIRH3xsJuPc8msZnje.png)  

  

我们把鼠标放到  

  

![](static/JZ6ObPuZHozuTwx9JrBc1I3Wntb.png)  

  

上面，可以看到 DHCP 的内容对应在这部分  

  

![](static/RSSabZtxhoM0uPx6jiicsMWEnCg.png)  

  

![](static/XzBDbXlbhoSUEcxapKicwbybnse.png)  

  

我们浏览 DHCP 报文中的内容可以看到，release 相关的内容是在 option 里面的，对应在右侧的 35 01 07  

  

其余 DHCP 报文中的一些包括当前 IP，下一个服务器 IP 和 Relay agent IP address 都是 0.0.0.0，意味着不再请求 IP 地址了。  

  

更具体的，我们点开 option 看到  

  

![](static/Lc6Wb3badoHAYdxPvoyc8Kf3nMd.png)  

  

即，Release 类型的说明，是在 Option 中，标记为 7 的哪个位置，也就是右侧显示的 7  

  

剩下的 Option 信息除了以太网的协议说明，MAC 地址和填充的 0 之外就没啥用了  

  

接下来我们看 renew 过程收发的四个包  

  

![](static/Oclnb1a7Oo9awwxtUbUcl7CBn7d.png)  

  

通过图片我们可以看出，一共有四个类型，分别是 Discover,Offer,Request 和 ACK  

  

联想到我们上课讲过的请求过程，他们分别意味着：  

  

Discover: 由 DHCP Client 发送，采用广播的形式通知网络内的 DHCP 服务器自己需要获得一个 IP 地址。  

  

Offer:DHCP 服务器返回的 DHCP offer，此报文携带了各种配置信息，包含了一个可以分配的 IP 地址，也可以包含 DNS 服务器的地址。(此处有可能收到多个 Offer，因为可能 LAN 内不止一个 DHCP 服务端)  

  

Request:此数据包用于申请 offer 中给出的 IP 地址，此时仍然没有真正获得 IP 地址，所以仍然是广播形式发送。  

  

ACK:DHCP 服务器对客户端的 REQUEST 报文的确认，客户端收到此报文后，才算获得了 IP 地址和相关的配置信息。  

  

#### 观察 Discover 包  

  

其目的地址为 255.255.255.255，即广播包，符合我们的预期。Discover 包是由本机发出，在局域网内广播的包。  

  

其主要内容如下  

  

![](static/MBwkbGg4eoqaLVxH30lcEePEnYb.png)  

  

![](static/EixDb94OHoC6Gyx7lPpc2Zb6nKd.png)  

  

然后我们观察其中的 Option 信息，发现在 Option(50)中，携带了 requested 的 IP 地址，也就是服务器会分配给我们的地址。并且在 Option(53)中，说明了当前的 DHCP 包的类型  

  

#### 观察 Offer 包  

  

Offer 包是 DHCP 服务器发给我们的，这个 Offer 包的 Dst 地址恰好就是我们刚刚 Requested 那个 IP 地址  

  

先展示一下总体信息  

  

![](static/KYPBbs8rBop4VqxVL6gclqDOnKe.png)  

  

然后我们查看细节，发现  

  

![](static/IR56buy9Jo0w4Ixba8ncQFtZn5c.png)  

  

这里变成了类型 2，Reply，和之前的 Request 完全不一样了  

  

然后我们观察一下 Option 的信息  

  

![](static/Hcf5bPOqxoc20BxefMTcQR8jnnc.png)  

  

这里发现，Option(54)中包含了 DHCP 的 Server Identifier，也就是 DHCP 服务器的 IP，这样我们后续就可以告诉全网，我们认可了哪一个 DHCP 服务器分给我们的 IP，避免了 DHCP 服务器资源的浪费。  

  

并且在 Option(51)中给出了 IP Address Lease Time，也就是这个 IP 我还能用多久，可以看到，我还能用 1 小时 28 分钟 36 秒  

  

#### 观察 Request 包  

  

我们首先观察可发现，这依旧是一个广播包。和我们想要通知全网，我们接受了哪个服务器的 IP 的核心功能相适配。  

  

然后我们点开文件，照例先展示内容  

  

![](static/WWalbUKZ9oEeRkx1s0qcpeWEn3g.png)  

  

然后点开 Option 的内容  

  

![](static/Hdknb3DhIoAhRGxghsScQGTJn4g.png)  

  

可以看到，这里仍然放着第一次 Requested 的 IP Address，然后在 Option(54)中展示了接受的 DHCP Server Identifier，即 10.3.9.2（也只收到了一个服务器的 Offer），之前的 discover 中是没有的  

  

这样，就成功通知了 LAN 内的所有 DHCP 服务器，我们已经接受了 10.3.9.2 服务器的 Offer  

  

#### 观察 ACK 包  

  

ACK 包是 DHCP 服务器返回给本机的一个 IP 分配成功的包。其 DST 已经是分配好的 IP 了。  

  

![](static/Lo7xbLJnUom5NOxuGI3cwaycnne.png)  

  

我们点开 Option，看到如下信息  

  

![](static/ZYgGb2DqZoIKrgxVlZFc58IEn9f.png)  

  

首先 DHCP 的消息类型已经被设置为 ACK 了。然后我们可以看到其中包括了 IP 地址的租期，子网掩码，DHCP 服务器识别 IP，以及 Domain Name Server  

  

其实这些用处都不大，主要的目的就是为了告诉本机，我已经成功把资源分配给你了。核心上只要消息类型是 ACK，加上地址租期和 DHCP 服务器的 Identifier 就可以了  

  

### DHCP 协议的功能和分配 IP 地址的过程  

  

通过以上的抓包实验，我们可以很清晰地看出 DHCP 协议的核心功能就是为主机分配 IP 地址。  

  

分配 IP 地址的过程：  

  

1、通过 discover 包向网内广播需要 IP 地址的请求  

  

2、DHCP 服务器通过返回 Offer 包，向主机提供可供分配的 IP 地址，并提供其租期地址  

  

3、本机通过选择心仪的 Offer，向全网广播选择的 DHCP 服务器，其他收到该消息的 DHCP 服务器就会取消掉原来分配的 IP，让出资源  

  

4、被选中的 DHCP 服务返回一个 ACK 包，通知主机，IP 分配成功，并告知 IP 地址的租期，分配过程完毕  

  

## 2.2 ICMP 报文  

  

### 2.2.1 捕获方法  

  

在主窗口设置显示过滤器：icmp&&ip.dst==110.242.68.66(www.baidu.com)，过滤所有的 ICMP 包出来  

  

再在 cmd 中输入命令：ping [www.baidu.com](http://www.baidu.com)  

  

得到结果如下：  

  

![](static/MvFCbalcooc3V4xTABgcxO8pnUb.png)  

  

### 2.2.2 报文内容分析  

  

回想课堂上的内容，我们知道，ICMP 报文是在 IP 数据报中的数据部分。  

  

![](static/SHFAbTucZoCZNyx0xu6cHbbpn0b.png)  

  

因此我们点开对应的 ICMP 协议的包，在数据部分就可以找到 ICMP 协议的包了。  

  

![](static/LI9PbZcB2oOIFMxHhXccLcYRnzf.png)  

  

其中，这部分是 IPV4 的 header 部分，而下面就是 ICMP 协议的报文  

  

![](static/Mt6LbV5ZPo51ySxVRngcbPPdnth.png)  

  

分析可知，该 ICMP 报文的意思是，发出了一个 Echo request(Type 8)，无额外错误细分(Code 0)，校验和正确，Identifier 为 1，Sequence Number 为 11906 的包。  

  

#### ICMP 报文的格式分析并描述各字段的作用  

  

在课本上我们学到，前四个字节是固定的，后四个字节由 ICMP 报文的类型决定，剩下的都是数据部分。我们来对照看一下实际捕获到的 IMCP 包是不是这样的格式。  

  

![](static/Nms8bv3eCoHpPcxSHOXcuavknZd.png)  

  

前四字节中  

  

Type 8 对应数据前面的 08，用于说明 ICMP 的类型，这里是 echo Request 类型。  

  

code:0 对应 00，是代码部分。该部分用于特定报文类型的进一步细化描述。  

  

checkSum 中的 0xc578 对应数据中的 c578，是用于防止传输过程发生错误的校验和检验。  

  

后四字节中，Identifier BE 和 Sequence Number BE 对应后四字节中 0x0001 和 0x2e82 的数据的小端存储结果，而 Identifier LE 和 Sequence Number LE 则是大端的存储结果。  

  

总的来说，后四字节总共存储了两个信息，一个是 Identifier，一个是 Sequence Number。Identifier 用于匹配请求与应答，而 Sequence Number 用于跟踪数据包的发送顺序。  

  

而在最后，它填充了 64 字节的 Data，就是图中显示的一堆 20 了。  

  

总而言之，ICMP 的实际格式和我们在课本上学到的基本一致。  

  

## 2.3 IP 包分段过程  

  

### 2.3.1 捕获方法  

  

在主窗口设置过滤器：ip.dst==10.3.19.2(www.bupt.edu.cn)，这样我们就可以 ping 这个固定的 ip，然后截取 IP 包了  

  

于是我在 CMD 中输入命令：ping -l 8000 [www.bupt.edu.cn](http://www.bupt.edu.cn)  

  

得到结果如下  

  

![](static/CqRdbsy4toPPUlxZGOMcX1WHnQh.png)  

  

### 2.3.2 报文内容分析  

  

我们取第一组的 IPv4 的包进行分析  

  

![](static/SZiub5svhogKJ1x9LjEcRSYcniY.png)  

  

```yaml  

//第一个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 1500  

    Identification: 0x3f96 (16278)  

    1. .... = Flags: 0x1, More fragments  

    ...0 0000 0000 0000 = Fragment Offset: 0  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0x9ba6 [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [Reassembled IPv4 in frame: 23]  

    [Stream index: 5]  

  

//第二个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 1500  

    Identification: 0x3f96 (16278)  

    1. .... = Flags: 0x1, More fragments  

    ...0 0000 1011 1001 = Fragment Offset: 1480  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0x9aed [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [Reassembled IPv4 in frame: 23]  

    [Stream index: 5]  

//第三个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 1500  

    Identification: 0x3f96 (16278)  

    1. .... = Flags: 0x1, More fragments  

    ...0 0001 0111 0010 = Fragment Offset: 2960  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0x9a34 [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [Reassembled IPv4 in frame: 23]  

    [Stream index: 5]  

  

//第四个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 1500  

    Identification: 0x3f96 (16278)  

    1. .... = Flags: 0x1, More fragments  

    ...0 0010 0010 1011 = Fragment Offset: 4440  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0x997b [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [Reassembled IPv4 in frame: 23]  

    [Stream index: 5]  

//第五个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 1500  

    Identification: 0x3f96 (16278)  

    1. .... = Flags: 0x1, More fragments  

    ...0 0010 1110 0100 = Fragment Offset: 5920  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0x98c2 [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [Reassembled IPv4 in frame: 23]  

    [Stream index: 5]  

//第六个包  

Internet Protocol Version 4, Src: 10.129.18.95, Dst: 10.3.19.2  

    0100 .... = Version: 4  

    .... 0101 = Header Length: 20 bytes (5)  

    Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)  

    Total Length: 628  

    Identification: 0x3f96 (16278)  

    0. .... = Flags: 0x0  

        0... .... = Reserved bit: Not set  

        .0.. .... = Don't fragment: Not set  

        ..0. .... = More fragments: Not set  

    ...0 0011 1001 1101 = Fragment Offset: 7400  

    Time to Live: 128  

    Protocol: ICMP (1)  

    Header Checksum: 0xbb71 [validation disabled]  

    [Header checksum status: Unverified]  

    Source Address: 10.129.18.95  

    Destination Address: 10.3.19.2  

    [6 IPv4 Fragments (8008 bytes): #18(1480), #19(1480), #20(1480), #21(1480), #22(1480), #23(608)]  

    [Stream index: 5]  

```  

  

通过以上的结果，我们可以得知：  

  

由于 ICMP 头部的存在，原来的 8000 字节数据变成了 8008 字节。  

  

分析：总共需要传输 8008 个字节的数据，通过上面的结果，我们可知道 MTU = 1500  

  

基于这个来看，由于每个 IP Header 长度为 20 字节，那么每个单元最多传输 1480 个字节的数据。而刚好，1480/8 = 85，说明 1480 这个长度恰好可以被 8 整除，因此无需减少携带量来适应 offset 标识，直接传输 1480 个字节的数据即可。  

  

8008/1480 = 5 余 608，余数恰好和最后一个报文的总长度对应上了。完美的说明了这里是怎么分段的。  

  

我们再看 offset，也和我们的分析一样，第二个分片的偏移量就是我们算出来的 1480。  

  

和我们的分析完美对应。  

  

## 2.4 TCP 建立连接和释放连接过程  

  

### 2.4.1 捕获方法  

  

经过我的实验，我发现，凡是有负载均衡的网页，直接关闭的话，基本上不会触发完整的四次挥手的流程，而是顶多触发到返回一个 ACK 之后，就触发 RST 包了，这显然没法完成实验，因此，我得找没有部署负载均衡的网页。  

  

刚好，之前数据结构课设的时候租了一台服务器，配置过 Web 服务器，因此  

  

在主窗口设置显示过滤器：  

  

ip.dst==8.140.206.115|| ip.src==8.140.206.115  

  

得到结果如下  

  

![](static/IUSubxalco1smBxNebHcoYUlnNf.png)  

  

### 2.4.2 报文内容分析  

  

我将按照三次握手和四次挥手的过程，逐渐描述各消息  

  

#### 第一次握手：客户端 → 服务器  

  

```yaml  

Transmission Control Protocol, Src Port: 6324, Dst Port: 443, Seq: 0, Len: 0  

    Source Port: 6324  

    Destination Port: 443  

    [Stream index: 10]  

    [Stream Packet Number: 1]  

    [Conversation completeness: Complete, WITH_DATA (63)]  

    [TCP Segment Len: 0]  

    Sequence Number: 0    (relative sequence number)  

    Sequence Number (raw): 1180082982  

    [Next Sequence Number: 1    (relative sequence number)]  

    Acknowledgment Number: 0  

    Acknowledgment number (raw): 0  

    1000 .... = Header Length: 32 bytes (8)  

    Flags: 0x002 (SYN)  

    Window: 65535  

    [Calculated window size: 65535]  

    Checksum: 0x028e [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    Options: (12 bytes), Maximum segment size, No-Operation (NOP), Window scale, No-Operation (NOP), No-Operation (NOP), SACK permitted  

    [Timestamps]  

```  

  

![](static/FVkfb8Pp4od3IrxIOVLcwn5gnVg.png)  

  

这是第一次握手的消息，其中：  

  

#### 第二次握手：客户端 ← 服务器  

  

```yaml  

Transmission Control Protocol, Src Port: 443, Dst Port: 1111, Seq: 0, Ack: 1, Len: 0  

    Source Port: 443  

    Destination Port: 1111  

    [Stream index: 3]  

    [Stream Packet Number: 2]  

    [Conversation completeness: Complete, WITH_DATA (63)]  

    [TCP Segment Len: 0]  

    Sequence Number: 0    (relative sequence number)  

    Sequence Number (raw): 4262798856  

    [Next Sequence Number: 1    (relative sequence number)]  

    Acknowledgment Number: 1    (relative ack number)  

    Acknowledgment number (raw): 2334991369  

    1000 .... = Header Length: 32 bytes (8)  

    Flags: 0x012 (SYN, ACK)  

    Window: 8192  

    [Calculated window size: 8192]  

    Checksum: 0x55b5 [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    Options: (12 bytes), Maximum segment size, No-Operation (NOP), Window scale, No-Operation (NOP), No-Operation (NOP), SACK permitted  

    [Timestamps]  

    [SEQ/ACK analysis]  

```  

  

![](static/R9CPb2bMgos6AAxehw1c1WaBnrh.png)  

  

这是第二次握手的消息，其中  

  

#### 第三次握手：客户端 → 服务器  

  

```yaml  

Transmission Control Protocol, Src Port: 1111, Dst Port: 443, Seq: 1, Ack: 1, Len: 0  

    Source Port: 1111  

    Destination Port: 443  

    [Stream index: 3]  

    [Stream Packet Number: 3]  

    [Conversation completeness: Complete, WITH_DATA (63)]  

    [TCP Segment Len: 0]  

    Sequence Number: 1    (relative sequence number)  

    Sequence Number (raw): 2334991369  

    [Next Sequence Number: 1    (relative sequence number)]  

    Acknowledgment Number: 1    (relative ack number)  

    Acknowledgment number (raw): 4262798857  

    0101 .... = Header Length: 20 bytes (5)  

    Flags: 0x010 (ACK)  

    Window: 255  

    [Calculated window size: 65280]  

    [Window size scaling factor: 256]  

    Checksum: 0xb53c [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    [Timestamps]  

    [SEQ/ACK analysis]  

```  

  

![](static/EJGNb4aBCo3HTVxxRj3c2iOynuc.png)  

  

这是第三次握手的消息，其中：  

  

三次握手过程已完成  

  

### 完整三次握手流程总结：  

  

#### 第一次挥手（主动关闭方 → 被动关闭方）  

  

```yaml  

Transmission Control Protocol, Src Port: 443, Dst Port: 1039, Seq: 25, Ack: 1, Len: 0  

    Source Port: 443  

    Destination Port: 1039  

    [Stream index: 9]  

    [Stream Packet Number: 2]  

    [Conversation completeness: Incomplete (28)]  

    [TCP Segment Len: 0]  

    Sequence Number: 25    (relative sequence number)  

    Sequence Number (raw): 476391171  

    [Next Sequence Number: 26    (relative sequence number)]  

    Acknowledgment Number: 1    (relative ack number)  

    Acknowledgment number (raw): 3666162612  

    0101 .... = Header Length: 20 bytes (5)  

    Flags: 0x011 (FIN, ACK)  

    Window: 67  

    [Calculated window size: 67]  

    [Window size scaling factor: -1 (unknown)]  

    Checksum: 0x616b [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    [Timestamps]  

```  

  

![](static/PpHPb1kDEoXBm3xFK10cKtBantd.png)  

  

这是第一次挥手的消息，由服务端端口 443 主动发起，其中：  

  

#### 第二次挥手（被动关闭方 → 主动关闭方）  

  

```yaml  

Transmission Control Protocol, Src Port: 1039, Dst Port: 443, Seq: 1, Ack: 26, Len: 0  

    Source Port: 1039  

    Destination Port: 443  

    [Stream index: 9]  

    [Stream Packet Number: 3]  

    [Conversation completeness: Incomplete (28)]  

    [TCP Segment Len: 0]  

    Sequence Number: 1    (relative sequence number)  

    Sequence Number (raw): 3666162612  

    [Next Sequence Number: 1    (relative sequence number)]  

    Acknowledgment Number: 26    (relative ack number)  

    Acknowledgment number (raw): 476391172  

    0101 .... = Header Length: 20 bytes (5)  

    Flags: 0x010 (ACK)  

    Window: 253  

    [Calculated window size: 253]  

    [Window size scaling factor: -1 (unknown)]  

    Checksum: 0x60b1 [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    [Timestamps]  

    [SEQ/ACK analysis]  

```  

  

![](static/X7DdbVfRholDEXxzYekcJDVNnrf.png)  

  

这是第二次挥手的消息，由客户端反馈给服务端，其中：  

  

#### 第三次挥手（被动关闭方 → 主动关闭方）  

  

```yaml  

Transmission Control Protocol, Src Port: 1039, Dst Port: 443, Seq: 1, Ack: 26, Len: 0  

    Source Port: 1039  

    Destination Port: 443  

    [Stream index: 9]  

    [Stream Packet Number: 4]  

    [Conversation completeness: Incomplete (28)]  

    [TCP Segment Len: 0]  

    Sequence Number: 1    (relative sequence number)  

    Sequence Number (raw): 3666162612  

    [Next Sequence Number: 2    (relative sequence number)]  

    Acknowledgment Number: 26    (relative ack number)  

    Acknowledgment number (raw): 476391172  

    0101 .... = Header Length: 20 bytes (5)  

    Flags: 0x011 (FIN, ACK)  

    Window: 253  

    [Calculated window size: 253]  

    [Window size scaling factor: -1 (unknown)]  

    Checksum: 0x60b0 [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    [Timestamps]  

```  

  

![](static/Pb7hbUJXkoLFTnxlfOYcLSjEn8d.png)  

  

这是第三次挥手的消息，由客户端反馈给服务端，其中：  

  

#### 第四次挥手（主动关闭方 → 被动关闭方）  

  

```yaml  

Transmission Control Protocol, Src Port: 443, Dst Port: 1039, Seq: 26, Ack: 2, Len: 0  

    Source Port: 443  

    Destination Port: 1039  

    [Stream index: 9]  

    [Stream Packet Number: 5]  

    [Conversation completeness: Incomplete (28)]  

    [TCP Segment Len: 0]  

    Sequence Number: 26    (relative sequence number)  

    Sequence Number (raw): 476391172  

    [Next Sequence Number: 26    (relative sequence number)]  

    Acknowledgment Number: 2    (relative ack number)  

    Acknowledgment number (raw): 3666162613  

    0101 .... = Header Length: 20 bytes (5)  

    Flags: 0x010 (ACK)  

    Window: 67  

    [Calculated window size: 67]  

    [Window size scaling factor: -1 (unknown)]  

    Checksum: 0x616a [unverified]  

    [Checksum Status: Unverified]  

    Urgent Pointer: 0  

    [Timestamps]  

    [SEQ/ACK analysis]  

```  

  

![](static/N704bBwOMoyvx5xwnwMckIjPnEg.png)  

  

这是第四次挥手的消息，是服务端反馈给客户端的，其中：  

  

### 四次挥手完整流程总结：  

  

### 2.4.3 TCP 三次握手流程图  

  

![](static/ZOtMbFktIo9mcbxAX2VcfwLRn8f.png)  

  

### 2.4.4 TCP 四次挥手流程图  

  

![](static/NX7XbyMTToao9ExE1aecFVvhnTb.png)  

  

# 3 实验结论和实验心得  

  

我用了大约 5 小时左右，超出了 2~3 小时的预测。第一遍实验用时 30 分钟，后面发现 TCP 在挥手的过程中，如果是大公司的网站，有负载均衡的那种，很容易触发 RST 类型的包，导致无法见到完整的四次挥手的过程。为了解决这点花了大概有一个小时左右，才发现可以用自己的服务器解决。其实还有一个办法就是在自己本地的端口写一个简单的 Web 服务器，这样应该就可以看到完整的 TCP 挥手过程。不过我这里是发现可以用自己远程部署的很少人访问的微型服务器来解决。  

  

总结本次实验，我对 DHCP 包进行动态分配 IP、ICMP 包处理 echo request 和 echo reply、IP 包的分段以及 TCP 建立连接和释放连接的过程更加的清晰了。这对我进行计算机网络的学习帮助很大，我能够更好的理解一下网络中的协议设计的原理，比如 TCP 为什么要三次握手，四次挥手，比如为什么 DHCP 的主机要发两次广播包。我的计网知识面得到了极大的拓宽。  