 #!/usr/bin/python
import model_calc as MC
import queue
import copy

def update_start(e,G,CongestionTag,MsgSendGap,StartEdgeMsgs,LinkMsgPassing):
    #在update_start中需要注意的事项
    #对于端到端流控，
   # print("start update")
    if CongestionTag[e]:
        CongestionTag[e] = False
        if e.curPacket.Msg == None:
            print("error happend 11")
        StartEdgeMsgs[e].UpdatePacket(e,G,MsgSendGap)
    else:
        if e.curPacket.Msg != None:
            print("error happend")
        #P = e.Start
        StartEdgeMsgs[e].ExtractPacket(e,G,MsgSendGap)
        msg =e.curPacket.Msg
        if msg != None:
            if not( e.curPacket.PSN == 1 and e.curPacket.PSN == msg.size):
                #只处理消息大小大于1的消息才会出发流量控制
                if e.curPacket.PSN == 1:
                    #msg首个包进入该链路
                    LinkMsgPassing[e].add(msg)
                elif e.curPacket.PSN == msg.size:
                    #msg末尾包通过e
                    LinkMsgPassing[e].remove(msg)
    return e.curPacket
def update(e,G,RoundRobinIndex,CongestionTag,LinkMsgPassing,MsgBlockLinks):
    #print("link update")
    a = "node" + "30"
    b = "node" + "4"
    if CongestionTag[e]:
        CongestionTag[e] = False

        if e.label == a+"--"+b:
            print(e.curPacket.Msg.label)

        for l in e.InEdges:
            if l.curPacket.nextlink(G) == e:
                CongestionTag[l] = True
        return e.curPacket

    tag = True
    backup = RoundRobinIndex[e] 
    for i in range(1,len(e.InEdges)+1):
        index = (i + RoundRobinIndex[e])%len(e.InEdges)
        if e.InEdges[index].curPacket.nextlink(G) == e:
            #index边有消息包，并且其下一条链路是e
            if tag:
                #print("Msg step")
                backup = index
                tag = False
                #命中roundrobin的下一个packet
                e.curPacket = copy.copy(e.InEdges[index].curPacket)
                if e.label == a+"--"+b:
                    print(e.curPacket.Msg.label)
                msg =e.curPacket.Msg
                pack = e.curPacket
                if not( pack.PSN == 1 and pack.PSN == msg.size):
                    #只处理消息大小大于1的消息才会出发流量控制
                    if pack.PSN == 1:
                        #msg首个包进入该链路
                        LinkMsgPassing[e].add(msg)
                #         s = len(LinkMsgPassing[e])
                #         #阻塞数量小于等于1没有触发端到端的拥塞控制的必要
                #         if s > 1:
                #             for msg in LinkMsgPassing[e]:
                #                 if s > MsgSendGap[msg][0]:
                #                     #当e上发生的拥塞数量大于消息msg的最多的拥塞数量时
                #                     MsgBlockLinks[msg].clear()
                #                     MsgBlockLinks[msg].add(e)
                #                     MsgSendGap[msg][0] = s
                #                 elif s == MsgSendGap[msg][0]:
                #                     #当e上发生的拥塞消息数量等于msg本身的最多拥塞数量时
                #                     MsgBlockLinks[msg].add(e)
                    elif pack.PSN == msg.size:
                        #msg末尾包通过e
                        LinkMsgPassing[e].remove(msg)
                #         for OtherMsg in LinkMsgPassing[e]:
                #             if e in MsgBlockLinks[OtherMsg]:
                #                 MsgBlockLinks[OtherMsg].remove(e)
                #                 if len(MsgBlockLinks[OtherMsg]) == 0:
                #                     UnUpdatedMsgs.add(OtherMsg)
                                

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
    if tag and e.label == a+"--"+b:
        print("gap")
    return e.curPacket

def takeSecond(elem):
    return elem[1]                
def latency_bandwith_congestion_estimate(G, MsgD):
    print("start")

    FinishDict = {}
    StartEdgeMsgs = {}
    RoundRobinIndex = {}
    CongestionTag = {}
    LinkMsgPassing = {}
    Temp = {}
    EdgeUpdateOrder = []
    MsgSendGap = {}
    MsgBlockLinks = {}
    MsgCounter = len(MsgD)
    for key,data in MsgD.items():
        #第一个1为带宽，第二个0为计数c,第三个数为sentsize
        #当gap == c的时候，消息便可以传输
        MsgSendGap[data["Msg"]] = [1.0,0,0,True]
        MsgBlockLinks[data["Msg"]] = set()
        #先初始化msg
        Rout = G.MsgRout[data["Msg"].Start.Iph_I][data["Msg"].End.Iph_I]
        l = Rout[0]
        # if l in LinkMsgPassing:
        #     LinkMsgPassing[l].add(data["Msg"])
        #     for msg in LinkMsgPassing[l]:
        #         MsgSendGap[data["Msg"]][0] = len(LinkMsgPassing[l])
        # else:
        #     StartEdgeMsgs[l] = MC.MsgChan()   
        #     LinkMsgPassing[l] = set()
        #     #LinkMsgPassing[l].add(data["Msg"])
        #MsgBlockLinks[data["Msg"]].add(l)

        

        if not l in StartEdgeMsgs:
            StartEdgeMsgs[l] = MC.MsgChan()
        StartEdgeMsgs[l].insert(data["Msg"])

        
        count = 10000
        for e in Rout:
            if e in Temp:
                Temp[e] = min(count,Temp[e])
            else:
                Temp[e] = count
            count-=1
    #完成edge更新序列的计算
    for e,value in Temp.items():
        EdgeUpdateOrder.append([e,value])
        if not e in LinkMsgPassing:
            LinkMsgPassing[e] = set()
        RoundRobinIndex[e] = 0
        CongestionTag[e] = False
        #LinkMsgPassing[e] = set()

    EdgeUpdateOrder.sort(key = takeSecond)

    all_time = 0.0
    while MsgCounter > 0:
        #print("aaaaaaaa")
        #UnUpdatedMsgs = set()
        update_msg_bandwith(G,MsgSendGap,LinkMsgPassing)
        #更新一个时间步
        all_time += 1
        #更新整个网络
        for e,value in EdgeUpdateOrder:
            if e.Start.type == 0:
                #print("Input edge")
                update_start(e,G,CongestionTag,MsgSendGap,StartEdgeMsgs,LinkMsgPassing) 
            else:
                update(e,G,RoundRobinIndex,CongestionTag,LinkMsgPassing,MsgBlockLinks)
            pack = e.curPacket
            if pack.Msg != None and e.End.type == 2 and pack.PSN == pack.Msg.size:
                MsgCounter -= 1
                #print("check")
                MsgD[pack.Msg.Start.label + pack.Msg.End.label]["time"] = all_time
                print("%s finised %d"%(pack.Msg.Start.label + pack.Msg.End.label,all_time))
                FinishDict[pack.Msg] = all_time
                pack.Msg.clear()
                pack.clear()
            if pack.Msg != None and e.End.type == 2:
                e.curPacket.clear()
                #print("check1")
    return all_time,FinishDict


def update_msg_congestion_information(msg,G,MsgSendGap,MsgBlockLinks,LinkMsgPassing,StartEdgeMsgs):
    #if len(MsgBlockLinks) != 0:
    #    print("error ")
    #消息必须要已经发送出去了，否则不进行端到端的拥塞控制
    if MsgSendGap[msg][2] != 0:
        max_edge = G.MsgRout[msg.Start.Iph_I][msg.End.Iph_I][0]
        max_congestion = StartEdgeMsgs[max_edge].msgNum
    
        for e in G.MsgRout[msg.Start.Iph_I][msg.End.Iph_I]:
            if len(LinkMsgPassing[e]) > max_congestion:
                MsgBlockLinks[msg].clear()
                MsgBlockLinks[msg].add(e)
                max_congestion = len(LinkMsgPassing[e])
                max_edge = e
            elif len(LinkMsgPassing[e]) == max_congestion:
                MsgBlockLinks[msg].add(e)

            if e.curPacket.Msg == msg and e.curPacket.PSN == 1:
                break
        MsgSendGap[msg][0] = max_congestion

def get_most_congestion_edge(LinkMsgPassingCopy,LinkBandwith):
    max_e  = None
    band = 0.0
    for e,data in LinkMsgPassingCopy.items():
        if len(data) > 0:
            if max_e == None or LinkBandwith[e]/len(data) < LinkBandwith[max_e]/len(LinkMsgPassingCopy[max_e]):
                max_e = e
    #LinkMsgPassingCopy[e].clear()
    #del LinkMsgPassingCopy[e]
    if max_e != None:
        if len(LinkMsgPassingCopy[max_e]) != 0:
            band =LinkBandwith[max_e]/(len(LinkMsgPassingCopy[max_e]))
        else:
            max_e = None
    return max_e,band
def update_msg_bandwith(G,MsgSendGap,LinkMsgPassing):
    #print("test")
    LinkMsgPassingCopy = copy.copy(LinkMsgPassing)
    for l,data in LinkMsgPassing.items():
        LinkMsgPassingCopy[l] = copy.copy(LinkMsgPassing[l])
    LinkBandwith = {}
    for e,data in LinkMsgPassing.items():
        LinkBandwith[e] = 1.0
    count = len(MsgSendGap)
    MinBand = 0.0
    max_e,MinBand = get_most_congestion_edge(LinkMsgPassingCopy,LinkBandwith)
    
    #目的时计算每一条消息的有效带宽
    while max_e != None:
        for msg in LinkMsgPassingCopy[max_e]:
            #设定每个消息的带宽MsgSendGap，已经设置过带宽的消息集合
            # if abs(MsgSendGap[msg][0] - MinBand) >= 0.00001:
            #     MsgSendGap[msg][1] = 0.0
            MsgSendGap[msg][0] = MinBand
            #print("msg:%s band:%f"%(msg.label,MinBand))
            #更新LinkMsgPassingCopy[最拥塞的链路，每个消息通过的所有链路上]
            #更新所有已经确定带宽的msg，通过的链路的剩余带宽LinkBandwith
            for l in G.MsgRout[msg.Start.Iph_I][msg.End.Iph_I]:
                if l != max_e and l in LinkMsgPassingCopy and msg in LinkMsgPassingCopy[l]:
                    LinkMsgPassingCopy[l].remove(msg)
                    LinkBandwith[l] -= MinBand
                    if len(LinkMsgPassingCopy[l]) == 0:
                        del LinkMsgPassingCopy[l]
        LinkMsgPassingCopy[max_e].clear()
        del LinkMsgPassingCopy[max_e]
        #先找到最拥塞的链路计算其中的消息的带宽
        max_e,MinBand = get_most_congestion_edge(LinkMsgPassingCopy,LinkBandwith)
    


