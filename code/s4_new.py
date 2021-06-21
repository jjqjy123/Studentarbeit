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
# Dicke der Schichten
Dicken_Aussenlage  = 1
Dicken_Deckschicht = 0.67
Dicken_Entkopplung = 0.1
Dicken_Papier = 0.15

# Vernetzungsize
Default_Elementsize = 0.25

# Bei Default sind alle Elementsize gleich
PartMeshsize_Aussenlage  = Default_Elementsize
PartMeshsize_Deck        = Default_Elementsize
PartMeshsize_Entkopplung = Default_Elementsize
# ---------------------------------------------------------------------------------
# Materialeigenschaften der Schichiten
# Deck
E_Deck  = 20000                                 # E-Modul der Deckmaterial
Nu_Deck = 0.4                                     # Poissonsrate der Deckmaterial
Expansion_Koeffizient_Deck = 5*10**(-6)         # Expansionskoeffizient

# Aussenlage
E_Aussenlage  = 25                             # E-Modul der Aussenlagematerial
Nu_Aussenlage = 0.4							      # Poissonsrate der Aussenlagematerial
Expansion_Koeffizient_Aussenlage = 2.5*10**(-4)	  # Expansionskoeffizient der Aussenlagematerial

# Entkopplungschicht
E_Entkopplung  = 500                              # E-Modul der Entkopplungschicht
Nu_Entkopplung = 0.4						      # Poissonsrate der Entkopplungschicht
Expansion_Koeffizient_Entkopplung = 0			  # Expansionskoeffizient der Entkopplungschicht
# ---------------------------------------------------------------------------------
# Materialeigenschaften der Waben
# Type der Material
Papier_Materialtype = 0          # Isotropic: 0 ; Orthropic: 1

# Isotropische Material
E_Papier  = 1800                 # E-Modul des Papiers
Nu_Papier = 0.37                 # Poissonsrate des Papiers
# Orthropische Material
E1_Papier = 5400                 # E1: am Meisten wird E-Modul in MD-Richtung definiert
E2_Papier = 3600                 # E2: am Meisten wird E-Modul in CD-Richtung definiert
E3_Papier = 18                   # E3: am Meisten wird E-Modul in ZD-Richtung definiert
Nu12_Papier = 0.4                # Nu12: am Meisten wird Poissonsrate in MD-CD definiert
Nu13_Papier = 0.4                # Nu13: am Meisten wird Poissonsrate in MD-ZD definiert
Nu23_Papier = 0.4                # Nu23: am Meisten wird Poissonsrate in CD-ZD definiert
G12_Papier = 2400                # G12: am Meisten wird Schubmodul in MD-CD definiert
G13_Papier = 2400                # G13: am Meisten wird Schubmodul in MD-ZD definiert
G23_Papier = 2400                # G23: am Meisten wird Schubmodul in CD-ZD definiert

# Expansionskoeffizient
Expansion_Koeffizient_Papier = 6.2*10**(-6)
# ---------------------------------------------------------------------------------

############################ Beginn des Modellaufbau ##############################
mdb.Model(name='S4', modelType=STANDARD_EXPLICIT)     # Neu-Modell
Model = mdb.models['S4']                              # Name des Modells
Assembly = Model.rootAssembly
# ---------------------------------------------------------------------------------
#: Modell aufbauen
#: Wabenpart wird durch Input-File importiert
mdb.Model(name='S4', modelType=STANDARD_EXPLICIT)     # Neu-Modell
Model = mdb.models['S4']                              # Name des Modells
Assembly = Model.rootAssembly
# ---------------------------------------------------------------------------------
#: Modell aufbauen
#: Wabenpart wird durch Input-File importiert
path = os.getcwd()
Model.PartFromInputFile(inputFileName = path + '\S4.inp')
Model.parts.changeKey(fromName='PART-1', toName='Waben')
Part_Waben = Model.parts['Waben']

x_Waben = []
y_Waben = []
z_Waben = []
# Ermittelung der Size der Waben
WabenNode = Model.parts['Waben'].nodes
for i in range(len(WabenNode)):
    x_Waben.append(WabenNode[i].coordinates[0])
    y_Waben.append(WabenNode[i].coordinates[1])
    z_Waben.append(WabenNode[i].coordinates[2])

x_WabenMax = max(x_Waben)
x_WabenMin = min(x_Waben)
y_WabenMax = max(y_Waben)
y_WabenMin = min(y_Waben)
z_WabenMax = max(z_Waben)
z_WabenMin = min(z_Waben)

Laenge_Waben = x_WabenMax-x_WabenMin
Breite_Waben = y_WabenMax-y_WabenMin
Dicke_Waben  = z_WabenMax-z_WabenMin 
Lange_Breit_Waben = (Laenge_Waben, Breite_Waben)         # Geometrie der anderen Schicht laut Waben definieren

#: Oberdeck
s2 = Model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.rectangle(point1=(0, 0), point2=(Laenge_Waben, Breite_Waben))
Part_Deck_O = Model.Part(name='Deck_O', dimensionality=THREE_D, type=DEFORMABLE_BODY)
Part_Deck_O = Model.parts['Deck_O']
Part_Deck_O.BaseShell(sketch=s2)

#: Unterdeck
s3 = Model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s3.geometry, s3.vertices, s3.dimensions, s3.constraints
s3.setPrimaryObject(option=STANDALONE)
s3.rectangle(point1=(0, 0), point2=(Laenge_Waben, Breite_Waben))
Part_Deck_U = Model.Part(name='Deck_U', dimensionality=THREE_D, type=DEFORMABLE_BODY)
Part_Deck_U = Model.parts['Deck_U']
Part_Deck_U.BaseShell(sketch=s3)
# ---------------------------------------------------------------------------------
############################## Materialdefinition #################################
# Definition des Papiers
Material_Papier = Model.Material(name='Papier')
Material_Papier.Expansion(table=((Expansion_Koeffizient_Papier, ), ))
if Papier_Materialtype == 0:
    Material_Papier.Elastic(table=((E_Papier, Nu_Papier), ))
else:
    Material_Papier.elastic.setValues(type=ENGINEERING_CONSTANTS, table=((E1_Papier, E2_Papier, E3_Papier,
                                                                          Nu12_Papier, Nu13_Papier, Nu23_Papier,
                                                                          G12_Papier, G13_Papier, G23_Papier), ))

# Definition der Aussenlagematerial
# PUR-Schaum
Material_Papier_Aussenlage = Model.Material(name='Aussenlage')
Material_Papier_Aussenlage.Elastic(table=((E_Aussenlage, Nu_Aussenlage), ))
Material_Papier_Aussenlage.Expansion(table=((Expansion_Koeffizient_Aussenlage, ), ))

# Definition der Deckmaterial
Material_Papier_Deck = Model.Material(name='Deckmaterial')
Material_Papier_Deck.Elastic(table=((E_Deck, Nu_Deck), ))
Material_Papier_Deck.Expansion(table=((Expansion_Koeffizient_Deck, ), ))

# Definition der Entkopplungschicht
Material_Papier_Entkopplung = Model.Material(name='Entkopplung')
Material_Papier_Entkopplung.Elastic(table=((E_Entkopplung, Nu_Entkopplung), ))
Material_Papier_Entkopplung.Expansion(table=((Expansion_Koeffizient_Entkopplung, ), ))
# ---------------------------------------------------------------------------------
# Materialeigenschaften zun Parts einzufuegen
# Waben
Model.HomogeneousShellSection(name='Papier', material='Papier', thickness=Dicken_Papier)
Element_Waben = Part_Waben.elements
region = Part_Waben.Set(elements=Element_Waben, name='Set-Waben')
Part_Waben.SectionAssignment(region=region, sectionName='Papier', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# Oberdeck
Model.HomogeneousShellSection(name='Oberdecke', material='Aussenlage', thickness=Dicken_Aussenlage)
face_Deck_O = Part_Deck_O.faces
Part_Deck_O.Set(faces=face_Deck_O, name='Set-Deck_O')
region = Part_Deck_O.sets['Set-Deck_O']
Part_Deck_O.SectionAssignment(region=region, sectionName='Oberdecke', offset=0.0, offsetType=BOTTOM_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# Unterdeck
Model.HomogeneousShellSection(name='Unterdecke', material='Deckmaterial', thickness=Dicken_Deckschicht)
face_Deck_U = Part_Deck_U.faces
Part_Deck_U.Set(faces=face_Deck_U, name='Set-Deck_U')
region = Part_Deck_U.sets['Set-Deck_U']
Part_Deck_U.SectionAssignment(region=region, sectionName='Unterdecke', offset=0.0, offsetType=TOP_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# ---------------------------------------------------------------------------------

################################### Assembly ######################################
# Instance_Waben
Assembly.DatumCsysByDefault(CARTESIAN)
Assembly.Instance(name='Waben', part=Part_Waben, dependent=ON)
Assembly.translate(instanceList=('Waben', ), vector=(0.0, -y_WabenMin, 0.0))            # Part zuordernen

# Instance_Deckschicht
# Deckschichten werden ober sowie unter symmetrische erstellt.
# Obere Deckschicht
Assembly.Instance(name='Deck_O', part=Part_Deck_O, dependent=ON)
Assembly.translate(instanceList=('Deck_O', ), vector=(0.0, 0.0, Dicke_Waben))
# Untere Deckschicht
Assembly.Instance(name='Deck_U', part=Part_Deck_U, dependent=ON)
Assembly.translate(instanceList=('Deck_U', ), vector=(0.0, 0.0, 0.0))
# ---------------------------------------------------------------------------------

################################## Interaction ####################################
# Tie-Verbindung zwischen der Parts
# Set-Surface
# Waben
WabenInstance_nodes = Assembly.instances['Waben'].nodes
# getByBoundingBox(<xMin, yMin, zMin, xMax, yMax, zMax>)
Set_WabenUnten = WabenInstance_nodes.getByBoundingBox(0, 0, 0, Laenge_Waben, Breite_Waben, 0)
Set_WabenOben = WabenInstance_nodes.getByBoundingBox(0, 0, Dicke_Waben, Laenge_Waben, Breite_Waben, Dicke_Waben)
Assembly.Set(nodes=Set_WabenOben, name='Set_WabenOben')
Assembly.Set(nodes=Set_WabenUnten, name='Set_WabenUnten')

# Surface-Deckschicht (Ober)
s1 = Assembly.instances['Deck_O'].faces
Assembly.Surface(side2Faces=s1, name='Surface_Deck_O')
# Surface-Deckschicht (Unter)
s2 = Assembly.instances['Deck_U'].faces
Assembly.Surface(side1Faces=s2, name='Surface_Deck_U')

# Surface to Nodes
Model.Tie(name='Constraint-1', master=Assembly.surfaces['Surface_Deck_O'], slave=Assembly.sets['Set_WabenOben'], positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
Model.Tie(name='Constraint-2', master=Assembly.surfaces['Surface_Deck_U'], slave=Assembly.sets['Set_WabenUnten'], positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
# ---------------------------------------------------------------------------------

###################################### Mesh #######################################
# Deck
Part_Deck_O.seedPart(size=PartMeshsize_Deck, deviationFactor=0.1, minSizeFactor=0.1)
Part_Deck_O.generateMesh()
Part_Deck_U.seedPart(size=PartMeshsize_Deck, deviationFactor=0.1, minSizeFactor=0.1)
Part_Deck_U.generateMesh()

# Elementtype S4
elemType1 = ElemType(elemCode=S4, elemLibrary=STANDARD, secondOrderAccuracy=OFF)
elemType2 = ElemType(elemCode=S3, elemLibrary=STANDARD)
Part_Deck_U.setElementType(regions=(face_Deck_U,), elemTypes=(elemType1, elemType2))
Part_Deck_O.setElementType(regions=(face_Deck_O,), elemTypes=(elemType1, elemType2))
# ---------------------------------------------------------------------------------

###################################### Load #######################################
# Set_XYZFest
v_Deck_U = Assembly.instances['Deck_U'].vertices
Set_XYZFest = v_Deck_U.findAt(((0.0, 0.0, 0.0), ))
Assembly.Set(vertices=Set_XYZFest, name='Set_XYZFest')

# Set_YZFest
Set_YZFest = v_Deck_U.findAt(((Laenge_Waben, 0.0, 0.0), ))
Assembly.Set(vertices=Set_YZFest, name='Set_YZFest')

# Set_YFest
v_Deck_O = Assembly.instances['Deck_O'].vertices
Set_YFest = v_Deck_O.findAt(((0.0, 0.0, Dicke_Waben), ))
Assembly.Set(vertices=Set_YFest, name='Set_YFest')

# Set-Fuer Output
Assembly.regenerate()
Nodes_Deck_O = Assembly.instances['Deck_O'].nodes

Y_Mittel = []
Y_Ober = []
Y_Unter = []
Y_Link = []
Y_Recht = []

Ober_Nodes = Nodes_Deck_O.getByBoundingBox(0-0.01, Breite_Waben-0.01, Dicke_Waben, Laenge_Waben+0.01, Breite_Waben+0.01, Dicke_Waben)
Unter_Nodes = Nodes_Deck_O.getByBoundingBox(0-0.01, 0-0.01, Dicke_Waben, Laenge_Waben+0.01, 0+0.01, Dicke_Waben)
Link_Nodes = Nodes_Deck_O.getByBoundingBox(0-0.01, 0-0.01, Dicke_Waben, 0+0.01, Breite_Waben+0.01, Dicke_Waben)
Recht_Nodes = Nodes_Deck_O.getByBoundingBox(Laenge_Waben-0.01, 0-0.01, Dicke_Waben, Laenge_Waben+0.01, Breite_Waben+0.01, Dicke_Waben)
Y_Posi=[]
for i in Link_Nodes:
    Y_Posi.append(i.coordinates[1])
Y_Posi.sort()
Mittel_Y_Posi = Y_Posi[len(Y_Posi)/2]
Tol_E = 0.0001 # Toleranz
Mittel_Nodes = Nodes_Deck_O.getByBoundingBox(0-Tol_E, Mittel_Y_Posi-Tol_E, Dicke_Waben, Laenge_Waben+Tol_E, Mittel_Y_Posi+Tol_E, Dicke_Waben)

for i in Mittel_Nodes:
    Y_Mittel.append(i.label)
for i in Ober_Nodes:
    Y_Ober.append(i.label)
for i in Unter_Nodes:
    Y_Unter.append(i.label)
for i in Link_Nodes:
    Y_Link.append(i.label)
for i in Recht_Nodes:
    Y_Recht.append(i.label)
    
Assembly.SetFromNodeLabels(name='Set_Output_Mittel', nodeLabels=(('Deck_O', Y_Mittel), ), unsorted=True)
Assembly.SetFromNodeLabels(name='Set_Output_Ober', nodeLabels=(('Deck_O', Y_Ober), ), unsorted=True)
Assembly.SetFromNodeLabels(name='Set_Output_Unter', nodeLabels=(('Deck_O', Y_Unter), ), unsorted=True)
Assembly.SetFromNodeLabels(name='Set_Output_Link', nodeLabels=(('Deck_O', Y_Link), ), unsorted=True)
Assembly.SetFromNodeLabels(name='Set_Output_Recht', nodeLabels=(('Deck_O', Y_Recht), ), unsorted=True)

# Output-Oberflache
# getByBoundingBox(<xMin, yMin, zMin, xMax, yMax, zMax>)
Set_Oberflaesche = Nodes_Deck_O.getByBoundingBox(0-Tol_E, 0-Tol_E, Dicke_Waben, Laenge_Waben+Tol_E, Breite_Waben+Tol_E, Dicke_Waben)
Assembly.Set(name='Oberflaeche_Oberdeck', nodes=Set_Oberflaesche)
# ---------------------------------------------------------------------------------

################################# Step Definition #################################
Model.StaticStep(name='Expansion', previous='Initial')
Model.fieldOutputRequests['F-Output-1'].setValues(variables=('U', 'E', 'S'))			# FieldOutput
#Model.historyOutputRequests['H-Output-1'].setValues(rebar=EXCLUDE, region=Assembly.sets['Set_Output_Mittel'], sectionPoints=DEFAULT, variables=('UT', ))	
# ---------------------------------------------------------------------------------
# RB
# BC1
Model.DisplacementBC(name='BC-1', createStepName='Initial', region=Assembly.sets['Set_YFest'], u1=UNSET, u2=SET, u3=UNSET, 
                     ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# BC2
Model.DisplacementBC(name='BC-2', createStepName='Initial', region=Assembly.sets['Set_YZFest'], u1=UNSET, u2=SET, u3=SET, 
                     ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# BC3
Model.DisplacementBC(name='BC-3', createStepName='Initial', region=Assembly.sets['Set_XYZFest'], u1=SET, u2=SET, u3=SET, 
                    ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# Set-T wird fuer Randbedingung der Temperaturaederung hier aufgestellt
n1 = Assembly.instances['Deck_O'].nodes
nodes1 = n1[0:len(n1)]
n2 = Assembly.instances['Deck_U'].nodes
nodes2 = n2[0:len(n2)]
n3 = Assembly.instances['Waben'].nodes
nodes3 = n3[0:len(n3)]
Assembly.Set(nodes=nodes1+nodes2+nodes3, name='Set-T')
#
Model.Temperature(name='Predefined Field-1', createStepName='Expansion', region=Assembly.sets['Set-T'], distributionType=UNIFORM, crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, magnitudes=(75.0, ))
###
# Regenerate
#Assembly.regenerate()
# ---------------------------------------------------------------------------------

####################################### Job #######################################
mdb.Job(name='JobS4', model='S4', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)                                                                    
mdb.jobs['JobS4'].writeInput(consistencyChecking=OFF)