import sys
import getopt


# CLASS DEFINITIONS
class CACHE(object):
    def __init__(self, iput):
        """Sets is a 3D array -
            1st D is sets 0 - 3
            2nd D is which entry (2 total) in the set
            3rd D is the actual info in this format: [valid bit, dirty bit, tag, word1, word2]

            when looking for shit in the cache, the IF will request information at whatever location the pc is at in the
            form of: 110000 (for 96)

            The cache interprets the requested address by breaking it down into parts. The lowest 2 bits are not needed
            at all, since we are incrementing in terms of 4 (so they will always be 0) and the next lowest bit isn't
            needed either since we are double-word aligned for each entry. The next lowest 2 bits we use to determine
            which of the 4 sets we are putting to or getting from, and whatever top bits are left
            are our tag (should be 2 but that only gives us addressing to 127... so might be more ). The tag is used to
            verify that the item in cache is, in fact, the thing we are looking for, so whenever we put shit to cache we
            have to set the tag, and whenever we check cache for shit we have to compare the tag bits in our request to
            the tag bits in that set in our cache.

            LRU (not implemented yet) is set to 0 or 1 to notate which entry was NOT used last. So if we store shit in
            Entry 0, then our LRU will be 1, so the next time we have to write over something we write in Entry 1"""

        self.sets = [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]
        self.lru = [0, 0, 0, 0]
        self.instructions = []  # list containing all instruction items
        self.memory = []        # list containing all data memory items
        self.mem = iput
        self.request_tag = 0    # tag to compare when checking for cache hit
        self.hit = False
        self.mem_to_grab = -1   # memory slot/s to be pulled on cache miss
        self.assocblock = 0     # 0 or 1, location of the block within a set when cache hit is detected
        self.request_set = 0    # set to check for a cache hit
        self.tag_mask = 0b1100
        self.split_mem(self.mem)  # split input into instruction and (data) memory lists

    def ping(self, pc):
        self.request_set = pc >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        self.request_tag = pc & self.tag_mask
        self.request_tag = self.request_tag >> 3
        if self.sets[self.request_set][0][2] == self.request_tag:       # check first block in matching set for hit
            self.assocblock = 0
            self.hit = True
        elif self.sets[self.request_set][1][2] == self.request_tag:     # check second block
            self.assocblock = 1
            self.hit = True
        if self.hit:
            if pc % 8 == 0:
                return self.sets[self.request_set][0]       # if address is %8 then we want the first word in block
            else:
                return self.sets[self.request_set][1]       # else we want second word in block
        else:
            self.hit = False
            self.mem_to_grab = pc  # cache miss, update this var and it will be pulled at the very end of the cycle
            return -1

    def split_mem(self, mem): # populates our lists at initialization
        is_not_break = True
        for line in mem:
            if is_not_break:
                x = line
                self.instructions.append(x[0:32])
                # if line is a break sequence, switch boolean to stop while loop
                if x == '10000000000000000000000000001101':
                    is_not_break = False
            else:
                x = line
                self.memory.append(x[0:32])

    def grab_mem(self, pc): # at end of cycle if cache miss, pull the requested address from instructions or memory
        print()             # THIS SEEMS INCORRECT, HOW DOES IT KNOW WHICH LIST TO GRAB FROM

    def lw(self, address):
        print()
        # algorithm for hit or miss
        # if hit return data
        # if miss, read self.instructions at (pc-96)/4 and pull that data, put it somewhere

    def sw(self, address):
        print()
        # algorithm for hit or miss
        # if hit, do something?
        # if miss, do something else?


class CONTROL(object):
    def __init__(self, iput, oput):
        self.stalled = False
        self.break_found = False
        self.pc = 96
        self.cycle = 1
        self.output = oput
        self.miss = False

        """MACHINE COMPONENTS"""
        self.cache = CACHE(iput)
        self.ifetch = IF()
        self.issue = ISSUE()
        self.reg = REG()

    def print_state(self):  # function to output all states of current cycle
        self.output.write('--------------------\n')
        self.output.write('Cycle: ' + self.cycle + '\n\n')
        self.ifetch.print_prebuffer(self.oput)
        # stuff printed after fetch goes here
        self.reg.print_regs(self.output)
        # stuff printed after registers goes here

    def next_cycle(self):
        # stuff that happens before instr fetch goes here
        self.ifetch.fetch(self.cache, self.pc)
        # stuff that happens after instr fetch goes here
        self.print_state()
        if self.miss:
            self.cache.grab_mem(self.pc)    # at end of cycle, if we had cache miss, tell cache to grab the stuff
            self.miss = False
        else:
            self.pc += 4                    # if no cache miss, increment PC


class IF:
    def __init__(self):
        self.pre_issue = [0, 0, 0, 0]
        self.prebuff_buffer = 0         # in case of cache miss, returns -1 to controller so that it doesnt increment pc

    def find_next_empty_entry(self):
        for x in range(0, 4):
            if self.pre_issue[x] == 0:
                return x
        return 4

    def fetch(self, cache, pc):         # requests information at address: pc from cache
        self.prebuff_buffer = cache.ping(pc)
        if self.prebuff_buffer < 0:     # make sure we hit
            return -1
        self.pre_issue[self.find_next_empty_entry()] = self.prebuff_buffer
        if self.find_next_empty_entry() < 3 and self.prebuff_buffer > 0: # if hit and we have space, get next word also
            self.prebuff_buffer = cache.ping(pc + 4)
            self.pre_issue[self.find_next_empty_entry()] = self.prebuff_buffer
        """Should we be checking here for J or BLTZ instructions?
            also, does cache identify the break?"""

    def print_prebuffer(self, outfile):
        outfile.write('Pre-Issue Buffer:\n')
        for x in range(0, 4):
            outfile.write('Entry ' + x + ':')
            if self.pre_issue[x] != 0:
                outfile.write(':\t[' + inst_to_str(self.pre_issue[x]) + ']\n')


class ISSUE():

    def send_next(self, pre_issue, alu, mem): # no idea what I was going for here
        temp = pre_issue[0]
        for x in range(0, 3):
            pre_issue[3-x] = pre_issue[2-x]
        return temp
    """I'm fairly certain I've confused the functions of the IF and ISSUE components so imma leave this be for now"""


# class MEM():

# class ALU():

# class WB:


class REG:
    def __init__(self):
        self.r = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def print_regs(self, output):
        output.write('Registers\nR00:')
        for x in range(0, 8):
            output.write('\t' + self.r[x])
        output.write('R08:')
        for x in range(8, 16):
            output.write('\t' + self.r[x])
        output.write('R16:')
        for x in range(16, 24):
            output.write('\t' + self.r[x])
        output.write('R24:')
        for x in range(24, 32):
            output.write('\t' + self.r[x])
        output.write('\n')


def to_int_2c(bin):
    conversion = int(bin, 2)
    if bin[0] == '1':
        conversion -= 2 ** len(bin)
    return conversion


def inst_to_str(x):
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


ifile = ''
ofile = ''


myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a


out_file = open(ofile + "_dis.txt", "w")

# read each line of file and put in list
with open(ifile, 'r') as infile:
    data = infile.read()
my_list = data.splitlines()

myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a

with open(ifile, 'r') as infile:
    data = infile.read()
# my_list = data.splitlines()

controller = CONTROL(my_list, ofile)
