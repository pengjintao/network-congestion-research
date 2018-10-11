 #!/usr/bin/python
import model_calc as MC

def latency_bandwith_estimate(G, MsgD):
    print("start")
    MC.add_msg_to_Node(MsgD,G)
    
    all_time = 0.0
    print(G.MsgCounter)
    while not G.MessageEmpty():
        print("test")
        break
