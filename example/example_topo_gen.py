#!/usr/bin/python

import sys
import getopt
import json
import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from collections import deque
import numpy as np


topology = {"nodes": [], "channels": [], "connections": [],"InNode":[],"Router":[],"OutNode":[]}
outputFile = "specific_graph"
for i in range(1,20):
    type = str()
    if i<=10:
        type = "InNode"
    elif i>=11 and i <= 14:
        type = "OutNode"
    else:
        type = "Router"
    N = {
            "node_id": "node"+str(i),
            "node_type": type,
            "x-coord": str(random.random()*10),
            "y-coord": str(random.random()*10)
    }
    topology["nodes"].append(N)

    if i<=10:
        topology["InNode"].append(N)
    elif i>=11 and i <= 14:
        topology["OutNode"].append(N)
    else:
        topology["Router"].append(N)
    
topology["connections"].append({
                    "source_id": "node1",
                    "destination_id": "node15"})
topology["connections"].append({
                    "source_id": "node2",
                    "destination_id": "node15"})
topology["connections"].append({
                    "source_id": "node3",
                    "destination_id": "node15"})
topology["connections"].append({
                    "source_id": "node4",
                    "destination_id": "node15"})

topology["connections"].append({
                    "source_id": "node15",
                    "destination_id": "node11"}) 
topology["connections"].append({
                    "source_id": "node15",
                    "destination_id": "node12"}) 

topology["connections"].append({
                    "source_id": "node5",
                    "destination_id": "node16"}) 
topology["connections"].append({
                    "source_id": "node6",
                    "destination_id": "node16"})                      
topology["connections"].append({
                    "source_id": "node16",
                    "destination_id": "node17"}) 
topology["connections"].append({
                    "source_id": "node17",
                    "destination_id": "node18"})
topology["connections"].append({
                    "source_id": "node17",
                    "destination_id": "node15"})
                    
topology["connections"].append({
                    "source_id": "node7",
                    "destination_id": "node18"})                    
topology["connections"].append({
                    "source_id": "node8",
                    "destination_id": "node18"})    
topology["connections"].append({
                    "source_id": "node9",
                    "destination_id": "node18"})                    
topology["connections"].append({
                    "source_id": "node10",
                    "destination_id": "node18"})
topology["connections"].append({
                    "source_id": "node18",
                    "destination_id": "node19"})      
topology["connections"].append({
                    "source_id": "node19",
                    "destination_id": "node13"})
topology["connections"].append({
                    "source_id": "node19",
                    "destination_id": "node14"})                   

with open(outputFile + ".json", "w") as ofile:
    json.dump(topology, ofile, sort_keys=True,
                indent=4, separators=(',', ': '))
