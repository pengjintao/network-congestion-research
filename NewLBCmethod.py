 #!/usr/bin/python
import model_calc as MC
import queue
import copy

def NewLBC_Estimate(G, Msg_List):
    print("Lets start")
    #算法要求离线计算，并且具有足够的速度
    #降低使用dict，set数据结构的频次

    #局部数据初始化
    MsgNum = len(Msg_List)
    FinishedMsgNum = 0

    RoundRobinIndex = []
    InputbuffsQ = Init_queue(G,RoundRobinIndex)  
    OutPacketBuf = InitOutPacketBuf(G)
    MessageBandwidth = [0.0]*4
    SendedPacketNum = [0]*len(Msg_List)


#初始化队列
def Init_queue(G,RoundRobinIndex)  :
    InputbuffsQ = []
    for r in G.RouterNode:
        temp = []
        temp1 = []
        for oe in r.OutEdges:
            temp1.append(0)
            t = []
            for ie in r.InEdges:
                q = queue.Queue()
                #q.put(ie.label+ " " + r.label+" " + oe.label)
                #print(str(r.Lid)+ " " +str(oe.SourceLid) + " " + str(ie.EndLid))
                t.append(q)
            temp.append(t)
        InputbuffsQ.append(temp)
        RoundRobinIndex.append(temp1)
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
    OutPacketBuf = []
    for i in range(0,len(G.Edges)):
        OutPacketBuf.append(MC.packet())
    # print("packet len %d  Edge Num %d "%(len(OutPacketBuf),len(G.Edges)))
    return OutPacketBuf
