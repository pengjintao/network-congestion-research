 #!/usr/bin/python
import model_calc as MC
import queue
import copy
import math

class packet:
    def __init__(self,MGid = 0,psn = 0):
        self.MsgGid = MGid
        self.Psn = psn
        self.step = 0
#[MsgGId,MsgSize,MessageStartNode.Lid,MessageEndNode.Lid]
def NewLBC_Estimate(G, Msg_List):
    print("Lets start")
    #算法要求离线计算，并且具有足够的速度
    #降低使用dict，set数据结构的频次

    #局部数据初始化
    MsgNum = len(Msg_List)
    MsgFinishedList = [0]*MsgNum
    FinishedMsgNum = 0
    time = 0

    EdgeRoundRobinIndex = [0]*len(G.Edges)
    RouterInputbuffsQ = Init_queue(G)
    RouterInputbuffsQMaxSize = 0
    EdgeInputQ = InitOutPacketBuf(G)
    EdgeCreditMax = 16
    EdgeCredit = []
    for e in G.Edges:
        EdgeCredit.append(EdgeCreditMax)

    NodeStartEdgeMsg = InitStartNodeEdge(G,Msg_List)


    MsgBandwidth = InitMsgStartBandwidth(Msg_List,NodeStartEdgeMsg,G)
    MsgTimeCounter = [0.0]*len(Msg_List)
    MsgSendReady =[]# [[0,1]]*len(Msg_List)#ready packet number ,PSN
    for msg in Msg_List:
        MsgSendReady.append([0,1])
    MsgSendedNum = [0]*len(Msg_List)

    #初始化每条边上通过的消息集合
    LinkMsgs = {}
    for l in G.Edges:
        LinkMsgs[l] = set()


    #测试用代码，用于保存每条边上通过的消息
    EdgeCheck = {}
    for e in G.Edges:
        EdgeCheck[e.label] = []
    #开始计算
    while FinishedMsgNum != MsgNum:
        time += 1
        #print("time = %d"%(time))
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
                    #print("read_send =%d "%real_send)
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
        #print("MsgSendReady[0][1] = %d"%(MsgSendReady[0][1]))
        for e in G.Edges:
            if e.Start.type == 0:
                #print("输入边情况")
                EdgeGid = e.Iph_I
                EdgeLid = e.SourceLid
                size = len(NodeStartEdgeMsg[e.Start.Lid][EdgeLid])
                #print(size)
                for i in range(0,min(e.bandwidth,EdgeCredit[e.Iph_I])):
                    #抽取bandwidth个数据包
                    index = EdgeRoundRobinIndex[EdgeGid]
                    # t = 0
                    for t in range(0,size):
                        #print("check %d %d"%(i,e.bandwidth))
                        p = (index + t)% size
                        #print(p)
                        MsgGid = NodeStartEdgeMsg[e.Start.Lid][EdgeLid][p]
                        #print("MsgSendReady[MsgGid][0] = %d"%(MsgSendReady[MsgGid][0]))
                        if MsgSendReady[MsgGid][0] > 0:
                            #print(G.InNode[Msg_List[MsgGid][2]].label + "  " + G.OutNode[Msg_List[MsgGid][3]].label)
                            #print("....MsgGid = %d  packet out %d = %d %s "%(MsgGid,MsgSendReady[MsgGid][1],Msg_List[MsgGid][1],e.label))
                            EdgeCredit[e.Iph_I] -= 1
                            if EdgeCredit[e.Iph_I] < 0:# EdgeCreditMax:
                                print("error warning0")
                            
                            EdgeInputQ[EdgeGid].put(packet(MsgGid,MsgSendReady[MsgGid][1]))
                            if MsgSendReady[MsgGid][1] == 1:
                                #first packet arrive edge e
                           #     print("MsgGid = %d packet in %d   %s "%(MsgGid, Msg_List[MsgGid][1],e.label))
                                LinkMsgs[e].add(MsgGid)
                            if MsgSendReady[MsgGid][1] == Msg_List[MsgGid][1]:
                           #     print("MsgGid = %d  packet out %d = %d %s "%(MsgGid,MsgSendReady[MsgGid][1],Msg_List[MsgGid][1],e.label))
                                LinkMsgs[e].remove(MsgGid)
                            #if MsgGid
                            MsgSendReady[MsgGid][0] -= 1
                            MsgSendReady[MsgGid][1] += 1
                            EdgeRoundRobinIndex[EdgeGid] = (p+1)%size
                            break


            elif e.Start.type == 1:
                #print("边连接的是路由器和别的节点")
                EdgeGid = e.Iph_I
                EdgeLid = e.SourceLid
                RouterLid = e.Start.Lid
                size = len(RouterInputbuffsQ[RouterLid][EdgeLid])
                #pack  = packet()
                for i in range(0,min(e.bandwidth,EdgeCredit[e.Iph_I])):
                    index = EdgeRoundRobinIndex[EdgeGid]
                    for t in range(0,size):
                        p = (index + t)% size
                        if not RouterInputbuffsQ[RouterLid][EdgeLid][p].empty():
                            if e.End.type != 2:
                                EdgeCredit[e.Iph_I] -= 1
                                if EdgeCredit[e.Iph_I] < 0:
                                    print("error warning1")
                            
                            #if e.label == "node15--node18":
                            #    print("check EdgeGid = %d"%(EdgeGid))
                            pack = RouterInputbuffsQ[RouterLid][EdgeLid][p].get()
                            EdgeCredit[G.RouterNode[RouterLid].InEdges[p].Iph_I] += 1
                            if  EdgeCredit[G.RouterNode[RouterLid].InEdges[p].Iph_I] > EdgeCreditMax:
                                print("error warning2")
                            EdgeInputQ[EdgeGid].put(pack)
#                            if pack.Psn == 1:
#                                LinkMsgs[e].add(pack.MsgGid)
#                            if pack.Psn == Msg_List[pack.MsgGid][1]:
#                                #print("")
#                                LinkMsgs[e].remove(pack.MsgGid)
                            EdgeRoundRobinIndex[EdgeGid] = (p+1)%size
                            break
        #第三步：更新每一条边
        for e in G.Edges:
            EdgeTemp = []
            EdgeGid = e.Iph_I
            #if e.label == "node15--node18":
            #    print("start check")
            if e.End.type == 1:
                #print("末端为路由器")
                while not EdgeInputQ[EdgeGid].empty():
                    #if e.label == "node15--node18":
                    #    print("check")

                   #EdgeCheck[e.label].append
                    pack = EdgeInputQ[EdgeGid].get()
                    pack.step += 1
                    MsgGid = pack.MsgGid
                    nextEdge = G.MsgRout[Msg_List[MsgGid][2]][Msg_List[MsgGid][3]][pack.step]

                    
                    EdgeTemp.append(G.InNode[Msg_List[MsgGid][2]].label + "  " + G.OutNode[Msg_List[MsgGid][3]].label)
                    #LinkMsgs
                    if pack.Psn == 1:
                        LinkMsgs[nextEdge].add(MsgGid)
                    if pack.Psn == Msg_List[MsgGid][1]:
                        LinkMsgs[nextEdge].remove(MsgGid)
                    #RouterInputbuffsQ
                    RouterInputbuffsQ[e.End.Lid][nextEdge.SourceLid][e.EndLid].put(pack)
                    if RouterInputbuffsQMaxSize < RouterInputbuffsQ[e.End.Lid][nextEdge.SourceLid][e.EndLid].qsize() :
                        RouterInputbuffsQMaxSize = RouterInputbuffsQ[e.End.Lid][nextEdge.SourceLid][e.EndLid].qsize() 
                #    print("c")
            elif e.End.type == 2:
                #print("末端为接受节点")
                #if not EdgeInputQ[EdgeGid].empty():
                #    print("check")

                #EdgeInputQ[EdgeGid].queue.clear()
                while not EdgeInputQ[EdgeGid].empty():
                    pack = EdgeInputQ[EdgeGid].get()
                    EdgeTemp.append(G.InNode[Msg_List[MsgGid][2]].label + "  " + G.OutNode[Msg_List[MsgGid][3]].label)
                    if pack.Psn == Msg_List[pack.MsgGid][1]:
                        MsgFinishedList[pack.MsgGid] = time
                        FinishedMsgNum += 1
               #         print(FinishedMsgNum)
            EdgeCheck[e.label].append(EdgeTemp)



    # print("all message finished at %d"%(time))
    # msgs = EdgeCheck["node6--node2"]
    # for i in range(0,len(msgs)):
    #     print("time step %d"%(i+1))
    #     for st in msgs[i]:
    #         print("msg: %s"%(st))
    #         # print time
        
        
        #第四步：更新每个消息的带宽
        LinkRemainBandwidth = []
        for e in G.Edges:
            LinkRemainBandwidth.append(e.bandwidth)
        LinkMsgPassingCopy = copy.copy(LinkMsgs)
        for l,data in LinkMsgs.items():
            LinkMsgPassingCopy[l] = copy.copy(LinkMsgs[l])
        e,minBandwidth = get_most_congestion_edge(LinkMsgPassingCopy,LinkRemainBandwidth)
        
      
        #目的时计算每一条消息的有效带宽
        while e != None:
            p = copy.copy(LinkMsgPassingCopy[e])
            for msgGid in p:
                MsgBandwidth[msgGid] = minBandwidth
                #print("msg:%s band:%f"%(MsgLabel(G,Msg_List,MsgGid),minBandwidth))
                for l in G.MsgRout[Msg_List[msgGid][2]][Msg_List[msgGid][3]]:
                    if l in LinkMsgPassingCopy and  msgGid in LinkMsgPassingCopy[l]:
                        LinkMsgPassingCopy[l].remove(msgGid)
                        LinkRemainBandwidth[l.Iph_I] -= minBandwidth
                        if len(LinkMsgPassingCopy[l]) == 0:
                            del LinkMsgPassingCopy[l]
            e,minBandwidth = get_most_congestion_edge(LinkMsgPassingCopy,LinkRemainBandwidth)
    #
    return time,MsgFinishedList,RouterInputbuffsQMaxSize

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

def get_most_congestion_edge(LinkMsgPassingCopy,LinkBandwith):
    max_e  = None
    band = 0.0
    for e,data in LinkMsgPassingCopy.items():
        if len(data) > 0:
            if max_e == None or LinkBandwith[e.Iph_I]/len(data) < LinkBandwith[max_e.Iph_I]/len(LinkMsgPassingCopy[max_e]):
                max_e = e
    #LinkMsgPassingCopy[e].clear()
    #del LinkMsgPassingCopy[e]
    if max_e != None:
        if len(LinkMsgPassingCopy[max_e]) != 0:
            band =LinkBandwith[max_e.Iph_I]/(len(LinkMsgPassingCopy[max_e]))
        else:
            max_e = None
    return max_e,band

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

def MsgLabel(G,Msg_List,MsgGId):
    return G.InNode[Msg_List[MsgGId][2]].label + "  " + G.OutNode[Msg_List[MsgGId][3]].label + "size = " + str(Msg_List[MsgGId][1])