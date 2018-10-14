 #!/usr/bin/python
import sys
import copy
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

class Graph:
	def __init__(self,configFile):
		self.MsgCounter = int(0)
		self.Edges = []
		self.InNode = []
		self.OutNode = []
		self.RouterNode = []
		self.MsgRout = []
		with open(configFile,'r') as cFile:
			Input = json.load(cFile)
		self.NodeMap = {}
		#print(Input["InNode"])
		#node 空间的分配，node中尚有InEdge OutEdge MSgChan未处理
		count = 0
		for x in Input["InNode"]:
			temp = Node()
			temp.label = x["node_id"]
			temp.type = 0;
			self.InNode.append(temp)
			temp.Iph_I = count;
			count += 1;
			self.NodeMap[x["node_id"]] = temp
		count = 0
		for x in Input["OutNode"]:
			temp = Node()
			temp.label = x["node_id"]
			temp.type = 2;
			self.OutNode.append(temp)
			temp.Iph_I = count;
			count += 1;
			self.NodeMap[x["node_id"]] = temp

		count = 0
		for x in Input["Router"]:
			temp = Node()
			temp.label = x["node_id"]
			temp.type = 1;
			temp.Iph_I = count;
			count += 1;
			self.RouterNode.append(temp)
			self.NodeMap[x["node_id"]] = temp

		#开始初始化Edge
		count = 0
		for x in Input["connections"]:
			temp = Edge()
			temp.Iph_I = count
			count+=1
			temp.label = x["source_id"] +"--" + x["destination_id"]
			temp.Start = self.NodeMap[x["source_id"]]
			temp.Start.OutEdges.append(temp)
			temp.End = self.NodeMap[x["destination_id"]]
			temp.End.InEdges.append(temp)
			if temp.Start.type == 0:
				#print("temp.start.type = InNode");
				temp.EdgeType = 0
			if temp.End.type == 2:
				#print("temp.start.type = OutNode");
				temp.EdgeType = 2;
			if temp.Start.type == 1 and temp.End.type == 1:
				#print("Router Edge ")
				temp.EdgeType = 1
			self.Edges.append(temp)
		#init Edge.OutEdges and Edge.InEdges
		for x in self.InNode + self.OutNode + self.RouterNode:
			for p in x.InEdges:
				for q in x.OutEdges:
					p.OutEdges.append(q)
					q.InEdges.append(p)


		#init MsgRout space
		for x in self.InNode:
			a = []
			for y in self.OutNode:
				temp = []
				a.append(temp)
			self.MsgRout.append(a)
		print(len(self.MsgRout))
		print(len(self.MsgRout[3]))
		self.MsgRout[3][0].append(1)
		print(len(self.MsgRout[3][0]))
		self.MsgRout[3][0].clear()


		#init Massage Router Table
		for Ipt in self.InNode:
			for Opt in self.OutNode:
				self.FindShortestPath(Ipt,Opt);
	def FindShortestPath(self,SendNode,RecvNode):
		S = set()
		#print("find shortest path");
		Q = queue.Queue();
		for x in SendNode.OutEdges:
			S.add(x)
			Q.put(x)
			e = None
		while not Q.empty():
			e = Q.get()
			e.End.prev = e.Start
			if e.End == RecvNode:
				#print("check")
				break;
			for x in e.OutEdges:
				if (not x in S):
					Q.put(x);
					S.add(x);
					x.prev = e;
		while e != None:
			self.MsgRout[SendNode.Iph_I][RecvNode.Iph_I].append(e)
			e = e.prev
		self.MsgRout[SendNode.Iph_I][RecvNode.Iph_I].reverse();
		# print("Start= %s end=%s "%(SendNode.label,RecvNode.label),end=' ')
		# for x in self.MsgRout[SendNode.Iph_I][RecvNode.Iph_I]:
		# 	print(x.label,end = ' ')
		# print(' ')
	
	def MessageEmpty(self):
		return self.MsgCounter <= 0
	def print_graph_MsgRout_table(self):
		for x in self.InNode:
			for y in self.OutNode:
				print("Start= %s end=%s "%(x.label,y.label),end=' ')
				for l in self.MsgRout[x.Iph_I][y.Iph_I]:
					print(l.label,end = ' ')
				print("")
	def PrintGraphMessage(self):
		for x in self.InNode:
			if x.Msgs.nextMsg != None:
				p = MsgChan()
				p.nextMsg = x.Msgs.nextMsg
				#print(type(p.nextMsg.msg.start))
				print("%s %d"%(p.nextMsg.msg.Start.label + p.nextMsg.msg.End.label,p.nextMsg.msg.size))
				p.nextMsg = p.nextMsg.nextMsg
				while p.nextMsg != x.Msgs.nextMsg:
					print("%s %d"%(p.nextMsg.msg.Start.label + p.nextMsg.msg.End.label,p.nextMsg.msg.size))
					p.nextMsg = p.nextMsg.nextMsg





class Edge:
	def __init__(self):
		self.Iph_I = 0
	#	print("start")
		#EdgeType 0(input edge) 1(mid edge) 2(out edge)
		self.label = ""
		self.EdgeType = int() # check
		self.InEdges = [] #check
		self.OutEdges = [] #check
		self.Start = None   #check
		self.End = None     #check
		self.bandwidth = 1
		self.roundRobin = 0
		self.curPacket = packet()
		self.Congestion = False
		self.prev = None # used for shortest path generator
class Node:
	def __init__(self):
		#0(start node) 1 (Router) 2 (recv node)
		self.label = ""
		self.type = 0  #check
		self.InEdges = [] #check
		self.OutEdges = [] #checks
		self.Iph_I = int()
		self.prev = None  #prev is used for shortest path generator
		self.Msgs = MsgChan()
class MsgChan:
	def __init__(self):
		self.msg = None
		self.nextMsg = None
		self.prevMsg = None
		self.msgNum = 0
		self.MsgQ = queue.Queue()
	def ExtractPacket(self,e,G,MsgSendGap):
		e.curPacket.clear()
		if self.nextMsg == None and self.MsgQ.empty():
			#print("check")
			#当前节点无任何消息，那么无法抽取任何packet	
			e.curPacket.clear()
		else:
			#当前开始边e所连接的消息，先抽取消息
			tag =  False
			for i in range(0,self.msgNum):
				#print(abs(MsgSendGap[self.nextMsg.msg][1]))
				if abs(MsgSendGap[self.nextMsg.msg][1]) <=MsgSendGap[self.nextMsg.msg][0]+ 0.00001:
					pack = packet()
					pack.Msg = self.nextMsg.msg
					MsgSendGap[self.nextMsg.msg][2] += 1
					pack.PSN = MsgSendGap[self.nextMsg.msg][2]
					pack.step = 0
					self.MsgQ.put(pack)
					#print("msg =%s PSN = %d "%(self.nextMsg.msg.label,pack.PSN))
					#print("msg =%s "%(self.nextMsg.msg.label))
					if pack.PSN >= self.nextMsg.msg.size:
					#	print("check point")
						self.delete_first()
					else:
						self.nextMsg = self.nextMsg.nextMsg
				else:
					self.nextMsg = self.nextMsg.nextMsg
			#更新e中每一个消息的时间步
			if self.nextMsg != None:
				for i in range(0,self.msgNum):
					MsgSendGap[self.nextMsg.msg][1]+=MsgSendGap[self.nextMsg.msg][0]
					while MsgSendGap[self.nextMsg.msg][1] >= 1.0:
						MsgSendGap[self.nextMsg.msg][1] = MsgSendGap[self.nextMsg.msg][1] - 1.0
					self.nextMsg = self.nextMsg.nextMsg
				
				# if tag:
				# 	tag = False
				# 	p = self.nextMsg.prevMsg.msg
				# 	MsgSendGap[p][1]+=MsgSendGap[self.nextMsg.msg][0]
				# 	if MsgSendGap[p][1] >= 1.0 - 0.00001:
				# 		MsgSendGap[p][1] = 0.0

			
			if not self.MsgQ.empty():
				e.curPacket = copy.copy(self.MsgQ.get())
				#else:
					#print("check 轮空")
				#p = self.nextMsg.msg
				#print("%s  block = %f,count = %f"%(p.label,MsgSendGap[p][0],MsgSendGap[p][1]))
				#else:print("test")
	def insert(self,msg):
		temp = MsgChan();
		temp.msg = msg;
		if self.nextMsg == None:
			self.nextMsg = temp
			temp.nextMsg = temp;
			temp.prevMsg = temp;
		else:
			temp.nextMsg = self.nextMsg;
			temp.prevMsg = self.nextMsg.prevMsg;
			temp.prevMsg.nextMsg = temp;
			temp.nextMsg.prevMsg = temp;
		self.msgNum += 1
	def delete_first(self):
		if self.nextMsg != None:
			temp = self.nextMsg
			if temp.nextMsg == temp:
				self.nextMsg = None;
			else:
				self.nextMsg = temp.nextMsg;
				self.nextMsg.prevMsg = temp.prevMsg
				temp.prevMsg.nextMsg = self.nextMsg
		self.msgNum -= 1
	def Empty(self):
		if self.nextMsg == None:
			return True
		else:
			return False

class Msg:
	def __init__(self):
		self.size = 0
		self.sendedsize = 0
		self.Start = None
		self.End = None
		self.label = ""
	def clear(self):
		self.sendedsize = 0
class packet:
	def __init__(self):
		self.Msg = None
		self.PSN = int()
		self.step = 0
	def nextlink(self,G):
		if self.Msg == None:
			return None
		IphList = G.MsgRout[self.Msg.Start.Iph_I][self.Msg.End.Iph_I]
		if self.step+1 < len(IphList):
			return IphList[self.step+1]
		else:
			return None
	def clear(self):
		self.Msg = None
		self.PSN = 0
		self.step = 0
def Init_random_Msgs(G,n):
	Msg_Dicts = {}
	SenderCount = len(G.InNode);
	RecverCount = len(G.OutNode);
	for x in G.InNode:
		x.Msgs.nextMsg = None
	for i in range(0,n):
		a = random.randint(0,SenderCount-1)
		b = random.randint(0,RecverCount-1)
		A = G.InNode[2]
		B = G.OutNode[b]
		size = random.randint(1,1000)
		if (A.label + B.label) in Msg_Dicts:
			Msg_Dicts[A.label + B.label]["Msg"].size += size
			#print("hit")
		else:
			temp = Msg()
			temp.size = size
			temp.Start = G.NodeMap[A.label]
			temp.End = G.NodeMap[B.label]
			temp.label = A.label + "-" + B.label
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
	G.MsgCounter = 0
	for x,data in MsgD.items():
		data["start"].Msgs.insert(data["Msg"])
	G.MsgCounter = len(MsgD)
		#print(type(data["Msg"].start))
def msgBackup_to_msgd(MSgBackup,MsgD,G):
	for x in MSgBackup:
		A = G.NodeMap[x[0]]
		B = G.NodeMap[x[1]]
		temp = Msg()
		temp.size = x[2]
		temp.Start = G.NodeMap[A.label]
		temp.End = G.NodeMap[B.label]
		temp.label = A.label + "-" + B.label
		MsgD[A.label + B.label]= {}
		MsgD[A.label + B.label]["Msg"] = temp
		MsgD[A.label + B.label]["start"] = A
		MsgD[A.label + B.label]["end"] = B
def msgd_to_msgBackup(MsgD,MSgBackup,G):
	for x,data in MsgD.items():
		MSgBackup.append ([data["start"].label,data["end"].label,data["Msg"].size])

def main(argv):
	print("calculation start")
	configFile = "test_1.json"
	saveFile2 = "save_Msg"

	#图的初始化
	G = Graph(configFile)
	#G.print_graph_MsgRout_table()
    #生成40条随机消息
	MSgBackup = []
	MsgD = None

	#
	if False:
		MsgD = {}
		with open(saveFile2+ ".json", 'r') as cFile:
			MSgBackup = json.load(cFile)
		msgBackup_to_msgd(MSgBackup,MsgD, G)
	else:
		MsgD = Init_random_Msgs(G,3)
		msgd_to_msgBackup(MsgD,MSgBackup ,G)
		with open(saveFile2 + ".json", "w") as ofile:
			json.dump(MSgBackup, ofile, sort_keys=True,indent=4, separators=(',', ': '))

	MsgD1 = copy.copy(MsgD)
	MsgD2 = copy.copy(MsgD)
	print("打印消息路由路径")
	print_Msg_Diects(G,MsgD)
	print("")


    #将随机生成的消息初始化进G中
	#add_msg_to_Node(MsgD,G)
	#G.PrintGraphMessage()
	#add_msg_to_Node(MsgD,G)
	#G.PrintGraphMessage()
	#print(Msg_Dicts)
	
	#开始纯带宽计算
	print("\n开始纯带宽计算")
	time,MsgFinishDict = BMethod.pure_bandwith_estimate(G,MsgD)
	print("total time = %f"%(time))
	T = []
	for x,time in MsgFinishDict.items():
		T.append([x,time,x.size])
	T.sort(key = LBMethod.takeSecond)
	for x,time,size in T:
		print("Msg:%s  FinishTime:%f  size = %d"%(x.label,time,size))

	#开始延迟带宽计算
	#print("\n开始延迟带宽计算")
	#LBMethod.latency_bandwith_estimate(G,MsgD1)

	#LBMethod.latency_bandwith_estimate(G,MsgD2)

	print("\n开始端到端的拥塞延迟带宽计算")
	time1,MsgFinishDict1 = LBCMethod.latency_bandwith_congestion_estimate(G,MsgD2)
	
	for x,time,size in T:
		print("Msg:%s  (LBCmethod - Bmethod)/Bmethod:%f  size = %d"%(x.label,(MsgFinishDict1[x] - time)/time,size))
if __name__ == "__main__":
    main(sys.argv)
