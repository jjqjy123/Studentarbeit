from abaqus import *
from abaqusConstants import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import regionToolset
import math
import random
import os
# ---------------------------------------------------------------------------------
######################## Parameter von Modell einstellen ##########################
# Dimensionen der Waben
Schichiten_Waben = 8                #: Menge der Schichiten von Wabenpart
Ampitude_Waben = 3                  #: Ampitude von Waben
T = 10                              #: Periode von Wabenschichten
Aufloesung   = 0.2                  #: Praezision
Laenge_Waben = 50
Dicke_Waben  = 15
Dicke_Papier = 0.3
Distanz = 2*Ampitude_Waben-0.1      #: Distanz zwischen Wabenschichten
PartMeshsize_Waben = 0.4
Dickseednummer_Waben = 30
# ---------------------------------------------------------------------------------
############################ Beginn des Modellaufbau ##############################
mdb.Model(name='S4', modelType=STANDARD_EXPLICIT)     # Neu-Modell
Model = mdb.models['S4']                              # Name des Modells
Assembly = Model.rootAssembly
# ---------------------------------------------------------------------------------
#: Punktliste von Wabenschicht erstellen
random.seed(0)
Randomphase_Liste = []                                #: um die zufaellige Anfangsphase von allen Wabenschichten zu speichern
Punkt_Liste = []                                      #: um die Punkte von allen Wabenschichten zu speichern
# ---------------------------------------------------------------------------------
#: Modell aufbauen
#: Wabenpart
s1 = Model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
for Schicht_Nummer in range(0, Schichiten_Waben):
    Punkt_Liste.append([])                                  #: Eine leere Punktlist vordefinieren
    Randomphase_Liste.append(random.random())               #: Zufaellige Anfangsphase bestimmen
    x = 0
    y_Symmetrieachse = Distanz*Schicht_Nummer               #: Position von y_Symmetrieachs in diese Schicht
    while (x <= Laenge_Waben):
        y = y_Symmetrieachse + Ampitude_Waben * math.sin(2*math.pi/T*x - T*Randomphase_Liste[Schicht_Nummer])
        if y - y_Symmetrieachse >= Distanz/2 or abs(y - y_Symmetrieachse - Distanz/2)<=0.01:
            Punkt_Liste[Schicht_Nummer].append((x, Distanz/2 + y_Symmetrieachse))
            if len(Punkt_Liste[Schicht_Nummer])>2:
                Model.sketches['__profile__'].Spline(points=Punkt_Liste[Schicht_Nummer])
            Punkt_Liste[Schicht_Nummer] = []
            while (y - y_Symmetrieachse >= Distanz/2) and (x <= Laenge_Waben):
                x += Aufloesung
                y = y_Symmetrieachse + Ampitude_Waben * math.sin(2*math.pi/T*x - T*Randomphase_Liste[Schicht_Nummer])
            Punkt_Liste[Schicht_Nummer].append((x, Distanz/2 + y_Symmetrieachse))
            x += Aufloesung
            continue
        elif y - y_Symmetrieachse <= -Distanz/2 or abs(y - y_Symmetrieachse + Distanz/2)<=0.01:
            Punkt_Liste[Schicht_Nummer].append((x, -Distanz/2 + y_Symmetrieachse))
            if len(Punkt_Liste[Schicht_Nummer])>2:
                Model.sketches['__profile__'].Spline(points=Punkt_Liste[Schicht_Nummer])
            Punkt_Liste[Schicht_Nummer] = []
            while (y - y_Symmetrieachse <= -Distanz/2) and (x <= Laenge_Waben):
                x += Aufloesung
                y = y_Symmetrieachse + Ampitude_Waben * math.sin(2*math.pi/T*x - T*Randomphase_Liste[Schicht_Nummer])
            Punkt_Liste[Schicht_Nummer].append((x, -Distanz/2 + y_Symmetrieachse))
            x += Aufloesung
            continue
        Punkt_Liste[Schicht_Nummer].append((x, y))          #: Punkte von Wabenschicht in entsprechender Punktliste speichern
        x += Aufloesung
        if (x >= Laenge_Waben) and (y - y_Symmetrieachse > -Distanz/2) and (y - y_Symmetrieachse < Distanz/2): 
            y = y_Symmetrieachse + Ampitude_Waben * math.sin(2*math.pi/T*x - T*Randomphase_Liste[Schicht_Nummer])
            Punkt_Liste[Schicht_Nummer].append((x, y))         
            Model.sketches['__profile__'].Spline(points=Punkt_Liste[Schicht_Nummer])
            break
for Schicht_Nummer in range(-1, Schichiten_Waben):          #: Zwischenschicht aufbauen
    s1.Line(point1=(0, Distanz*Schicht_Nummer + Distanz/2), point2=(Laenge_Waben, Distanz*Schicht_Nummer + Distanz/2))
Part_Waben = Model.Part(name='Wabenpart', dimensionality=THREE_D, type=DEFORMABLE_BODY)
Part_Waben.BaseShellExtrude(sketch=s1, depth=Dicke_Waben)
# ---------------------------------------------------------------------------------
###################################### Mesh #######################################
Edge_Waben = Part_Waben.edges
seededge = []
for edge in Edge_Waben:
    if edge.getSize()==Dicke_Waben:
        seededge.append(edge)                                                                #: Raender laengs der Dickrichtung Liste speichern

Part_Waben.seedEdgeByNumber(edges=seededge, number=Dickseednummer_Waben, constraint=FINER)   #: Praezision von Dickrichtung ist nicht so wichtig
Part_Waben.seedPart(size=PartMeshsize_Waben, deviationFactor=0.1, minSizeFactor=0.1)
Part_Waben.generateMesh()

# Elementtype S4
elemType1 = ElemType(elemCode=S4, elemLibrary=STANDARD, secondOrderAccuracy=OFF)
elemType2 = ElemType(elemCode=S3, elemLibrary=STANDARD)
face_Waben = Part_Waben.faces
Part_Waben.setElementType(regions=(face_Waben,), elemTypes=(elemType1, elemType2))
# ---------------------------------------------------------------------------------
#################################### Inp File #####################################
path = os.getcwd()
name ='S4' 
inp_name = name + '.inp'
nodes = Part_Waben.nodes                                    
elements=Part_Waben.elements
with open(path + '\\' + inp_name, 'w+') as f1:
    f1.write('*Node\n')                                    
    for i in nodes:
        f1.write(str(i.label))
        for j in range(0, 3):
            f1.write(',')
            f1.write('     ')
            f1.write(str(format(i.coordinates[j], '.6f')))
        f1.write('\n')
    f1.write('*Element, type='+ name)
    f1.write('\n')
    for i in elements:
        f1.write(str(i.label))
        nodes_element = i.getNodes()
        for j in nodes_element:
            f1.write(', ')
            f1.write(str(j.label))
        f1.write('\n')
