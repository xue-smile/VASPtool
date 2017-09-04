#-------------------------------------------Introduction------------------------------------------------
#In polaron modeling, we see a change in the bond lengths within a cystal structure when a charge is
# placed on an atom. We can use this idea to move an electron or hole from one atom to another in a 
# crystal.
#This is used in ab initio methods to determine charge mobility
#Here we use python to help model this behavior.
#We define simple functions to help us manipulate the position_vector file.
#This program is set up to use the POSCAR file in VASP.
#This program can manipulate the bond length of neighboring atoms around a central atom. This will create
# a new file with the adjusted structure so that we can move our hole or electron to or from that atom.
#This code is also designed to perform a linear interpolation between a initial and final state structure:
# This function requires initial state and final state position vector files
# The output file is a state inbetween the initial and final state.
#-------------------------------------------------------------------------------------------------------
import os
import math

#--------------------Part 1: Creating a file for an electron/hole transfer------------------------------

def polaroncalc(poscar_file,alpha,neighboring_ions,atom_serial_number, destination_file):

    with open(poscar_file,'r') as f:
        get_all=f.readlines()
        for i, line in enumerate(get_all,-7):
            if i==atom_serial_number:
                metal_ion=line.split( )
                metal_ion=[float(n) for n in metal_ion]


####This section calculates a new coordinate for each neighboring ion####
####Coordinates are converted back to string to write to file####
    for oxy in range(len(neighboring_ions)):
        with open(destination_file,'w') as f:
            for i, line in enumerate(get_all,-7):
                if i==neighboring_ions[oxy]:
                    oline=line.split( )
                    oline = [float(n) for n in oline]
                    o_coord_new=[]
                    for n, ocoord in enumerate(oline):
                        MO_old=ocoord-metal_ion[n]
                        MO_new=alpha*MO_old
                        o_new=MO_new+metal_ion[n]
                        str_o=format(o_new, '.16f')
                        o_coord_new.append(str_o)
                    xyz="  ".join(o_coord_new)
                    f.writelines("  "+xyz+'\n')
                    print xyz
                else:
                    f.writelines(line)
        with open(destination_file,'r') as f:
            get_all=f.readlines()
    return destination_file


####Use distance formula to find the nearest neighbors.####
####Verify coordinates with Vesta, Avogadro or other structure modeling software####
####distances are calculated in direct coordinates, not angstroms####
####This can be used as input into polaroncalc for oxygen neighbors if desired####
####Compare the bondlenths of neighboring atoms####

#def periodic_boundary(distance):    
    
    #for n,atom in enumerate(distance):
    #    for component in atom:
#    if distance > 0.5:
#        distance = distance - 1
        #component = format(distance,'.16f')
               
#    elif distance < -0.5:
#        distance = distance + 1
        #    component = format(component,'.16f')
               
#    return distance    

#def distance(p0,p1):
#    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2 + (p0[2] - p1[2])**2)

def neighbor_finder(poscar_file, atom_serial_number,coordination_number):
####poscar_file: input vector file####
####atom_serial_number: serial number coorsponding to central atom of interest####
####coordination number: number of bonded neighbors####
    import numpy as np #for arrays
    import heapq #for sorting
    distances=[]
    a_vectorT=[]
####This section opens the position vector file, reads the file into get_all.####
####Then the atom serial number is place into an array####
   
    with open(poscar_file,'r') as f:
        get_all=f.readlines()
        for i, line in enumerate(get_all,-7):
            if i==atom_serial_number:
                metal_ion=line.split(   )
                metal_ion=[float(n) for n in metal_ion]
                ion_array=np.array(metal_ion)
            if i <=-3 and i >=-5:
                a_vectT=line.split( )
                a_vectT=[float(n) for n in a_vectT]
                a_vectorT.append(a_vectT)
                np.array(a_vectorT)
       
            
    for n, line in enumerate(get_vector(poscar_file)):
        neighbor_array=np.array(line)
        dist = np.linalg.norm(([periodic_boundary(ion_array[i]*a_vectorT-neighbor_array[i]*a_vectorT) for i in range(2)]))
        distances.append(dist)
    ksmall=heapq.nsmallest((coordination_number+1), range(len(distances)),distances.__getitem__)
    kdist=heapq.nsmallest((coordination_number+1), distances)
    n = 0
    while n < len(ksmall): #change numbering to start at 1
        ksmall[n]=ksmall[n] + 1
        n=n+1

    neighbor_table={}
    for i in range(len(ksmall)):
        neighbor_table[ksmall[i]]=kdist[i]
    for key, item in neighbor_table.items():
        if key is atom_serial_number:
            del neighbor_table[key]
    return neighbor_table

    

#--------------------Part 2: Creating multiple files for determining transition state energy------------
change_steps=(0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0) 
####creates a list of increments to change atom positions by####

####this section creates a template to copy data from when we write our output file####
def make_file(inputfile):
####inputfile: use initial POSCAR file as input for most cases####
    with open(inputfile,'r') as f:
        outputfile=f.readlines()
        return outputfile


####this counts the number of atoms in the POSCAR file so that we can make a list of coordinates for any 
# size structure####
def count_atom(inputfile):
####inputfile: use initial POSCAR file as input for most cases#### 
    for i, line in enumerate(make_file(inputfile)):
        total=0
        if i ==6:
            atom_count=line.split()
            atom_count=[int(n) for n in atom_count]
            count=0
            while count < len(atom_count):
                total=total+atom_count[count]
                count = count +1
            return total

      
    
####this section reads intial and final position of atoms from the initial and final state 
# position vector files####
####we input files that represent the atom on one atom(initial) and a neighbor atom (final)####
####the result is a nested list of atom coordinates, the values are floating points:
# list[atom1[coordinate_x,coordinate_y,coordinate_z]
####we also make a dictionary that can be used as a quick reference for each of the position vector files####     
####if the file format is incorrect an error message will appear (try, expect)
def get_vector(workingfile):
####workingfile: initial and final state position vector files. Usually a list of two files####
    try:
        with open(workingfile,'r') as f:  ##with funtion to open and close a file
            whole_file=f.readlines()  ##reads all lines of file
            vector=[]
            for i, line in enumerate(whole_file,-7):
                if i >= 1 and i<=count_atom(workingfile):  ##for loop over the coordinates of BiVO3 supercell with 0 velocity
                    coordinates=line.split( )  
                    coordinates=[float(n) for n in coordinates]
                    vector.append(coordinates)  ##now each atom is a list of its coodinates (list of lists)
        return vector
    except:
        print "Not a valid position vector file!"
        print """Position vector file requires format:'\n' atom line 5'\n' #of atoms line 6'\n' begin position coordinates line 9 """


####This section does the calculation that we want to do to the POSCAR coordinates####
####It returns the values as a nested list, where each sublist is a set of string values####

def change_bond(workingfiles,change_step):
####workingfiles: initial and final state position vector files. Usually a list of two files####
####changestep: a number between 0 and 1, where 0 is the initial state and 1 is the final state position####
    import numpy as np
    output_coordinates=[]
    initial_state=get_vector(str(workingfiles[0]))
    initial_state= np.array(initial_state)
    final_state=get_vector(str(workingfiles[1]))
    final_state=np.array(final_state)
    output_position=((1-change_step)*initial_state+final_state*change_step)
    output_position=output_position.tolist()
    for lst in output_position:
        for i in range(len(lst)):
            lst[i]=format(lst[i],'.16f')
           
    for lst in output_position:
        for i in range(len(lst)):
            if lst[i][0] !='-':
                lst[i]=' '+ lst[i]
        output_line=' '.join(lst)
        output_coordinates.append(output_line)
    
    return output_coordinates
"""
####This section does the calculation that we want to do to the POSCAR coordinates####
####It returns the values as a nested list, where each sublist is a set of string values####
def periodicity(workingfiles):
####workingfiles: initial and final state position vector files. Usually a list of two files####
####changestep: a number between 0 and 1, where 0 is the initial state and 1 is the final state position####
    import numpy as np
    output_coordinates=[]
    initial_state=get_vector(str(workingfiles[0]))
    initial_state= np.array(initial_state)
    final_state=get_vector(str(workingfiles[1]))
    output_position=np.array(final_state)
    
    for lst in final_state:
        for i in range(len(lst)):
            if lst[i] < 0.5 and lst > 0.5:
                lst[i] = format(lst[i],'.16f')
            elif lst[i] > 0.5:
                lst[i] = 1 + lst[i]
                lst[i] = format(lst[i],'.16f')
            else:
                lst[i] = lst[i] - 1
                lst[i] = format(lst[i],'.16f')
     
    for lst in output_position:
        for i in range(len(lst)):
            if lst[i][0] !='-':
                lst[i]=' '+ lst[i]
        output_line=' '.join(lst)
        output_coordinates.append(output_line)
    
    return output_coordinates


periodicity(['init_POSCAR','fin_POSCAR'])"""
####finally we use the list from change bond and insert it into write file####
####write file creates a new file with the changes from change bond####
####writing to files is file by file because the user will likely want to change file paths
# and file names####
def interpolation(new_file, workingfiles, change_step):
####new_file: file name for the output file####
####workingfiles: initial and final state position vector files. Usually a list of two files#### 
####change_step:  a number between 0 and 1, where 0 is the initial state and 1 is the final state position####
    call=change_bond(workingfiles,change_step)
    with open(new_file,'w') as f:
            for i, line in enumerate(make_file(workingfiles[0]),-7):
                if i >= 1 and i <= count_atom(workingfiles[0]):
                    f.writelines('  ' + call[i-1] + '\n')
                else:
                    f.writelines(line)
    return new_file


print neighbor_finder('init_POSCAR',1,6)