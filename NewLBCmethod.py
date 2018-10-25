 #!/usr/bin/python
import model_calc as MC
import queue
import copy


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

    MsgBandwidth = [0.0]*len(Msg_List)
    MsgTimeCounter = [0.0]*len(Msg_List)
    MsgSendReady = [0,0]*len(Msg_List)#ready packet number ,PSN
    MsgSendedNum = [0]*len(Msg_List)

    NodeStartEdgeMsg = InitStartNodeEdge(G,Msg_List)
    
    #初始化每条边上通过的消息集合
    LinkEdges = {}
    for l in G.Edges:
        LinkEdges[l] = set()            

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