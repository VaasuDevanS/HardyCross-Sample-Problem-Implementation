#!/usr/bin/env python3

__Developer__ = 'Vaasudevan S'
__Version__ = {'Python':'3.5.3', 'GRASS':'7.4'}
__Name__ = 'PipeNetwork.py'

# --------------------- Environment Variables for GRASS -----------------------
import os
import sys

gisdb = 'GRASS/'
os.environ['GISBASE'] = gisbase = "/usr/lib/grass74"
location = 'Chennai'
mapset = 'AU'
sys.path.append(os.path.join(gisbase, "etc", "python"))

import grass.script.setup as gsetup
rcfile = gsetup.init(gisbase, gisdb, location, mapset)

from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules import Module
#os.environ['GRASS_VERBOSE'] = '-1' #runs modules silently

#-------------------------------- Variables -----------------------------------
Join = os.path.join
O = ['overwrite']
Layers = ('Buildings', 'Roads', 'TankPoints', 'myNet') # Available Layers
Colors = ['red', 'green', 'orange', 'purple', 'yellow', 'blue', 'grey']
Pipe_Dia = '1' # metres
#-------------------------------- Code ----------------------------------------
import configparser
from pprint import pprint

config = configparser.RawConfigParser()
config.optionxform = str  # Making config file's keys case-sensitive
config.read('Values.cfg') # Config file with Input Values

def Generate(Qa):
    """
    This function is a recursive function that will call on its own unless
    both the Del values are less than or equal to 2.5
    """
    Dels = []
    global Iterations
    Iterations += 1
    for net in Network:

        Arcs = [net[i:i+2] for i in range(3)]
        Hl, Hl_Qa = {}, {} # Head Loss and Head Loss / Qa
        for arc in Arcs:
            Hl[arc] = (Qa[arc]**2) * k[arc] * Dir[arc]
            Hl_Qa[arc] = abs(Hl[arc]/Qa[arc])
        Del = -sum(Hl.values())/(n*sum(Hl_Qa.values()))
        Dels.append(Del)

    # Append the Overall Dels to O_Del
    O_Del.append(Dels)

    # Adding attribute columns with the values
    v.db_addcolumn(map='myNet', columns='value double precision')
    for net in Network:
        Arcs = [net[i:i+2] for i in range(3)]
        for arc in Arcs:
            whr = "name like '%s'" % arc.lower()
            v.db_update(map='myNet',
                        column='value',
                        where=whr,
                        value=round(abs(Qa[arc]),3))

    v.label(map='myNet', type='line', column='value', labels='Line',
            size='5', opaque='no', color='red')

    v.label(map='TankPoints', type='point', column='name', labels='TankPoints',
            size='5', opaque='no', color='red')

    # Prepare Map
    ps = Module('ps.map')
    ps(input=Join('Test1', '#ps_scripts', 'GenNetwork.psmap'),
       output='Network-Iteration-%s.ps'%Iterations,
       flags=O)

    v.db_dropcolumn(map='myNet', columns='value')

    if not all(i>=con for i in Dels):
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
    else:
        print("\n\n")
        print("Number of Iterations: %s\n" % Iterations)
        pprint(Qa)

# Cleaning the Workspace
g.remove(type='vector', pattern='*', flags=['f'])

# Importing the ShapeFiles to GRASS
for lr in Layers:
    v.in_ogr(input=Join('Test1', lr), output=lr, key='id', flags=O)

# Adding columns `color` and `size` to layers `Buildings` and `TankPoints`
# such that it can be used for artistic map layout.
v.db_addcolumn(map='Buildings', columns='color varchar(10)')
v.db_addcolumn(map='TankPoints', columns='size double precision')
for id,color in enumerate(Colors, start=1):
    whr = 'id like %s' % id
    v.db_update(map='Buildings', column='color', where=whr, value=color)
v.db_update(map='TankPoints', column='size', value=10)
v.db_update(map='TankPoints', column='size', value=20, where='id like 1')

# ------------- Defining the Network and reading the Config values -------------
Network = ('ABDA', 'BCDB')
a = Inflow = [i for i,j in config.items('InFlow')]
A = eval(config.get('InFlow', 'A'))
B = eval(config.get('InFlow', 'B'))
C = eval(config.get('OutFlow', 'C'))
D = eval(config.get('OutFlow', 'D'))

k = {i:eval(j) for i,j in config.items('k')} # k value
n = eval(config.get('n', 'n'))
con = eval(config.get('con', 'con'))

# ----------- Calculating the Direction of Flow based on the Inflows ----------
Dir, Qa, O_Del = {}, {}, []
Iterations = 0
for net in Network:
    Arcs = [net[i:i+2] for i in range(3)]
    for arc in Arcs:
        if any(arc.startswith(j) for j in Inflow):
            Dir[arc] = 1
        else:
            Dir[arc] = -1

# ---------------------------- Assuming Qa values ----------------------------
Qa = {}

if ord(a[0]) == ord(a[1])-1:
    Qa['AB'] = A / 2                    # 25
    Qa['DA'] = A / 2                    # 25
    B += Qa['AB']                       # B = 25 + 50 = 75
    Qa['BC'] = B / 2                    # 75 / 2 = 32.5
    Qa['DB'] = Qa['BD'] = B / 2         # 75 / 2 = 32.5
    Qa['CD'] = (D-Qa['DA']-Qa['BD']) if (Qa['DA']+Qa['BD']) > D else (Qa['BC'] - C)

else:
    Qa['AB'] = Qa['AD'] = A / 2
    Qa['CB'] = Qa['CD'] = C / 2
    Qa['BD'] = (Qa['AB']+Qa['CD']-B) if (B<D) else (Qa['AD']+Qa['CD']-D)

Generate(Qa) # Calling the Function with the assumed values
g.remove(type='vector', pattern='*', flags=['f', 'quiet'])

# Print Last Qa values and Del values
pprint(O_Del)
print()

#EOF
