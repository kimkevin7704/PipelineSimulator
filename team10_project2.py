import sys
import getopt

# CLASS DEFINITIONS

class CONTROL:
    def __init__(self, output):
        self.stalled = False
        self.break_found = False
        self.PC = 96
        self.output = output


class IF():
    def __init__(self):
        self.preIssue = [0, 0, 0, 0]

    def sendNext(self):
        temp = self.preIssue[0]
        for x in range(0, 3):
            self.preIssue[3-x] = self.preIssue[2-x]
        return temp

    def findNextEmptyEntry(self):
        for x in range(0, 3):
            if self.preIssue[x] == 0:
                return x
        return 4

    def fetch(self, cache, pc):
        self.preIssue[self.findNextEmptyEntry] = cache.ping(pc)
        if self.findNextEmptyEntry < 3:
            self.preIssue[self.findNextEmptyEntry] = cache.ping(pc)
        # Should we be checking here for J or BLTZ instructions?
        # also,




# class ISSUE():

# class MEM():

# class ALU():

# class WB:


class Reg():
    def __init__(self):
        self.r = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


ifile = ''
ofile = ''


myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a


# outfile = open(ofile + "_sim.txt", 'w')


# read each line of file and put in list
# with open(ifile, 'r') as infile:
#    data = infile.read()
# my_list = data.splitlines()

def to_int_2c(bin):
    conversion = int(bin, 2)
    if bin[0] == '1':
        conversion -= 2 ** len(bin)
    return conversion


out_file = open(ofile + "_dis.txt", "w")


# read each line of file and put in list
with open(ifile, 'r') as infile:
    data = infile.read()
my_list = data.splitlines()


def inst_to_string(x):
    def R():
        instruction = x[26:]
        instruction_hex = int(instruction, 2)
        if instruction_hex == 0:
            # if all 0 is NOP
            if x == '10000000000000000000000000000000':
                return 'NOP'
            else:
                # sll Rd, Rt, Shamt
                Rd = str(int(x[16:21], 2))
                Rt = str(int(x[11:16], 2))
                Shamt = str(int(x[21:26], 2))
                return 'SLL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt
        elif instruction_hex == 34:
            # sub Rd, Rs, Rt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            return 'SUB' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt
        elif instruction_hex == 32:
            # add Rd, Rs, Rt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            return 'ADD' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt
        elif instruction_hex == 8:
            # jr Rs
            Rs = str(int(x[6:11], 2))
            return 'JR' + '\t' + 'R' + Rs
        elif instruction_hex == 2:
            # srl Rd, Rt, shamt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Shamt = str(int(x[21:26], 2))
            return 'SRL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt
        elif instruction_hex == 36:
            # and Rd, Rs, Rt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            return 'AND' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n'
        elif instruction_hex == 37:
            # or Rd, Rs, Rt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            return 'OR' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt
        elif instruction_hex == 10:
            # movz Rd, Rs, Rt
            Rd = str(int(x[16:21], 2))
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            return 'MOVZ' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt

    def I():
        instruction = x[1:6]
        instruction_hex = int(instruction, 2)
        if instruction_hex == 8:
            # addi Rt, Rs, Imm
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            Imm = str(to_int_2c(x[16:]))
            return 'ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm
        elif instruction_hex == 11:
            # sw Rt, BOffset(Rs)
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            BOffset = str(to_int_2c(x[16:]))
            return 'SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'
        elif instruction_hex == 3:
            # lw Rt, Boffset(Rs)
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            BOffset = str(to_int_2c(x[16:]))
            return 'LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'
        elif instruction_hex == 1:
            # bltz Rs, label
            Rs = str(int(x[6:11], 2))
            label = str(to_int_2c(x[16:]))
            return 'BLTZ' + '\t' + 'R' + Rs + ', #' + label
        elif instruction_hex == 4:
            # beq Rs, Rt, label
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            label = str(to_int_2c(x[16:]))
            return 'BEQ' + '\t' + 'R' + Rs + ', R' + Rt + ', #' + label
        elif instruction_hex == 28:
            # mul Rd, Rs, Rt
            Rs = str(int(x[6:11], 2))
            Rt = str(int(x[11:16], 2))
            Rd = str(int(x[16:21], 2))
            return 'MUL' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt

    def J():
        # j label
        jump_address = str(int(x[6:], 2) * 4)
        return 'J' + '\t' + '#' + jump_address

    opcode = x[1:6]
    opcode_parse = int(opcode, 2)

    if opcode_parse == 0:
        R()
    elif opcode_parse == 2:
        J()
    else:
        I()

def dis(output_file, my_list):
    mem_address = 96
    is_not_break = True
    for line in my_list:
        if is_not_break:
            x = line
            # if line is a break sequence, switch boolean to stop while loop
            if x == '10000000000000000000000000001101':
                is_not_break = False
                mem_address_str = str(mem_address)
                mem_address += 4
                output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BREAK' + '\n')
            else:
                valid_bit = x[0]
                # if valid bit is 0, invalid instruction, add 4 to memory address
                if valid_bit == '0':
                    mem_address_str = str(mem_address)
                    mem_address += 4
                    output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'Invalid Instruction' + '\n')
                # else if valid bit is 1,
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
                            # if all 0 is NOP
                            if x == '10000000000000000000000000000000':
                                output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'NOP' + '\n')
                            else:
                                # sll Rd, Rt, Shamt
                                Rd = str(int(x[16:21], 2))
                                Rt = str(int(x[11:16], 2))
                                Shamt = str(int(x[21:26], 2))
                                output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SLL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt + '\n')
                        elif instruction_hex == 34:
                            # sub Rd, Rs, Rt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SUB' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                        elif instruction_hex == 32:
                            # add Rd, Rs, Rt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'ADD' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                        elif instruction_hex == 8:
                            # jr Rs
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'JR' + '\t' + 'R' + Rs + '\n')
                        elif instruction_hex == 2:
                            # srl Rd, Rt, shamt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Shamt = str(int(x[21:26], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SRL' + '\t' + 'R' + Rd + ', R' + Rt + ', #' + Shamt + '\n')
                        elif instruction_hex == 36:
                            # and Rd, Rs, Rt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'AND' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                        elif instruction_hex == 37:
                            # or Rd, Rs, Rt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'OR' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')
                        elif instruction_hex == 10:
                            # movz Rd, Rs, Rt
                            Rd = str(int(x[16:21], 2))
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'MOVZ' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')

                    def I():
                        instruction = x[1:6]
                        instruction_hex = int(instruction, 2)
                        if instruction_hex == 8:
                            # addi Rt, Rs, Imm
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            Imm = str(to_int_2c(x[16:]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm + '\n')
                        elif instruction_hex == 11:
                            # sw Rt, BOffset(Rs)
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            BOffset = str(to_int_2c(x[16:]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                        elif instruction_hex == 3:
                            # lw Rt, Boffset(Rs)
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            BOffset = str(to_int_2c(x[16:]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                        elif instruction_hex == 1:
                            # bltz Rs, label
                            Rs = str(int(x[6:11], 2))
                            label = str(to_int_2c(x[16:]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BLTZ' + '\t' + 'R' + Rs + ', #' + label + '\n')
                        elif instruction_hex == 4:
                            # beq Rs, Rt, label
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            label = str(to_int_2c(x[16:]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BEQ' + '\t' + 'R' + Rs + ', R' + Rt + ', #' + label + '\n')
                        elif instruction_hex == 28:
                            # mul Rd, Rs, Rt
                            Rs = str(int(x[6:11], 2))
                            Rt = str(int(x[11:16], 2))
                            Rd = str(int(x[16:21], 2))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'MUL' + '\t' + 'R' + Rd + ', R' + Rs + ', R' + Rt + '\n')

                    def J():
                        # j label
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
            output_file.write(x + '\t' + mem_address_str + '\t' + converted_binary + '\n')