 #!/usr/bin/python
import model_calc as MC
import queue

def update_start(e,G):
    print("start update")
    if e.Congestion:
        e.Congestion = False
    else:
        if e.curPacket.Msg != None:
            print("error happend")
        P = e.Start
        P.Msgs.ExtractPacket(e,G)
    return e.curPacket
def update(e,Q,G):
    print("link update")
    if e.Congestion:
        e.Congestion = False
        for l in e.InEdges:
            if l.curPacket.nextlink(G) == e:
                l.Congestion = True
                Q.put(l)
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
            
            Q.put(e.InEdges[index])
    e.roundRobin = backup
    return e.curPacket
    
def latency_bandwith_estimate(G, MsgD):
    print("start")
    MC.add_msg_to_Node(MsgD,G)
    
    all_time = 0.0
    time_step  = 1.0
    print(G.MsgCounter)
    while not G.MessageEmpty():
        # print("test")
        #更新一个时间步
        all_time += 1
        Q = queue.Queue()
        S = set()
        #将接受端所有的入边加入队列
        for o in G.OutNode:
            for e in o.InEdges:
                Q.put(e)
                S.add(e)

        #更新整个网络
        pack = MC.packet()
        while not Q.empty():
            e = Q.get()
            if e.Start.type == 0:
                print("Input edge")
                pack = update_start(e,G) 
            else:
                pack = update(e,Q,G)
            if pack.Msg != None and e.End.type == 2:
                e.curPacket.clear()
            if pack.Msg != None and e.End.type == 2 and pack.PSN == pack.Msg.size:
                G.MsgCounter -= 1
                MsgD[pack.Msg.Start.label + pack.Msg.End.label]["time"] = all_time
                print("%s finised"%(pack.Msg.Start.label + pack.Msg.End.label))
     #   break
    return all_time
