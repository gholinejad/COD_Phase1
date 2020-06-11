# Working with input file
datas = open('./io/MicroInstruction.txt', 'r')
microins = datas.readlines() #this methos return a list of file lines index
datas.close()

#print (microins[0])

intByte = []     #a list contain 8bit index (every 4 index can map to a 32 bit word!)
MILIST = []      #a list contains generated words.
mild = []        #micro instruction list of dictionary
LSF = False
RSF = False
SBUS = 0b1111
ALU = 0b1111
Shifter = 0b111
Dest = 0b1111
Nxt = 0b1111
Address = 0b111111111111

DicTable = {     #Creating Table 5.1 in Ref.
'SBUS':{'R0': 0b0000,'R1': 0b0001,'R2': 0b0010,'R3': 0b0011,'R4': 0b0100,'R5': 0b0101,'R6': 0b0110,'R7': 0b0111,'IN': 0b1000,'Address/Constant': 0b1001} ,
'ALU':{'ACC': 0b0000,'SBus': 0b0001,'ACC+SBus': 0b0010,'ACC-SBus': 0b0011,'SBus-ACC': 0b0100,'ACC&SBus': 0b0101,'not ACC': 0b0110,'not SBus': 0b0111,'ACC+1': 0b1000,'SBus-1': 0b1001,'0': 0b1010,'1': 0b1011} ,
'Shifter':{'logical SHL(ALU)': 0b000, 'logical SHR(ALU)': 0b001, 'ALU': 0b111} ,
'Dest':{'R0': 0b0000,'R1': 0b0001,'R2': 0b0010,'R3': 0b0011,'R4': 0b0100,'R5': 0b0101,'R6': 0b0110,'R7': 0b0111,'ACC': 0b1000,'unconnected': 0b1111} ,
'Nxt':{'NoJMP': 0b0000 , 'JMP': 0b0001 , 'JMP_IF_Z': 0b0100 , 'JUMP_IF_C': 0b0010, 'JUMP_IF_NZ': 0b1100 , 'JUMP_IF_NC': 0b1010 } 
}


def seq_ins_parser(microins):
    mild = []
    for line in microins:
        NextLetter = 0
        tmpaddress = ''
        while(line[NextLetter] != ' '):
            tmpaddress = tmpaddress + line[NextLetter]
            NextLetter = NextLetter + 1
        #print(tmpaddress)


        NextLetter = NextLetter + 1 


        tmpNA = NextLetter
        tmplabel = '' 
        while(line[NextLetter] != ':'):
            tmplabel = tmplabel + line[NextLetter]
            if (NextLetter+1 == len(line)):
                NextLetter = tmpNA - 1
                tmplabel = ''
                break
            NextLetter = NextLetter + 1
        #print(tmplabel)
        

        NextLetter = NextLetter +1 


        tmpcommandfield = ''
        while(line[NextLetter+1]+line[NextLetter+2]  != '||'):
            tmpcommandfield = tmpcommandfield + line[NextLetter]
            NextLetter = NextLetter + 1
        #print (tmpcommandfield)

        NextLetter = NextLetter + 3

        tmpjumpfield = line[NextLetter:]
        #print(tmpjumpfield,'-------------------------------------------------------------')

        midic = {'address' : tmpaddress , 'label' : tmplabel , 'command' : tmpcommandfield , 'jmp': tmpjumpfield}
        mild.append(midic)
    '''
    for j in mild:
        print(j,'\n-----------') '''
    return mild
    


def RunCommand(CurrentLine):
    global LSF,RSF,SBUS,ALU,Shifter,Dest,Nxt,Address,DicTable
    CurrentCommand = CurrentLine['command']

    CCList = CurrentCommand.split('->').copy()
    if len(CCList) == 2:                         #means '->' was existed
        LoS = CCList[0].strip()
        RoS = CCList[1].strip()
        for m in DicTable['Dest']:
            if(RoS == m):
                Dest = DicTable['Dest'][m]
    elif len(CCList) == 1:                       #means '->' was not existed
        LoS = CCList[0].strip()
        Dest = DicTable['Dest']['unconnected']

    #print('Dest:',Dest)
    

    LoSSplit = LoS.split('(').copy()
    #print(LoSSplit)
    if len(LoSSplit) == 1:
        tmpAlu = LoSSplit[0]
    elif len(LoSSplit) == 2:
        LoSSplitpow2 = LoSSplit[1].split(')').copy()
        tmpAlu = LoSSplitpow2[0]
        if LoSSplitpow2[1].find('>>') != -1:
            RSF = True
        if LoSSplitpow2[1].find('<<') != -1:
            LSF = True
        ########################################### it can be a advance shifter

    


    tmpAluSplitmin = tmpAlu.split('-').copy()
    tmpAluSplitadd = tmpAlu.split('+').copy()
    tmpAluSplitand = tmpAlu.split('&').copy()


    if tmpAlu.find('not')!= -1:                           # if not assign.
        tmpAluSplitnot = tmpAlu.split('not')
        for k in DicTable['SBUS']:
            if tmpAluSplitnot[1].strip() == k:                  #IN,R0...R7
                SBUS = DicTable['SBUS'][k]
                ALU = 0b0011                 #alu value is not sbus
    
    elif tmpAlu.find('>>')!= -1:                           # if right shift
        RSF = True

    elif tmpAlu.find('>>')!= -1:                           # if left shift
        LSF = True

    else:
        if(len(tmpAluSplitmin)==1 and len(tmpAluSplitadd)==1 and len(tmpAluSplitand)==1 ):    #if dont have operator
            for k in DicTable['SBUS']:
                if tmpAlu == k:                  #IN,R0...R7
                    SBUS = DicTable['SBUS'][k]
                    ALU = 0b0001                 #alu value is sbus
            if tmpAlu == 'ACC':                  #ACC
                #SBUS is dont care 
                ALU = 0b0000
        else:                                        #have operator
                        
            if len(tmpAluSplitmin) == 2:
                schr = '-' 
            if len(tmpAluSplitadd) == 2:
                schr = '+' 
            if len(tmpAluSplitand) == 2:
                schr = '&' 

            
            op1 = tmpAluSplitmin[0].strip()
            op2 = tmpAluSplitmin[1].strip()
            sop1 = op1
            sop2 = op2
            if op1!='ACC':
                for h in DicTable['SBUS']:
                    if h == op1:
                        SBUS = DicTable['SBUS'][h]
                sop1 = 'SBus'
            if op2!='ACC':
                for h in DicTable['SBUS']:
                    if h == op2:
                        SBUS = DicTable['SBUS'][h]
                sop2 = 'SBus'
            #print('WARRRRRRR:',sop1+schr+sop2)
            for k in DicTable['ALU']:          #search for find string in alu
                if k == (sop1+schr+sop2):
                    ALU = DicTable['ALU'][k]
            


    if LSF == False and RSF == False:            #for shifter
        Shifter = 0b111
    elif LSF == True: 
        Shifter = 0b000
    elif RSF == True:
        Shifter = 0b001











    #return CurrentCommand



def RunJMP(CurrentLine):
    global Nxt,DicTable,Address
    CurrentJump = CurrentLine['jmp']
    CJ = CurrentJump.strip()
    #CJS = CJ.split('JUMP').copy()
    #print(CJS[1].strip())
    if CJ.find('JUMP')!= -1:
        JumpLabel = CJ.split('JUMP')[1].strip()
        Nxt = 0b0001 
        if CJ.find('JUMP_IF_Z')!= -1:
            JumpLabel = CJ.split('JUMP_IF_Z')[1].strip()
            Nxt = 0b0100 
        elif CJ.find('JUMP_IF_C')!= -1:
            JumpLabel = CJ.split('JUMP_IF_C')[1].strip() 
            Nxt = 0b0010 
        elif CJ.find('JUMP_IF_NC')!= -1:
            JumpLabel = CJ.split('JUMP_IF_NC')[1].strip() 
            Nxt = 0b1010 
        elif CJ.find('JUMP_IF_NZ')!= -1:
            JumpLabel = CJ.split('JUMP_IF_NZ')[1].strip() 
            Nxt = 0b1100
    else:                                                #no jump
        Nxt = 0b0000
        JumpLabel = 'Nothing'     #suppose default value for label

    JumpAddress = 1616     #suppose default value for address
    for k in range (len(mild)):
        if mild[k]['label'] == JumpLabel:
            JumpAddress = mild[k]['address']
            break

    #print ('Jump address is :',JumpAddress, '\t\tJump label is :',JumpLabel) 

    Address = int(JumpAddress)



mild = seq_ins_parser(microins)
for i in range(len(mild)):
    RunCommand(mild[i])
    RunJMP(mild[i])
    print("____________________________________________________________________________________________________")
    print('Command Number',i,'---\t\t',microins[i])
    print('This Line saved in Dictionary: ',mild[i],'\n')
    print('The Command Successfully Encoded!','\n')
    print('SBUS: '+str(bin(SBUS)) +'\t\tALU: '+ str(bin(ALU)) +'\t\tShifter: ' + str(bin(Shifter)) +'\t\tDest: ' + str(bin(Dest)),'\t\tNxt: ' + str(bin(Nxt)),'\t\tAddress: ' + str(bin(Address)),'\n')
    MI = '0'
    SBUS_str = str(bin(SBUS))[2:]
    ALU_str = str(bin(ALU))[2:]
    Shifter_str = str(bin(Shifter))[2:]
    Dest_str = str(bin(Dest))[2:]
    Nxt_str = str(bin(Nxt))[2:]
    Address_str = str(bin(Address))[2:]
    ########## assign number of bits in each variable ##########
    while len(SBUS_str) != 4:
        SBUS_str = '0' + SBUS_str
    while len(ALU_str) != 4:
        ALU_str = '0' + ALU_str
    while len(Shifter_str) != 3:
        Shifter_str = '0' + Shifter_str
    while len(Dest_str) != 4:
        Dest_str = '0' + Dest_str
    while len(Nxt_str) != 4:
        Nxt_str = '0' + Nxt_str
    while len(Address_str) != 12:
        Address_str = '0' + Address_str
    
    MI = MI + SBUS_str + ALU_str + Shifter_str + Dest_str + Nxt_str + Address_str
    MISHOW = '0' + '  ' + SBUS_str + '  '+ ALU_str+ '  ' + Shifter_str + '  ' + Dest_str+ '  ' + Nxt_str + '  '+ Address_str
    
    Byte = []
    ##### byte be byte ba method .byte() buffer mikonim ####
    Byte.append(MI[0:8])
    Byte.append(MI[8:16])
    Byte.append(MI[16:24])
    Byte.append(MI[24:32])

    for r in range(len(Byte)):        ### for converting each of 4 bytes into int (because python cant work with binary file objects with string format)
        intnum = 0
        for p in range(len(Byte[r])):
            if(Byte[r][p]=='1'):
                intnum = intnum + pow(2,len(Byte[r])-1-p)
        intByte.append(intnum)
    
    MILIST.append(MI)    ## didn't used but it's good for debbuging :)

    print('Generated 32 bit Word is : ',MISHOW)



###################################### write binary file
buffer = bytes(intByte)
print("____________________________________________________________________________________________________")
print ('\nThat\'s Binary format saved in EndFile.txt : \t',buffer,'\n\nAll Done!')
print("____________________________________________________________________________________________________")

with open('./io/EndFile.txt','bw') as exportbinfile:
    exportbinfile.write(buffer)


### for read endfile
'''
with open('./io/EndFile.txt','br') as f:
    buf = f.read(256)

    for h in buf:
        print(bin(h))
'''



