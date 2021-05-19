# encoding=utf-8
from odbAccess import *
import os


path = os.getcwd()
# Odb.File Name
def set_U_Output(name_ODB, name_Set, file):

    FOdb = session.openOdb(name=name_ODB)
    Assembly = FOdb.rootAssembly

    numnodes = 0
    for instance in Assembly.instances.values():                              #: calculate amount of nodes. here muss use values()
        n = len(instance.nodes)
        numnodes = numnodes + n
    
    fieldoutput_node = Assembly.nodeSets[name_Set]                            # :the set is defined in Assembly 
    Verschiebung = FOdb.steps['Expansion'].frames[-1].fieldOutputs['U']       # :-1 means the last frame(1 is also OK here),fieldOutputs to return values of displacements
    Verschiebung_Set = Verschiebung.getSubset(region=fieldoutput_node)        #: get values of Set-Output

    csv_name = name_ODB.rsplit('\\', 1)[1].split('.')[0]+'_'+name_Set+'.csv'
    with open(file+'\\'+csv_name, 'w+') as f1:
        f1.write(str(numnodes))
        f1.write('\n')
        for i in Verschiebung_Set.values:
            f1.write(str(i.nodeLabel))
        # x y z koordinaten
            for j in range(0, 3):
                f1.write(',')
                f1.write(str(Verschiebung.values[0].instance.getNodeFromLabel(int(i.nodeLabel)).coordinates[j]))   #: 0 means instance of NO.1 value,here 1,2,3...are also OK 
            f1.write(',')
        # u3
            f1.write(str(i.data[2]))                                          #: [2] means U3
            f1.write('\n')

def file_out(setname):
    setname = setname.upper()
    file = path+'\\'+setname
    if not os.path.exists(file):
        os.mkdir(file)
    for fpathe, dirs, fs in os.walk(path):
        for f in fs:
            filename = os.path.join(fpathe, f) 
            if filename.endswith('.odb'):
                set_U_Output(filename, setname, file)
                

file_out('Set_Output_Mittel')
