 #!/usr/bin/python
import model_calc
def pure_bandwith_estimate(G,MsgD):
    #按照阶段计算每次通信模式改变后的传输开销
    all_time = 0.0
    while len(MsgD) > 0:
        #先初始化路由图
        #再设置第一时刻各个消息的带宽
        #最早完成的一批消息从MsgD中剔除
        MsgRealBandwith = {}
        LinkMsgs = {}
        LinkMaxBandwith = {}
        for x,data in MsgD.items():
            for l in G.MsgRout[data["start"].Iph_I][data["end"].Iph_I]:
                LinkMaxBandwith[l] = l.bandwidth
                if l in LinkMsgs:
                    LinkMsgs[l].add(data["Msg"])
                else:
                    LinkMsgs[l] = {data["Msg"]}

        while len(LinkMsgs) != 0:
            min_band_link = None
            min_band_link_data = None
            #找到最小带宽的链路
            for x,data in LinkMsgs.items():
                if min_band_link_data == None or
                 len(data) > len(min_band_link_data):
                    min_band_link = x
                    min_band_link_data = data
            #设置通过最小链路的消息的带宽
            #将这些消息从LinkMsgs中剔除
            #将无消息的链路从LinkMsgs中除去
            b = LinkMaxBandwith[min_band_link] / len(min_band_link_data)
            for msg in min_band_link_data:
                MsgRealBandwith[msg] = b
                for link in G.MsgRout[msg.Start.Iph_I][msg.End.Iph_I]:
                    if link in LinkMsgs:
                        LinkMsgs[link].remove(msg)
                        LinkMaxBandwith[link] -= b
                        if len(LinkMsgs[link]) == 0:
                            del LinkMsgs[link]
                            del LinkMaxBandwith[link]
        
        #现在开始查找最先完成的一批消息的时间步
        minimum_time_step = 8888888888.0
        all_time += minimum_time_step
        for msg,b in MsgRealBandwith.items():
            t = msg.size / b
            if t < minimum_time_step:
                minimum_time_step = t
        #将在这段时间内完成的消息剔除
        for msg,b in MsgRealBandwith.items():
            msg.size -= minimum_time_step*MsgRealBandwith[msg]
            if msg.size <= 0.0001:
                del MsgD[msg.Start.label + msg.End.label]
        



        LinkMsgList = LinkMsgs.items()

        break
    return all_time