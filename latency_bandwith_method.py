 #!/usr/bin/python
import model_calc as MC
import queue
import copy

def update_start(e,G):
   # print("start update")
    if e.Congestion:
        e.Congestion = False
    else:
        if e.curPacket.Msg != None:
            print("error happend")
        P = e.Start
        P.Msgs.ExtractPacket(e,G)
    return e.curPacket
def update(e,Q,G,S,NodeMap):
    #print("link update")
    if e.Congestion:
        e.Congestion = False
        for l in e.InEdges:
            if l.curPacket.nextlink(G) == e:
                l.Congestion = True
                insert_edge_to_queue(e,Q,S,NodeMap)
        return e.curPacket
    tag = True
    backup = e.roundRobin
    for i in range(1,len(e.InEdges)+1):
        index = (i + e.roundRobin)%len(e.InEdges)
        if e.InEdges[index].curPacket.nextlink(G) == e:
            #index边有消息包，并且其下一条链路是e
            if tag:
                backup = index
                tag = False
                #命中roundrobin的下一个packet
                e.curPacket = e.InEdges[index].curPacket
                e.curPacket.step += 1
                e.InEdges[index].Congestion = False
                e.InEdges[index].curPacket.clear()
            else:
                e.InEdges[index].Congestion = True
            insert_edge_to_queue(e.InEdges[index],Q,S,NodeMap)
    e.roundRobin = backup
    return e.curPacket

def insert_edge_to_queue(e,Q,S,NodeMap):
    if not e in S:
        Q.put(e)
        S.add(e)
        NodeMap[e.Start] -= 1
        if NodeMap[e.Start] == 0:
            for e1 in e.Start.InEdges:
                insert_edge_to_queue(e1,Q,S,NodeMap)
def latency_bandwith_estimate(G, MsgD):
    print("start")
    MC.add_msg_to_Node(MsgD,G)
    
    NodeOutEdgeMap = {}
    for key,x in G.NodeMap.items():
        NodeOutEdgeMap[x] = set()
    for key,data in MsgD.items():
        for e in G.MsgRout[data["Msg"].Start.Iph_I][data["Msg"].End.Iph_I]:
            NodeOutEdgeMap[e.Start].add(e)
    NodeOutDgreeMap = {}
    for key,data in NodeOutEdgeMap.items():
        NodeOutDgreeMap[key] = len(data)
    all_time = 0.0
    time_step  = 1.0
    print(G.MsgCounter)
    while not G.MessageEmpty():
        #print(G.MsgCounter)
        #更新一个时间步
        all_time += 1
        Q = queue.Queue()
        S = set()
        NodeMap = copy.copy(NodeOutDgreeMap)
        #将接受端所有的入边加入队列
        for o in G.OutNode:
            for e in o.InEdges:
                insert_edge_to_queue(e,Q,S,NodeMap)

        #更新整个网络
        pack = MC.packet()
        while not Q.empty():
            #print(Q.qsize())
            e = Q.get()
            if e.Start.type == 0:
               # print("Input edge")
                pack = update_start(e,G) 
            else:
                pack = update(e,Q,G,S,NodeMap)
            if pack.Msg != None and e.End.type == 2 and pack.PSN == pack.Msg.size:
                G.MsgCounter -= 1
                print("check")
                MsgD[pack.Msg.Start.label + pack.Msg.End.label]["time"] = all_time
                print("%s finised"%(pack.Msg.Start.label + pack.Msg.End.label))
            if pack.Msg != None and e.End.type == 2:
                e.curPacket.clear()
                print("check1")
        
    return all_time
