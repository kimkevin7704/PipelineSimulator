import sys, getopt


cycle = 0
instr = []
#first memory address is at 96

mem_address = 96
Regis = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pMem = []
dataStartLoc = 0

def to_int_2c(bin):
        conversion = int(bin, 2)
        if bin[0] == '1':
                conversion -= 2**len(bin)
        return conversion

               
def printState():
        outfile.write("====================\n")
        outfile.write("cycle:" + str(cycle) + '\t' + str(mem_address) + '\t' + instr[0] + '\n')
        outfile.write('\n')
        outfile.write("registers:\n")
        outfile.write("r00:\t" + str(Regis[0]) + '\t' + str(Regis[1]) + '\t' + str(Regis[2]) + '\t' + str(Regis[3]) + '\t' + str(Regis[4]) + '\t' + str(Regis[5]) + '\t' + str(Regis[6]) + '\t' + str(Regis[7]) + '\n') 
        outfile.write("r08:\t" + str(Regis[8]) + '\t' + str(Regis[9]) + '\t' + str(Regis[10]) + '\t' + str(Regis[11]) + '\t' + str(Regis[12]) + '\t' + str(Regis[13]) + '\t' + str(Regis[14]) + '\t' + str(Regis[15]) + '\n')
        outfile.write("r16:\t" + str(Regis[16]) + '\t' + str(Regis[17]) + '\t' + str(Regis[18]) + '\t' + str(Regis[19]) + '\t' + str(Regis[20]) + '\t' + str(Regis[21]) + '\t' + str(Regis[22]) + '\t' + str(Regis[23]) + '\n')
        outfile.write("r24:\t" + str(Regis[24]) + '\t' + str(Regis[25]) + '\t' + str(Regis[26]) + '\t' + str(Regis[27]) + '\t' + str(Regis[28]) + '\t' + str(Regis[29]) + '\t' + str(Regis[30]) + '\t' + str(Regis[31]) + '\n')
        outfile.write('\n')
        outfile.write("data:\n")

        outputCount = 0
        headCount = 0
        for data in pMem:
                if headCount == 0:
                        outfile.write(str((outputCount * 4) + dataStartLoc) + ":\t")
                
                outfile.write(str(data))
                outputCount += 1
                headCount += 1
                if headCount == 8:
                        outfile.write('\n')
                        headCount = 0
                else:
                        outfile.write('\t')

        outfile.write("\n")
        instr.pop()

def JUMP(jAddress):
        printState()
        global mem_address
        mem_address = int(jAddress) - 4

def JR(rs):
        printState()
        global mem_address
        mem_address = R[int(rs)] - 4

def BEQ(rs, rt, label):
        printState()
        if Regis[int(rs)] == Regis[int(rt)]:
                global mem_address
                mem_address = int(mem_address + (int(label)))

def BLTZ(rs, label):
        printState()
        if int(Regis[int(rs)]) < 0:
                global mem_address
                mem_address = int(mem_address + (int(label)))

def ADD(rd, rs, rt):
        Regis[int(rd)] = Regis[int(rs)] + Regis[int(rt)]
        printState()
def ADDI(rt, rs, imm):
        Regis[int(rt)] = Regis[int(rs)] + int(imm)
        printState()
def SUB(rd, rs, rt):
        Regis[int(rd)] = Regis[int(rs)] - Regis[int(rt)]
        printState()                
def SW(rs, rt, bOffset):
        pMem[int(((int(bOffset) + int(Regis[int(rs)])) - 172)/4)] = int(Regis[int(rt)])
        printState()
def LW(rs, rt, bOffset):
        Regis[int(rt)] = pMem[int(((int(bOffset) + int(Regis[int(rs)])) - 172)/4)]
        printState()
def SLL(rd, rs, shamt):
        Regis[int(rd)] = int(str(Regis[int(rs)]), 10) << int(shamt)
        printState()
def SRL(rd, rs, shamt):
        Regis[int(rd)] = int(str(Regis[int(rs)]), 10) >> int(shamt)
        printState()                
def MUL(rd, rs, rt):
        Regis[int(rd)] = Regis[int(rs)] * Regis[int(rt)]
        printState()                
def AND(rd, rs, rt):
        Regis[int(rd)] = Regis[int(rs)] & Regis[int(rt)]
        printState()
def OR(rd, rs, rt):
        Regis[int(rd)] = Regis[int(rs)] | Regis[int(rt)]
        printState()
def MOVZ(rd, rs, rt):
        if Regis[int(rt)] == int(0):
                Regis[int(rd)] = Regis[int(rs)]
        printState()
def NOP():
        printState()
                        
                                
              

ifile = ''
ofile = ''


myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a


outfile = open(ofile + "_sim.txt", 'w')


#read each line of file and put in list
with open(ifile, 'r') as infile:
    data = infile.read()
my_list = data.splitlines()

output_file = open(ofile + "_dis.txt", "w")

#take each list element and disassemble

#get size of list
list_size = len(my_list)
#make boolean to stop disassembly after break
is_not_break = True
breakPoint = 1
for line in my_list:
        x = line
        if is_not_break:                
                #if line is a break sequence, switch boolean to start reading in program data
                if x == '10000000000000000000000000001101':
                        is_not_break = False
                        dataStartLoc = 96 + (4 * breakPoint)
                else:
                    breakPoint += 1
        else:
                pMem.append(to_int_2c(x))
#reset bool
is_not_break = True
                
                
#for each list element...
while is_not_break:
        x = my_list[int((mem_address - 96)/4)]
        #if line is a break sequence, switch boolean to stop while loop
        if x == '10000000000000000000000000001101':
                is_not_break = False
                mem_address_str = str(mem_address)
                
                cycle += 1
                #mem_address += 4
                instr.append(str('BREAK'))
                printState()
        else:
                valid_bit = x[0]
                #if valid bit is 0, invalid instruction, add 4 to memory address
                if valid_bit == '0':
                    mem_address_str = str(mem_address)
                    
                #else if valid bit is 1, 
                elif valid_bit == '1':
                        cycle += 1
                        mem_address_str = str(mem_address)
                        #sM.mem_address += 4
                        opcode = x[1:6]
                        opcode_parse = int(opcode, 2)

                        def R(instr):
                                instruction = x[26:]
                                instruction_hex = int(instruction, 2)
                                if instruction_hex == 0:
                                        #if all 0 is NOP
                                        if x == '10000000000000000000000000000000':
                                                instr.append(str('NOP'))
                                                NOP()       
                                        else:   
                                                #sll Rd, Rt, Shamt
                                                Rd = str(int(x[16:21], 2))
                                                Rt = str(int(x[11:16], 2))
                                                Shamt = str(int(x[21:26], 2))                                                
       
                                                instr.append(str('SLL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt))
                                                SLL(Rd, Rt, Shamt)

                                elif instruction_hex == 34:
                                        #sub Rd, Rs, Rt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                         
                                        instr.append(str('SUB' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        SUB(Rd, Rs, Rt)

                                elif instruction_hex == 32:
                                        #add Rd, Rs, Rt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                             
                                        instr.append(str('ADD' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        ADD(Rd, Rs, Rt)
                                elif instruction_hex == 8:
                                        #jr Rs
                                        Rs = str(int(x[6:11], 2))
                                             
                                        instr.append(str('JR' + '\t' + 'R' + Rs))
                                        JR(Rs, mem_address)
                                elif instruction_hex == 2:
                                        #srl Rd, Rt, shamt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Shamt = str(int(x[21:26], 2))
                                             
                                        instr.append(str('SRL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt))
                                        SRL(Rd, Rt, Shamt)
                                elif instruction_hex == 36:
                                        #and Rd, Rs, Rt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                             
                                        instr.append(str('AND' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        AND(Rd, Rs, Rt)
                                elif instruction_hex == 37:
                                        #or Rd, Rs, Rt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                             
                                        instr.append(str('OR' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        OR(Rd, Rs, Rt)
                                elif instruction_hex == 10:
                                        #movz Rd, Rs, Rt
                                        Rd = str(int(x[16:21], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                             
                                        instr.append(str('MOVZ' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        MOVZ(Rd, Rs, Rt)
                        def I(instr):
                                instruction = x[1:6]
                                instruction_hex = int(instruction, 2)
                                if instruction_hex == 8:
                                        #addi Rt, Rs, Imm
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                        Imm = str(to_int_2c(x[16:]))
                                        
                                        instr.append(str('ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm))
                                        ADDI(int(Rt), int(Rs), int(Imm))
                                elif instruction_hex == 11:
                                        #sw Rt, BOffset(Rs)
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                        BOffset = str(to_int_2c(x[16:]))                           
                                             
                                        instr.append(str('SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'))
                                        SW(Rs, Rt, BOffset)                                        
                                elif instruction_hex == 3:
                                        #lw Rt, Boffset(Rs)
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                        BOffset = str(to_int_2c(x[16:]))
                                             
                                        instr.append(str('LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'))
                                        LW(Rs, Rt, BOffset)

                                elif instruction_hex == 1:
                                        #bltz Rs, label
                                        Rs = str(int(x[6:11], 2))
                                        label = str(to_int_2c(x[16:]))
                                             
                                        instr.append(str('BLTZ' + '\t' + 'R' + Rs + ', #' + label))
                                        BLTZ(Rs, label)
                                elif instruction_hex == 4:
                                        #beq Rs, Rt, label
                                        Rt = str(int(x[11:16], 2))
                                        Rs = str(int(x[6:11], 2))
                                        label = str(to_int_2c(x[16:]))
                                             
                                        instr.append(str('BEQ' + '\t' + 'R' + Rs + ', R' + Rt + ', #' + label))
                                        BEQ(Rs, Rt, label)
                                elif instruction_hex == 28:
                                        #mul Rd, Rs, Rt
                                        Rs = str(int(x[6:11], 2))
                                        Rt = str(int(x[11:16], 2))
                                        Rd = str(int(x[16:21], 2))
                                             
                                        instr.append(str('MUL' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt))
                                        MUL(Rd, Rs, Rt)
                        def J(instr):
                                #j label
                                jump_address = str(int(x[6:], 2) * 4)
                                     
                                instr.append(str('J' + '\t' + '#' + jump_address))
                                JUMP(jump_address)
                        if opcode_parse == 0:
                                R(instr)
                        elif opcode_parse == 2:
                                J(instr)
                        else:
                                I(instr)
                mem_address += 4


else:
        x = line
        mem_address_str = str(mem_address)
        mem_address += 4
        converted_binary = str(to_int_2c(x[1:]))
        cycle += 1

mem_address = 96
is_not_break = True

for line in my_list:
    if is_not_break:
        x = line
        #if line is a break sequence, switch boolean to stop while loop
        if x == '10000000000000000000000000001101':
            is_not_break = False
            mem_address_str = str(mem_address)
            mem_address += 4
            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BREAK' + '\n')
        else:
            valid_bit = x[0]
            #if valid bit is 0, invalid instruction, add 4 to memory address
            if valid_bit == '0':
                mem_address_str = str(mem_address)
                mem_address += 4
                output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'Invalid Instruction' + '\n')
            #else if valid bit is 1, 
            elif valid_bit == '1':
                mem_address_str = str(mem_address)
                mem_address += 4
                opcode = x[1:6]
                opcode_parse = int(opcode, 2)
                def to_int_2c(bin):
                    conversion = int(bin, 2)
                    if bin[0] == '1':
                        conversion -= 2**len(bin)
                    return conversion
                def R():
                    instruction = x[26:]
                    instruction_hex = int(instruction, 2)
                    if instruction_hex == 0:
                        #if all 0 is NOP
                        if x == '10000000000000000000000000000000':
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'NOP' + '\n')
                        else:   
                            #sll Rd, Rt, Shamt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Shamt = str(int(x[21:26], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SLL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt + '\n')
                    elif instruction_hex == 34:
                        #sub Rd, Rs, Rt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SUB' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                    elif instruction_hex == 32:
                        #add Rd, Rs, Rt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'ADD' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                    elif instruction_hex == 8:
                        #jr Rs
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'JR' + '\t' + 'R' + Rs + '\n')
                    elif instruction_hex == 2:
                        #srl Rd, Rt, shamt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Shamt = str(int(x[21:26], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SRL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt + '\n')
                    elif instruction_hex == 36:
                        #and Rd, Rs, Rt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'AND' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                    elif instruction_hex == 37:
                        #or Rd, Rs, Rt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'OR' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                    elif instruction_hex == 10:
                        #movz Rd, Rs, Rt
                        Rd = str(int(x[16:21], 2))
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'MOVZ' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                def I():
                    instruction = x[1:6]
                    instruction_hex = int(instruction, 2)
                    if instruction_hex == 8:
                        #addi Rt, Rs, Imm
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        Imm = str(to_int_2c(x[16:]))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm + '\n')
                    elif instruction_hex == 11:
                        #sw Rt, BOffset(Rs)
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        BOffset = str(to_int_2c(x[16:]))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                    elif instruction_hex == 3:
                        #lw Rt, Boffset(Rs)
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        BOffset = str(to_int_2c(x[16:]))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                    elif instruction_hex == 1:
                        #bltz Rs, label
                        Rs = str(int(x[6:11], 2))
                        label = str(to_int_2c(x[16:]))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BLTZ' + '\t' + 'R' + Rs + ', #' + label + '\n')
                    elif instruction_hex == 4:
                        #beq Rs, Rt, label
                        Rt = str(int(x[11:16], 2))
                        Rs = str(int(x[6:11], 2))
                        label = str(to_int_2c(x[16:]))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BEQ' + '\t' + 'R' + Rs + ', R' + Rt + ', #' + label + '\n')
                    elif instruction_hex == 28:
                        #mul Rd, Rs, Rt
                        Rs = str(int(x[6:11], 2))
                        Rt = str(int(x[11:16], 2))
                        Rd = str(int(x[16:21], 2))
                        output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'MUL' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                def J():
                    #j label
                    jump_address = str(int(x[6:], 2) * 4)
                    output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'J' + '\t' + '#' + jump_address + '\n')
                if opcode_parse == 0:
                    R()
                elif opcode_parse == 2:
                    J()
                else:
                    I()
    else:
        x = line
        mem_address_str = str(mem_address)
        mem_address += 4
        converted_binary = str(to_int_2c(x[1:]))
        output_file.write (x + '\t' + mem_address_str + '\t' + converted_binary + '\n')
