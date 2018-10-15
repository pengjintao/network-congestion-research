 #!/usr/bin/python
import model_calc as MC
import queue
import copy

def update_start(e,G,CongestionTag):
   # print("start update")
    if CongestionTag[e]:
        CongestionTag[e] = False
    else:
        if e.curPacket.Msg != None:
            print("error happend")
        P = e.Start
        P.Msgs.ExtractPacket(e,G)
    return e.curPacket
def update(e,G,RoundRobinIndex,CongestionTag):
    #print("link update")
    if CongestionTag[e]:
        CongestionTag[e] = False
        for l in e.InEdges:
            if l.curPacket.nextlink(G) == e:
                CongestionTag[l] = True
                #insert_edge_to_queue(e,Q,S,NodeMap)
        return e.curPacket

    # if e.curPacket.Msg!= None and e.curPacket.PSN == e.curPacket.Msg.size:
    #     #末尾包离开该链路
    #     if not e.curPacket.Msg in LinkMsgsPassing[e]:
    #         print("error happend")
    #     LinkMsgsPassing[e].remove(e.curPacket.Msg)
    #     t = len(LinkMsgsPassing[e])
    #     for msg in LinkMsgsPassing[e]:
    #         temp = 0
    #         for edge in G.MsgRout[msg.Start.Iph_I][msg.End.Iph_I]:
    #             temp = max(temp,len())
    #         if msg in MsgBlockGap:
    #             MsgBlockGap[msg] = max(MsgBlockGap[msg],t - msg.Start.Msgs.msgNum)
    #         else:
    #             MsgBlockGap[msg] = max(0,t - msg.Start.Msgs.msgNum)


    tag = True
    backup = RoundRobinIndex[e] 
    for i in range(1,len(e.InEdges)+1):
        index = (i + RoundRobinIndex[e])%len(e.InEdges)
        if e.InEdges[index].curPacket.nextlink(G) == e:
            #index边有消息包，并且其下一条链路是e
            if tag:
                backup = index
                tag = False
                #命中roundrobin的下一个packet
                e.curPacket = copy.copy(e.InEdges[index].curPacket)

                # if e.curPacket.Msg.PSN == 1:
                #     #msg首个包进入该链路
                #     congestion_effect_valid = True
                #     update_edge = e.InEdges[index]

                #print(e.curPacket.Msg.sendedsize)
                e.curPacket.step += 1
                CongestionTag[e.InEdges[index]]= False
                #e.InEdges[index].Congestion = False
                e.InEdges[index].curPacket.clear()
            else:
                CongestionTag[e.InEdges[index]]= True
                #e.InEdges[index].Congestion = True
            #insert_edge_to_queue(e.InEdges[index],Q,S,NodeMap)
    RoundRobinIndex[e] = backup
    return e.curPacket

# def insert_edge_to_queue(e,Q,S,NodeMap):
#     if not e in S:
#         Q.put(e)
#         S.add(e)
#         NodeMap[e.Start] -= 1
#         if NodeMap[e.Start] == 0:
#             for e1 in e.Start.InEdges:
#                 insert_edge_to_queue(e1,Q,S,NodeMap)
def takeSecond(elem):
    return elem[1]                
def latency_bandwith_estimate(G, MsgD):
    print("start")
    MC.add_msg_to_Node(MsgD,G)
    #MC.print_Msg_Diects(G,MsgD)
    #print("add msg to Node")
    #G.PrintGraphMessage()
    RoundRobinIndex = {}
    CongestionTag = {}
    Temp = {}


    for key,data in MsgD.items():
        #MsgSendtime[data["Msg"]] = 0
       # MsgBlockGap[data["Msg"]] = 0
        count = 10000
        for e in G.MsgRout[data["Msg"].Start.Iph_I][data["Msg"].End.Iph_I]:
            if e in Temp:
                Temp[e] = min(count,Temp[e])
            else:
                Temp[e] = count
            count-=1
    EdgeUpdateOrder = []
    for e,value in Temp.items():
        EdgeUpdateOrder.append([e,value])
        RoundRobinIndex[e] = 0
        CongestionTag[e] = False
        #LinkMsgsPassing[e] = set()
    EdgeUpdateOrder.sort(key = takeSecond)

    #for i in range(0,len(EdgeUpdateOrder)):
    #    print(EdgeUpdateOrder[i][0].Start.label + EdgeUpdateOrder[i][0].End.label,end = ' ')
    #    print(EdgeUpdateOrder[i][1])
    # for x,y in EdgeUpdateOrder:
    #     print(x.Start.label + x.End.label)
    #for key,data in NodeOutEdgeMap.items():
    #     NodeOutDgreeMap[key] = len(data)
    # Q = queue.Queue()
    # S = set()
    # for o in G.OutNode:
    #     for e in o.InEdges:
    #         Q.put(e)
    #         S.add(e)
    all_time = 0.0
    while not G.MessageEmpty():
        #print(G.MsgCounter)
        #更新一个时间步
        all_time += 1
        # Q = queue.Queue()
        # S = set()
        # NodeMap = copy.copy(NodeOutDgreeMap)
        # #将接受端所有的入边加入队列
        # for o in G.OutNode:
        #     for e in o.InEdges:
        #         insert_edge_to_queue(e,Q,S,NodeMap)

        #更新整个网络
        for e,value in EdgeUpdateOrder:
            #print(e.Start.label + e.End.label)
            #e = Q.get()
            if e.Start.type == 0:
               # print("Input edge")
                update_start(e,G,CongestionTag) 
            else:
                update(e,G,RoundRobinIndex,CongestionTag)
            pack = e.curPacket
            if pack.Msg != None and e.End.type == 2 and pack.PSN == pack.Msg.size:
                G.MsgCounter -= 1
                #print("check")
                MsgD[pack.Msg.Start.label + pack.Msg.End.label]["time"] = all_time
                print("%s finised %d"%(pack.Msg.Start.label + pack.Msg.End.label,all_time))
                pack.Msg.clear()
                pack.clear()
            if pack.Msg != None and e.End.type == 2:
                e.curPacket.clear()
                #print("check1")
    return all_time
