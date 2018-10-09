 #!/usr/bin/python
import model_calc

def pure_bandwith_estimate(G,MsgD):
    while len(MsgD) > 0:
        MsgRealBandwith = {}
        LinkMsgs = {}
        for x,data in MsgD.items():
            for l in G.MsgRout[data["start"].Iph_I][data["end"].Iph_I]:
                if l in LinkMsgs:
                    LinkMsgs[l].append(data["Msg"])
        LinkMsgList = LinkMsgs.items()
        
        break
    return 3