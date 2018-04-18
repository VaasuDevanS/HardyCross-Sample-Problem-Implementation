# PipeNetwork Calculation - Problem
from __future__ import division

def Generate(Qa):

    Dels = []
    for net in Network:

        Arcs = [net[i:i+2] for i in range(3)]
        Hl, Hl_Qa = {}, {}
        for arc in Arcs:
            Hl[arc] = (Qa[arc]**2) * k[arc] * Dir[arc]
            Hl_Qa[arc] = abs(Hl[arc]/Qa[arc])
        Del = -sum(Hl.values())/(n*sum(Hl_Qa.values()))
        Dels.append(Del)
        #print([Qa[i]*Dir[i] for i in Arcs])
    print(Dels)

    if not all(i>=-2.5 for i in Dels):
        New_Qa = {}
        for id,net in enumerate(Network):
            Arcs = [net[i:i+2] for i in range(3)]
            for arc in Arcs:
                if arc == 'BD':
                    New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[id]-Dels[int(not id)]
                elif arc == 'DB':
                    New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[id]-Dels[int(not id)]
                else:
                    New_Qa[arc] = Qa[arc]*Dir[arc]+Dels[id]
        Generate(New_Qa)

A = 50
B = 50

C = 75
D = 25

Network = ('ABDA', 'BCDB')
k = {'AB':2, 'BD':1, 'DA':2, 'BC':4, 'CD':3, 'DB':1} # Read from the User
n = 2

# Calculating the Direction of Flow based on the Inflows
Dir = {}
Inflow = 'A', 'B'
for net in Network:
    Arcs = [net[i:i+2] for i in range(3)]
    for arc in Arcs:
        if any(arc.startswith(j) for j in Inflow):
            Dir[arc] = 1
        else:
            Dir[arc] = -1

Qa = {}

Qa['AB'] = A / 2 # 25
Qa['DA'] = A / 2 # 25
B += Qa['AB'] # B = 25 + 50 = 75
Qa['BC'] = B - D # 75 - 25 = 50
Qa['BD'] = Qa['DB'] = D # 25
#Qa['CD'] =

#Qa['BC']

#D -= Qa['BD']

Qa = {'AB':25, 'BD':25, 'DA':25, 'BC':50, 'CD':25, 'DB':25}
Generate(Qa)