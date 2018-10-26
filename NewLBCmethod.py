 #!/usr/bin/python
import model_calc as MC
import queue
import copy
import math

class packet:
    def __init__(self,MGid = 0,psn = 0):
        self.MsgGid = MGid
        self.Psn = psn
        self.step = 1
#[MsgGId,MsgSize,MessageStartNode.Lid,MessageEndNode.Lid]
def NewLBC_Estimate(G, Msg_List):
    print("Lets start")
    #算法要求离线计算，并且具有足够的速度
    #降低使用dict，set数据结构的频次

    #局部数据初始化
    MsgNum = len(Msg_List)
    FinishedMsgNum = 0

    EdgeRoundRobinIndex = [0]*len(G.Edges)
    RouterInputbuffsQ = Init_queue(G)  
    EdgeInputQ = InitOutPacketBuf(G)

    NodeStartEdgeMsg = InitStartNodeEdge(G,Msg_List)


    MsgBandwidth = InitMsgStartBandwidth(Msg_List,NodeStartEdgeMsg,G)
    MsgTimeCounter = [0.0]*len(Msg_List)
    MsgSendReady = [[0,1]]*len(Msg_List)#ready packet number ,PSN
    MsgSendedNum = [0]*len(Msg_List)

    
    #初始化每条边上通过的消息集合
    LinkEdges = {}
    for l in G.Edges:
        LinkEdges[l] = set()            

    #开始计算
    while FinishedMsgNum != MsgNum:
        #第一步：根据消息的带宽，向网络中注入流量
        for InNode in G.InNode:
            for OutEdge in InNode.OutEdges:
                #validsize = 0
                t = len(NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid])
                for i  in range(0,t):
                    msgGid = NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid][i]
                    temp = MsgTimeCounter[msgGid] + float(MsgBandwidth[msgGid])
                    remain_size = Msg_List[msgGid][1] - MsgSendedNum[msgGid]
                    max_send = math.floor(temp)
                    real_send = min(remain_size,max_send)
                    MsgSendedNum[msgGid] += real_send
                    # if real_send != 0:
                    #     print("check %d"%(real_send))
                    # if MsgSendedNum[msgGid] == Msg_List[msgGid][1] :
                    #     #此时消息已经发送完毕
                    #     MsgTimeCounter[msgGid] = 0.0
                    # else:
                    #     #msgGid消息还有剩余
                    #     #NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid][validsize] = NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid][i]
                    MsgTimeCounter[msgGid] = temp - float(max_send)
                        #validsize+=1
                    MsgSendReady[msgGid][0] += real_send
                #开始裁剪NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid]
                #NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid] = NodeStartEdgeMsg[InNode.Lid][OutEdge.SourceLid][:validsize]
        #第二步：更新每一个Edge的输入Q
        for e in G.Edges:
            if e.Start.type == 0:
                #print("输入边情况")
                EdgeGid = e.Iph_I
                EdgeLid = e.SourceLid
                size = len(NodeStartEdgeMsg[e.Start.Lid][EdgeLid])
                for i in (0,e.bandwidth):
                    #抽取bandwidth个数据包
                    index = EdgeRoundRobinIndex[EdgeGid]
                    # t = 0
                    for t in range(0,size):
                        p = (index + t)% size
                        MsgGid = NodeStartEdgeMsg[e.Start.Lid][EdgeLid][p]
                        if MsgSendReady[MsgGid][0] > 0:
                            EdgeInputQ[EdgeGid].put(packet(MsgGid,MsgSendReady[MsgGid][1]))
                            MsgSendReady[MsgGid][0] -= 1
                            MsgSendReady[MsgGid][1] += 1
                            EdgeRoundRobinIndex[EdgeGid] = (p+1)%size
                            break


            # elif e.Start.type == 1:
            #     #print("边连接的是路由器和别的节点")

#初始化队列
def Init_queue(G)  :
    InputbuffsQ = []
    for r in G.RouterNode:
        temp = []
        for oe in r.OutEdges:
            t = []
            for ie in r.InEdges:
                q = queue.Queue()
                #q.put(ie.label+ " " + r.label+" " + oe.label)
                #print(str(r.Lid)+ " " +str(oe.SourceLid) + " " + str(ie.EndLid))
                t.append(q)
            temp.append(t)
        InputbuffsQ.append(temp)
            #print(InputbuffsQ[r.Lid][oe.SourceLid][ie.EndLid].get())
    # for r in G.RouterNode:
    #     for oe in r.OutEdges:
    #         print(RoundRobinIndex[r.Lid][oe.SourceLid])
    #         for ie in r.InEdges:
    #             print(InputbuffsQ[r.Lid][oe.SourceLid][ie.EndLid].get())
    #             print(str(r.Lid)+ " " +str(oe.SourceLid) + " " + str(ie.EndLid))
    return InputbuffsQ

#初始化每条边的开始端口上的buf
def  InitOutPacketBuf(G):
    OutPacketQBuf = []
    for i in range(0,len(G.Edges)):
        OutPacketQBuf.append(queue.Queue())
    # print("packet len %d  Edge Num %d "%(len(OutPacketBuf),len(G.Edges)))
    return OutPacketQBuf


#对于每一个开始边，都要关联一个消息数组，和一个发送队列保存从其边上发送的消息。
def InitStartNodeEdge(G,Msg_List):
    #消息数组
    StartEdgeMessages = []
    for node in G.InNode:
        temp = []
        for outEdge in node.OutEdges:
            temp.append([])
        StartEdgeMessages.append(temp)
    for msg_A in Msg_List:
        msgId = msg_A[0]
        startNLid = msg_A[2]
        endNLid = msg_A[3]
        e = G.MsgRout[startNLid][endNLid][0]
        StartEdgeMessages[e.Start.Lid][e.SourceLid].append(msgId)
    # for node in G.InNode:
    #     print("Node id = %s:"%(node.label))
    #     for e in node.OutEdges:
    #         print("      edge:%s"%(e.label))
    #         for msgId in StartEdgeMessages[e.Start.Lid][e.SourceLid]:
    #             print("      msg:%s"%(G.OutNode[Msg_List[msgId][3]].label))
    return StartEdgeMessages    

#初始化每一条消息的初始带宽
def InitMsgStartBandwidth(Msg_List,NodeStartEdgeMsg,G):
    MsgBandwidth = []
    for msg_A in Msg_List:
        startNLid = msg_A[2]
        endNLid = msg_A[3]
        e = G.MsgRout[startNLid][endNLid][0]
        MsgBandwidth.append(e.bandwidth)
    return MsgBandwidth
