#These are the dependencies needed by the software
#-----------------------------------------------------------
import subprocess
import os 
import os.path
from subprocess import Popen, PIPE
import time
import math
import tempfile
import RNA
import numpy as np
import pandas as pd
from openpyxl import Workbook
#-----------------------------------------------------------
#PrimedRPA
#-----------------------------------------------------------
    # For the software to run, the parameters file and the functions file must be on the same directory
parameters = input ('Parameters File Name: ')
def primed_rpa(parameters): 
    subprocess.Popen(['PrimedRPA', parameters])

#Primed_rpa(parameters)
#Time.sleep(35)
#-----------------------------------------------------------


#Pandas
#-----------------------------------------------------------
#FASTA file with the sequences of interest
fastaname = input('Fasta File Name: ')
#No of primers, more primers also mean more sequences generated
num_primers = int(input('Number of Desired Primer Pairs: '))
#Primer parameters file, you can find it on the repository
primer_file = input('Output file name of PrimedRPA Run: ')
#Usually 1 kcal/mol but will depend on your specific project
rango_energ = int(input('Energy range for calculating suboptimal structures (kcal/mol): ')) 
seq_fasta = open(fastaname, "r")
tar_seq_in = seq_fasta.readlines()
seq_fasta.close()
df = pd.read_csv(primer_file, usecols=["Amplicon Size","FP Binding Start Site","FP GC%","Forward Primer (FP)","Max Dimerisation Percentage Score","RP Binding Start Site","RP GC%","Reverse Primer (RP)","Reverse Primer Length"]) 
df.columns = ['amplicon_size','fpbind','fpgc','forward_primer','maxdim_score','rpbind','rpgc','reverse_primer','rp_length']#filtro para el archivo de primers (tomar en cuenta consideraciones de guia de twist: https://www.twistdx.co.uk/docs/default-source/RPA-assay-design/twistamp-assay-design-manual-v2-5.pdf?sfvrsn=29)
filter = df[(df.amplicon_size >= 95) & (df.amplicon_size <= 200) & (df.fpgc > 30) & (df.fpgc < 70) & (df.rpgc > 30) & (df.rpgc < 70) & (df.maxdim_score < 40)]
# Take into consideration that the Amplicon Size isn't always 100 !!!
listed = filter.sort_values(['maxdim_score','amplicon_size'], ascending=[True, True]) 
primers = listed.iloc[0:num_primers][:] 

#We started to create the amplicon that will be used f
def amplicon(primers, tar_seq_in):
    tar_seq_con=[]
    tar_seq = ""
    x = int(len(primers))
    amplicons = []
    id_primer = []
    #Eliminates file name
    tar_seq_in.pop(0)
    for element in tar_seq_in:
        tar_seq_con.append(element.strip())
    for element in tar_seq_con:
        tar_seq += str(element)
    for i in range (x):
        length = (int(primers.iat[i,8]))
        fp = (int(primers.iat[i,1]))
        rp = (int(primers.iat[i,5]) + length) 
        seq_amplicon = tar_seq[fp:rp]
        amplicons.append(seq_amplicon)
        id_primer.append(i+1)
    primers.insert(5,"amplicon",amplicons,False)
    primers.insert(6,'id',id_primer,False)
    return primers

#We create our primer list
listaprimers = amplicon(primers, tar_seq_in)
#-----------------------------------------------------------


#Toehold Designer
#-----------------------------------------------------------
#Variables
structure = '..............................(((((((((...((((((...........))))))...)))))))))..............................'
window = 36
result_path = ''
constante_r = 0.00198720425864083 #Kcal/(K*mol)
temp = 310.15 #Kelvin (37ºC)

#Functions for toehold creation:
def split_sequence(sequence, window): #Sliding window iteration
    #Creates a new list of possible sequences for the toehold
    sequences = []
    #Creates a limit for the iterations depending the lenght of the RNA sequence and the sliding window
    limit = len(sequence) - window + 1
    #This iteration allows you to add to the list all the fragments of the target sequence that can be used to create the toehold
    for i in range(0, limit):
        sequences.append(sequence[i:window + i])
    return sequences

def reversed_complement(sequence):
    #Mapping is a dictionary with all the nucleotides
    mapping = {'A': 'U', 'G': 'C', 'U': 'A', 'C': 'G'}
    sequence_upper = sequence.upper()
    complement = ''
    #For each nucleotide inside the sequence's fragment this will create its complement
    for c in sequence_upper:
        complement += mapping[c]
    #Reversed the entire sequence
    return complement[::-1]

    #Filter in order to avoid stop codons that may interfer with our translation process
def no_stop(sequence):
    stop = ['UAA', 'UAG', 'UGA']
    for i in range(0, len(sequence), 3):
        #If the sequence contains any of hte 3 stop codons, it will break and return false if not return true
        if sequence[i:i + 3] in stop:
            return False
    return True

    #Inputs: List of fragments of the target sequence and list of the complementary sequences of those fragments
def possible_toehold_A(reg_sequences, rev_comp_sequences):
    #The loop and the linker are toehold standarized parts, taken from the design made by Pardee et al on their Zika detection paper
    loop = 'GUUAUAGUUAUGAACAGAGGAGACAUAACAUGAAC'
    linker = 'GUUAACCUGGCGGCAGCGCAAAAG'
    #Toehold empty dictionary
    toeholds = {}
    #Zip() creates an iterator that returns tuples in the form of (complementary sequence, sequence fragment)
    for rev, reg in zip(rev_comp_sequences, reg_sequences):
        #Calls the function no_stop() that takes the input: The sequence fragment in the index [0:6] 
        # Calls to the reversed_complement() function to return the complement sequence from the index [0:3] of the sequence fragment + the linker 
        if no_stop(reg[0:6] + 'AAC' + reversed_complement(reg[0:3]) + linker):
            #If no_stop returns True, takes the sequence fragment and adds to its complement inside the dictionary that will composed the toehold
            toeholds[reg] = rev + loop + reg[0:6] + 'AAC' + reversed_complement(reg[0:3]) + linker
    #Finally returns the toehold dictionary containing each sequence fragment with its respective toehold only for the toeholds that does not posses any stop codons
    return toeholds
#-----------------------------------------------------------


#Filter functions for the generated toeholds 
#-----------------------------------------------------------

#Function that calculates the linearity of our target sequence
def target_single_strandedness (amplicon, target):
    replacement = ''
    fc = RNA.fold_compound(amplicon)
    (mfe_struct, mfe) = fc.mfe()
    fc.exp_params_rescale(mfe)
    #Computes partition function
    (pp, pf) = fc.pf()
    eall = pf #kcal/mol
    loc = amplicon.index(target)
    length = len(target)
    for i in range (length):
        replacement += 'x'
    mod_est = mfe_struct[:loc] + replacement + mfe_struct[(loc + length):]
    mod_est = mod_est.replace('(', '.')
    mod_est = mod_est.replace(')', '.')
    p = subprocess.Popen(['RNAfold', '-C', '-p'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(bytes(amplicon + '\n' + mod_est + '\n', 'utf-8'))
    p_output = p.communicate()[0]
    p.stdin.close()
    x=str(p_output)
    os.remove('dot.ps')
    os.remove('rna.ps')
    ind = x.index('[')
    ind2 = x.index(']')
    eunpaired = float(x[(ind+1):(ind2)])
    pu = math.exp((eall - eunpaired)/(constante_r * temp))
    return pu

#Function that calculates the linearity of our toehold
def toehold_single_strandedness (toehold):
    replacement = ''
    fc = RNA.fold_compound(toehold)
    (mfe_struct, mfe) = fc.mfe()
    fc.exp_params_rescale(mfe)
    #Computes partition function
    (pp, pf) = fc.pf()
    eall = pf #Kcal/mol
    for i in range (30):
        replacement += 'x'
    mod_est = replacement + mfe_struct[30:]
    mod_est = mod_est.replace('(', '.')
    mod_est = mod_est.replace(')', '.')
    p = subprocess.Popen(['RNAfold', '-C', '-p'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(bytes(toehold + '\n' + mod_est + '\n', 'utf-8'))
    p_output = p.communicate()[0]
    p.stdin.close()
    x=str(p_output)
    os.remove('dot.ps')
    os.remove('rna.ps')
    ind = x.index('[')
    ind2 = x.index(']')
    eunpaired = float(x[(ind+1):(ind2)])
    pu = math.exp((eall - eunpaired)/(constante_r * temp))
    return pu

#Function that returns the average number of nucleotides mismatched in equilibrium according to a given secondary structure
def ensemble_defect(sequence, structure): 
    fc = RNA.fold_compound(sequence) #Calculates the secondary structure of the toehold
    (mfe_struct, mfe) = fc.mfe()  #Minimum Free Energy (MFE)
    (propensity, ensemble_energy) = fc.pf()
    defect = fc.ensemble_defect(structure)
    x=[mfe_struct,mfe,defect] #Matrix with the toeholds secondary structure, the MFE value and the defect value
    return x

#Function that returns the delta gibbs energy that correlates with the reporter expression of the Switch-Trigger duplex
def delta_gibbs(sequence, toehold):
    p = subprocess.Popen(['RNAup', '-b', '-o'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(bytes(sequence + '\n' + toehold + '\n', 'utf-8'))
    p_output = p.communicate()[0]
    p.stdin.close()
    x=str(p_output[71:77])
    return x


#This function takes the sequences and the energetic range to compute a dictionary with the structures and the MFE 
#The key is the structure with dot-parentesis format
#The interpretation was taken from: https://www.tbi.univie.ac.at/RNA/ViennaRNA/doc/html/examples_python.html
def RNASubopt(sRNA, dRangoEnergía):
    aEstructuras={}

    #Set global switch for unique ML decomposition (intact variable)
    RNA.cvar.uniq_ML=1

    #Dictionary for the program insformation
    #Counts variable allows to numbre the suboptimal structures
    aDatosSubopt={'contador':1, 'secuencia':sRNA}

    #This cicle iterates over the generated structures
    def imprimeEstSubopt(estructura, energia, diccionario):
        if not estructura == None:
            aEstructuras[estructura]=energia

            #We increas the counter
            diccionario['contador']=diccionario['contador']+1

            #Break the counter after meeting all structures

    #Creates a 'fold_compund' for our sequence
    a=RNA.fold_compound(sRNA)

    #Enumerates the structures that shared a rank of xdacal/mol or x/100 kcal/mol
    # MFE and print the structures with the following function
    
    a.subopt_cb(dRangoEnergía*100, imprimeEstSubopt, aDatosSubopt)
    
    ##Finally, we order the dictionary from minor to major MFE values 
    aEstructuras={k:v for k, v in sorted(aEstructuras.items(), key=lambda item: item[1])}

    datos={'Estructura':[], 'MFE':[]}
    datos['MFE']=list(aEstructuras.values())
    datos['Estructura']=[*aEstructuras]

    dfEstructurasMFE=pd.DataFrame.from_dict(datos)
    return dfEstructurasMFE

def toehold_filter(toeholds, target, structure):
    th_list = [] #Toehold final list
    tar_list=[] #Target list
    mfe_list=[] #MFE values list
    mfestruct_list=[] #List with toeholds secondary structures
    gibbs_list=[]#Gibbs free energy
    cofoldlist=[] #MFE structure and MFE toehold-target complex
    score = [] #Sensor score

    for tar, toehold in toeholds.items():
        id = target.index(tar) #Creates an id depending on the targer sequence position 
        th_list.append(toehold)
        sensor_defect = (ensemble_defect(toehold, structure)[2])
        mfe_list.append(ensemble_defect(toehold, structure)[1])
        mfestruct_list.append(ensemble_defect(toehold, structure)[0])
        tar_list.append(tar)
        seq_defect = target_single_strandedness(target, tar)
        th_defect = toehold_single_strandedness(toehold)
        score_value = 5*(1-seq_defect) + 4*(1-th_defect) + 3*sensor_defect
        score.append(score_value)
        
        
    df = pd.DataFrame(th_list,columns=['Toeholds'])
    df.insert(1,'Target',tar_list,False)
    df.insert(2,'Score',score,False)
    df.insert(3,'MFE',mfe_list,False)
    df.insert(4,'MFE_Structure',mfestruct_list,False)
    
    #Score values
    df = df[(df.Score <= 10)] #Score filtration (0 es better and 100 is worst)
    df = df.sort_values('Score', ascending=True) #Minor to major score values
    df = df.iloc[0:15][:] #We take the first 15

    #Cofold function filter
    for values in (df['Toeholds']): 
        keyTmp = str(values) 
        keyTmp = keyTmp+"&"+target
        cofoldlist.append(keyTmp) 
    for n in range(len(cofoldlist)):
        cofoldlist[n] = RNA.cofold(cofoldlist[n])
    tar_toe_mfestr = []
    tar_toe_mfe = []
    for x in range (len(cofoldlist)):
        tar_toe_mfestr.append(cofoldlist[x][0])
        tar_toe_mfe.append(cofoldlist[x][1])
    df.insert(5, 'Target-Toehold MFE Structure', tar_toe_mfestr, False)
    df.insert(6, 'Target-Toehold MFE', tar_toe_mfe, False)
    
    #Gibbs free energy
    for y in (df['Toeholds']):
        gibbs_list.append(delta_gibbs(target, y))
    df.insert(7, 'Delta G', gibbs_list, False)
    df = df.sort_values('Delta G', ascending=True) #Major to minor delta Gibbs
    df = df.iloc[0:10][:] #Take the first 10
    
    #MFE and delta MFE
    df = df.sort_values('MFE', ascending=True) #MFE minor to major
    df = df.iloc[0:5][:] #We select the first 5
    fc = RNA.fold_compound(target) #Calculates the targets MFD
    (mfe_struct, mfe) = fc.mfe()
    delta_mfe=[] #List of Delta MFE
    for i in range (len(df)): 
        delta_mfe.append((df.iloc[i][6])-(df.iloc[i][3] + mfe)) #Calculates the change on MFE (Delta)
    df.insert(8,'Delta MFE',delta_mfe,False) 
    df = df.sort_values('Delta MFE',ascending=True) #Minor to major

    return df
#-----------------------------------------------------------



#Sequencial order of the toeholds assembly
def creacion_toeholds(listaprimers, window):
    resultados_finales = []
    x = int(len(listaprimers))
    writer = pd.ExcelWriter('output.xlsx',engine='xlsxwriter')
    workbook=writer.book
    for i in range (x):
        seq_amplicon = listaprimers.iat[i,5]
        processed_sequence = seq_amplicon.upper().replace('T', 'U').replace(' ', '')
        reg_sequences = split_sequence(processed_sequence, window)
        rev_comp_sequences = [reversed_complement(s) for s in reg_sequences]
            #Returns a dictionary with the sequence and its possible toehold
        target_toehold_map = possible_toehold_A(reg_sequences, rev_comp_sequences)
        seq_amplicon = seq_amplicon.upper().replace('T', 'U')
        lista_toeholds = toehold_filter(target_toehold_map, seq_amplicon, structure) #Final list of toeholds (5) for each amplicon pair of primers 

        #File export and generation
        par_primers = listaprimers.iloc[i][:]
        worksheet=workbook.add_worksheet(('toeholds_' + str(i+1)))
        writer.sheets[('toeholds_' + str(i+1))] = worksheet
        worksheet.write_string(0, 0, ('Primers and Toeholds ' + str(i+1)))
        par_primers.to_excel(writer,sheet_name=('toeholds_' + str(i+1)),startrow=1 , startcol=0, index=True)
        lista_toeholds.to_excel(writer,sheet_name=('toeholds_' + str(i+1)),startrow=1, startcol=5, index=False)

        #Subopt filtering function
        aTHFiltered = lista_toeholds['Toeholds'].tolist()
        n=0
        z=2
        for toehold in aTHFiltered:
            n=n+1
            z=z+3
            toe_subopt = RNASubopt(toehold, rango_energ)  #all secondary structures with energies within 1 kcal/mol of the mfe (lista de diccionarios)
            worksheet.write_string((lista_toeholds.shape[0] + 6), z, ('Toehold '+str(n)+' Suboptimal Structures within ' + str(rango_energ) + ' kcal/mol of the mfe'))
            toe_subopt.to_excel(writer,sheet_name=('toeholds_' + str(i+1)),startrow=(lista_toeholds.shape[0] + 7), startcol=(z), index=False)

    writer.save()


creacion_toeholds(listaprimers, window)

####################
