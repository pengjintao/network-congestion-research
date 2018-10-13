 #!/usr/bin/python
import sys
sys.path.append("../")
import getopt
import json
import random
import queue
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from collections import deque
import numpy as np
import pure_bandwith_method as BMethod
import latency_bandwith_method as LBMethod
import latency_bandwith_congestion_method as LBCMethod
import model_calc as MC
import copy


def IphConstructMsg(a,b,size,Msg_Dicts,G):
    label = "node" + str(a)+"node" + str(b)
    temp = MC.Msg()
    temp.size = size
    temp.Start = G.NodeMap["node" + str(a)]
    temp.End = G.NodeMap["node" + str(b)]
    print(temp.Start.label,end = ' ')
    print(temp.End.label)
    Msg_Dicts[label] = {}
    Msg_Dicts[label]["Msg"] = temp
    Msg_Dicts[label]["start"] = temp.Start
    Msg_Dicts[label]["end"] = temp.End

def Init_example_random_Msgs1(G):
    Msg_Dicts = {}
    IphConstructMsg(5,14,80,Msg_Dicts,G)
    IphConstructMsg(1,12,20,Msg_Dicts,G)
    IphConstructMsg(2,12,20,Msg_Dicts,G)
    IphConstructMsg(3,12,20,Msg_Dicts,G)
    IphConstructMsg(4,12,20,Msg_Dicts,G)


    IphConstructMsg(6,12,80,Msg_Dicts,G)
    IphConstructMsg(7,13,20,Msg_Dicts,G)
    IphConstructMsg(8,13,20,Msg_Dicts,G)
    IphConstructMsg(9,13,20,Msg_Dicts,G)
    IphConstructMsg(10,13,20,Msg_Dicts,G)
    return Msg_Dicts


def Init_random_Msgs(G,n):
	Msg_Dicts = {}
	SenderCount = len(G.InNode);
	RecverCount = len(G.OutNode);
	for x in G.InNode:
		x.Msgs.nextMsg = None
	for i in range(0,n):
		a = random.randint(0,SenderCount-1)
		b = random.randint(0,RecverCount-1)
		A = G.InNode[a]
		B = G.OutNode[b]
		size = random.randint(1,1000)
		if (A.label + B.label) in Msg_Dicts:
			Msg_Dicts[A.label + B.label]["Msg"].size += size
			#print("hit")
		else:
			temp = MC.Msg()
			temp.size = size
			temp.Start = G.NodeMap[A.label]
			temp.End = G.NodeMap[B.label]
			#print(G.NodeMap[B.label])
			Msg_Dicts[A.label + B.label]= {}
			Msg_Dicts[A.label + B.label]["Msg"] = temp
			Msg_Dicts[A.label + B.label]["start"] = A
			Msg_Dicts[A.label + B.label]["end"] = B
			#A.Msgs.insert(temp)
	return Msg_Dicts
def print_Msg_Diects(G,Msg_Dicts):
	for key,data in Msg_Dicts.items():
		print ("Msg:%s size:%d"%(key,data["Msg"].size))
		for l in G.MsgRout[data["start"].Iph_I][data["end"].Iph_I]:
			print(l.label,end = ' ')
		print("")
def add_msg_to_Node(MsgD,G):
	for x in G.InNode:
		while x.Msgs.nextMsg != None:
			x.Msgs.delete_first()
	for x,data in MsgD.items():
		data["start"].Msgs.insert(data["Msg"])
		#print(type(data["Msg"].start))
   
def main(argv):
	print("calculation start")
	configFile = "specific_graph.json"
	def clear(self):
		self.sendedsize = 0
	#图的初始化
	G = MC.Graph(configFile)
	#G.print_graph_MsgRout_table()
	MsgD = Init_example_random_Msgs1(G)
	MsgD1 = copy.copy(MsgD)
	print_Msg_Diects(G,MsgD)
	print("")
    #将随机生成的消息初始化进G中
	#add_msg_to_Node(MsgD,G)
	#G.PrintGraphMessage()
	add_msg_to_Node(MsgD,G)
	G.PrintGraphMessage()
	#print(Msg_Dicts)
	
	print("开始纯带宽计算")
	time,MsgFinishDict = BMethod.pure_bandwith_estimate(G,MsgD)
	print("total time = %f"%(time))
	for x,time in MsgFinishDict.items():
		print("Msg:%s  FinishTime:%f"%(x.Start.label+"-" + x.End.label,time))

	print("延迟带宽拥塞计算")
	LBCMethod.latency_bandwith_congestion_estimate(G,MsgD1)


if __name__ == "__main__":
    main(sys.argv)
