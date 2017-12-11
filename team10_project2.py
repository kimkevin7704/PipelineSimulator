import sys
import getopt

"""
    KEVIN'S UPDATE NOTES
    
    I don't understand tags, lru shit at all... not sure how to grab instructions other than the straight binary string from the input file
    If you know how to pull the instruction, registers/address, tag, set and all that info from the binary instruction in memory, we need that to go forward
    
    LW and SW instructions can be defined with the rest of the instructions. (we have the code already but I don't know how to apply it when
    we fetch instructions from cache/memory)
    
    CODE FOR INSTRUCTIONS (mem-address will be based on pc? Regis will be from the REG class):
    def JUMP(jAddress):
        global mem_address
        mem_address = int(jAddress) - 4

    def JR(rs):
            global mem_address
            mem_address = R[int(rs)] - 4
    
    def BEQ(rs, rt, label):
            if Regis[int(rs)] == Regis[int(rt)]:
                    global mem_address
                    mem_address = mem_address + int(label)
    def BLTZ(rs, label):
            if int(Regis[int(rs)]) < 0:
                    global mem_address
                    mem_address = mem_address + int(label)
    
    def ADD(rd, rs, rt):
            Regis[int(rd)] = Regis[int(rs)] + Regis[int(rt)]
    def ADDI(rt, rs, imm):
            Regis[int(rt)] = Regis[int(rs)] + int(imm)
    def SUB(rd, rs, rt):
            Regis[int(rd)] = Regis[int(rs)] - Regis[int(rt)]
    def SW(rs, rt, bOffset):
            pMem[int(((int(bOffset) + int(Regis[int(rs)])) - 172)/4)] = int(Regis[int(rt)])
    def LW(rs, rt, bOffset):
            Regis[int(rt)] = pMem[int(((int(bOffset) + int(Regis[int(rs)])) - 172)/4)]
    def SLL(rd, rs, shamt):
            Regis[int(rd)] = int(str(Regis[int(rs)]), 10) << int(shamt)
    def SRL(rd, rs, shamt):
            Regis[int(rd)] = int(str(Regis[int(rs)]), 10) << int(shamt)      
    def MUL(rd, rs, rt):
            Regis[int(rd)] = Regis[int(rs)] * Regis[int(rt)]
    def AND(rd, rs, rt):
            Regis[int(rd)] = Regis[int(rs)] & Regis[int(rt)]
    def OR(rd, rs, rt):
            Regis[int(rd)] = Regis[int(rs)] | Regis[int(rt)]
    def MOVZ(rd, rs, rt):
            if Regis[int(rt)] == int(0):
                    Regis[int(rd)] = Regis[int(rs)]
    def NOP():
    
    
    THINGS ADDED:
        1. disassembler driver added (writes .txt disassembler output on run)
        2. will create 2 output files when run
        3. preissuebuffer, prealu, and premem classes added (initialized in controller)
        4. IF changed. Need a way to figure out if stalled (after pipeline finished)
            I think IF should contain all the instruction definition code. (will determine if its a NOP, Break, Jump, etc...)
        5. Started a driver for our pipeline output. Need to update as we go along
    
    THINGS WE NEED:
        1. fetching shit from cache
        2. way to define instructions from raw instruction and pass info to methods (need IF to differentiate instruction types)
    
    If instruction fetching from cache/memory works, I'll probably be able to code the rest of the pipeline ez.
    hard to write stuff for alu, mem, wb since we need to know the instruction type, registers, etc.
"""
# DISASSEMBLER METHODS

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


# CLASS DEFINITIONS FOR PIPELINE

class REG:
    def __init__(self):
        self.r = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def print_regs(self, output):
        output.write('Registers\nR00:')
        for x in range(0, 8):
            output.write('\t' + str(self.r[x]))
        output.write('\nR08:')
        for x in range(8, 16):
            output.write('\t' + str(self.r[x]))
        output.write('\nR16:')
        for x in range(16, 24):
            output.write('\t' + str(self.r[x]))
        output.write('\nR24:')
        for x in range(24, 32):
            output.write('\t' + str(self.r[x]))
        output.write('\n')

class CONTROL:
    def __init__(self, iput, oput):
        self.stalled = False
        self.break_found = False
        self.pc = 96
        self.cycle = 1
        self.output = oput
        self.miss = False

        #MACHINE COMPONENTS
        #things we need: pre-issue buffer
        self.cache = CACHE(iput)
        self.ifetch = IF()
        self.pib = PREISSUEBUFFER()
        self.issue = ISSUE()
        self.preALU = PREALU()
        self.preMEM = PREMEM()
        self.reg = REG()

    def print_state(self):  # function to output all states of current cycle
        self.output.write('--------------------\n')
        self.output.write('Cycle: ' + str(self.cycle) + '\n\n')
        # self.ifetch.print_prebuffer(self.oput)
        # stuff printed after fetch goes here
        self.reg.print_regs(self.output)
        # stuff printed after registers goes here

    def next_cycle(self):
        # stuff that happens before instr fetch goes here
        fetch_code = self.ifetch.fetch(self.cache, self.pc, self.pib)
        if fetch_code == -1:
            self.miss = True
        elif fetch_code == 0:
            self.break_found = True;
        # stuff that happens after instr fetch goes here
        self.print_state()
        if self.miss:
            self.cache.grab_mem(self.pc)    # at end of cycle, if we had cache miss, tell cache to grab the stuff
            self.miss = False
        else:
            self.pc += 4                    # if no cache miss, increment PC

class CACHE:
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
        self.LRU = [0, 0, 0, 0]
        self.instructions = []  # list containing all instruction items
        self.memory = []        # list containing all data memory items
        self.mem = iput
        self.hit = False
        # self.mem_to_grab = -1   # memory slot/s to be pulled on cache miss
        self.assocblock = 0     # 0 or 1, location of the block within a set when cache hit is detected
        self.set_mask = 0b11000
        self.break_line = 96
        self.num_instructions = 0
        self.split_mem(self.mem)  # split input into instruction and (data) memory lists

    def ping(self, pc):
        request_tag = pc >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        request_set = pc & self.set_mask
        request_set = request_tag >> 3
        if self.sets[request_set][0][2] == request_tag:       # check first block in matching set for hit
            self.assocblock = 0
            self.hit = True
        elif self.sets[request_set][1][2] == request_tag:     # check second block
            self.assocblock = 1
            self.hit = True
        if self.hit:
            if pc % 8 == 0:
                return self.sets[request_set][self.assocblock][3]       # if address is %8 then we want the first word in block
            else:
                return self.sets[request_set][self.assocblock][4]       # else we want second word in block
        else:
            self.hit = False
            # self.mem_to_grab = pc  # cache miss, update this var and it will be pulled at the very end of the cycle
            return -1

    def split_mem(self, mem): # populates our lists at initialization
        is_not_break = True
        for line in mem:
            if is_not_break:
                x = line
                self.instructions.append(x[0:32])
                if x == '10000000000000000000000000001101':
                    is_not_break = False
                else:
                    self.num_instructions += 1
                    self.break_line += 4  # finds the mem location for BREAK so we can determine which list to pull from

            else:
                x = line
                self.memory.append(x[0:32])

    def grab_mem(self, pc): # pull the requested address from instructions or memory based on break_line value
        block_to_grab = 0
        block_to_grab2 = (pc - 96)/4
        block_tag = pc >> 5
        block_set = pc & self.set_mask
        block_set = block_set >> 3
        if pc < self.break_line:
            block_to_grab = self.instructions[int(block_to_grab2)]
            block_to_grab2 = self.instructions[int(block_to_grab2) + 1]
        else:
            block_to_grab = self.memory[block_to_grab2 - self.num_instructions]
            block_to_grab2 = self.memory[block_to_grab2 - self.num_instructions + 1]

        if self.sets[block_set][self.LRU[block_set]][0] == 1:
            self.write_back(block_set, block_tag, self.sets[block_set][self.LRU[block_set]][3], self.sets[block_set][self.LRU[block_set]][4])
        self.sets[block_set][self.LRU[block_set]][0] = 1
        self.sets[block_set][self.LRU[block_set]][2] = block_tag
        self.sets[block_set][self.LRU[block_set]][3] = block_to_grab
        self.sets[block_set][self.LRU[block_set]][4] = block_to_grab2
        if self.LRU[block_set] == 1:
            self.LRU[block_set] = 0
        else:
            self.LRU[block_set] = 1

    def write_back(self, set, tag, word1, word2):
        mem_to_write_to = (set << 5) + (tag << 3)
        mem_to_write_to = (mem_to_write_to - 96)/4
        if mem_to_write_to < self.break_line:
            self.instructions[mem_to_write_to] = word1
            self.instructions[mem_to_write_to + 1] = word2
        else:
            self.memory[(mem_to_write_to - self.num_instructions)] = word1
            self.memory[(mem_to_write_to - self.num_instructions) + 1] = word2

class IF:
    def __init__(self):
        self.hitCheck = 0       # in case of cache miss, returns -1 to controller so that it doesnt increment pc
        self.isStall = False    # if fetch unit is stalled, no instruction fetch

    # returns number of instructions IF can fetch
    def canFetch(self, pib):
        # if stalled, return 0
        if self.isStall == True:
            return 0
        availableSlots = controller.pib.isFull()
        # return number of slots available in PIB
        if availableSlots == 0:
            return 0
        if availableSlots == 1:
            return 1
        else:
            return 2

    def fetch(self, cache, pc, pib):         # requests information at address: pc from cache
        """SOHAILS NOTES: I'm setting this function to return 4 possible values back to the controller:
            -1 if its a miss - controller tells cache to grab that mem block at end of cycle
            -2 if we have a BEQ/BLTZ and we need a stall - NOT IMPLEMENTED IDK WHAT TO DO FOR THIS, HOW DOES IT KNOW IF THE REGISTERS ARE READY OR NOT
            PC values if we have a jump/jr/branch and registers are ready - controller updates pc value at end of cycle - NOT IMPLEMENTED SEE ABOVE
            0 if we found BREAK

            note: nops and invalid instructions are just discarded I guess so the controller doesn't need to know bout that   """

        self.hitCheck = cache.ping(pc)
        if self.hitCheck < 0:     # make sure we hit
            return -1
        # IF HITCHECK != BRANCH, NOP, INVALID, OR BREAK...
        # controller.pib.addToBuffer(self.hitCheck)   # add instruction to PIB
        instr_check = self.instr_check(self.hitCheck)
        if instr_check[0] == -1: # case: BREAK found [0,0,0,0]
            return 0
        elif instr_check[0] == 0: # case: nop or invalid instr - discard instruction [-1,0,0,0]
            self.hitCheck = -1
        elif instr_check[0] == 1:   # case: jr instr [1,rs,0,0]
            print()
        elif instr_check[0] == 2:   # case: jump [2,jump_address]
            print()
        elif instr_check[0] == 3:  # case: bltz
            print()
        elif instr_check[0] == 4:  # case: beq
            print()
        elif instr_check[0] == 5:  # case: sll [5, rd, rt, shamt]
            print()

        if pib.isFull() > 0 and self.hitCheck > 0:  # if hit and we have space, get next word also
            self.hitCheck = cache.ping(pc + 4)
            pib.addToBuffer(self.hitCheck)

    def instr_check(self):
        return_field = [0, 0, 0, 0]
        if self.hitCheck[0] == 0: #invalid instr check
            return_field[0] = 0
            return return_field
        if self.hitCheck == '10000000000000000000000000001101':
            return_field[0] = -1
            return return_field
        opcode = self.hitCheck[1:6]
        opcode_parse = int(opcode, 2)
        instruction = self.hitCheck[26:]
        instruction_hex = int(instruction, 2)

        if opcode_parse == 0:
            if instruction_hex == 0:
                # if all 0 is NOP
                if self.hitCheck == '10000000000000000000000000000000':
                    return_field[0] = 0
                    return return_field
                else:
                    Rd = int(self.hitCheck[16:21], 2)
                    Rt = int(self[11:16], 2)
                    Shamt = int(self[21:26], 2)
                    return_field[0] = 5
                    return_field[1] = Rd
                    return_field[2] = Rt
                    return_field[3] = Shamt
                    return return_field
            elif instruction_hex == 8:
                # jr Rs
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 1
                return_field[1] = Rs
                return return_field

        elif opcode_parse == 2:
            jump_address = int(self.hitCheck[6:], 2) * 4
            return_field[0] = 2
            return_field[1] = jump_address
            return return_field
        else:
            if opcode_parse == 1:
                # bltz Rs, label
                Rs = int(self.hitCheck[6:11], 2)
                label = to_int_2c(self.hitCheck[16:])
                return_field[0] = 3
                return_field[1] = Rs
                return_field[2] = label
                return return_field
            elif opcode_parse == 4:
                # beq Rs, Rt, label
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                label = to_int_2c(self.hitCheck[16:])
                return_field[0] = 4
                return_field[1] = Rs
                return_field[2] = Rt
                return_field[3] = label
                return return_field
        return_field[0] = 5
        return return_field

    # BRANCH, BREAK, NOP, AND INVALID INSTRUCTIONS ARE ALL FETCHED. IF WILL HANDLE THEM.

class PREISSUEBUFFER:
    def __init__(self):
        self.buffer = [0, 0, 0, 0]

    # add instruction to PIB [0,0,0,0] --> [0,0,0,I1]
    def addToBuffer(self, instruction):
        self.buffer.pop(0)
        self.buffer.append(instruction)

    # remove instruction from PIB [0,0,I2,I1] --> [0,0,0,I2]
    def removeFromBuffer(self):
        # if first in line of PIB is occupied, POP and add 0 at end of line
        if self.buffer[3] != 0:
            self.buffer.pop(3)
            self.buffer.insert(0, "0")

    # check if preissue buffer is full, has 1 slot, or more than 1 available
    # RETURNS NUMBER OF SLOTS TO FILL FOR IF
    def isFull(self):
        slotsAvailable = 0
        for slot in self.buffer:
            if slot == 0:
                slotsAvailable += 1
        if slotsAvailable == 0:
            return 0
        if slotsAvailable == 1:
            return 1
        else:
            return 2

    def printPrebuffer(self, outfile):
        outfile.write('Pre-Issue Buffer:\n')
        for x in range(0, 3):
            outfile.write('Entry ' + x + ':')
            if self.buffer[x] != 0:
                outfile.write(':\t[' + inst_to_str(self.buffer[x]) + ']\n')

class ISSUE():
    #STILL NEEDS HAZARD CHECKS (SHOULD DO AFTER FINISHING PIPELINE)
    #IF INSTRUCTION IS LW OR SW, SEND TO PREMEM QUEUE. ALL OTHERS GO TO PREALU
    def send_next(self, controller): # no idea what I was going for here
        maxSendPerCC = 0        # once counter hits 2, stop sending
        for x in range(0, 3) and maxSendPerCC <= 2:
            if controller.pib[3-x] != 0:
                instructionToSend = controller.pib[3 - x]
                #CHECK IF LW OR SW
                controller.preMEM.addToBuffer(instructionToSend)
                maxSendPerCC += 1
                #ELSE
                controller.preALU.addToBuffer(instructionToSend)
                maxSendPerCC += 1

class PREALU:
    def __init__(self):
        self.buffer = [0,0]

    def isFull(self):
        slotsAvailable = 0
        for slot in self.buffer:
            if slot == 0:
                slotsAvailable += 1
        if slotsAvailable == 0:
            return 0
        if slotsAvailable == 1:
            return 1
        else:
            return 2

    # add instruction [0,0] --> [0,I1]
    def addToBuffer(self, instruction):
        self.buffer.pop(0)
        self.buffer.append(instruction)

    # remove instruction[I2,I1] --> [0,I2]
    def removeFromBuffer(self):
        # if first in line of PIB is occupied, POP and add 0 at end of line
        if self.buffer[1] != 0:
            self.buffer.pop(1)
            self.buffer.insert(0,"0")

class PREMEM:
    def __init__(self):
        self.buffer = [0,0]

    def isFull(self):
        slotsAvailable = 0
        for slot in self.buffer:
            if slot == 0:
                slotsAvailable += 1
        if slotsAvailable == 0:
            return 0
        if slotsAvailable == 1:
            return 1
        else:
            return 2

    # add instruction [0,0] --> [0,I1]
    def addToBuffer(self, instruction):
        self.buffer.pop(0)
        self.buffer.append(instruction)

    # remove instruction[I2,I1] --> [0,I2]
    def removeFromBuffer(self):
        # if first in line is occupied, POP and add 0 at end of line
        if self.buffer[1] != 0:
            self.buffer.pop(1)
            self.buffer.insert(0,"0")

# DRIVER

ifile = ''
ofile = ''

myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a

out_file_dis = open(ofile + "_dis.txt", "w")
out_file_pipeline = open(ofile + "_pipeline.txt", "w")

# read each line of file and put in list
with open(ifile, 'r') as infile:
    data = infile.read()

my_list = data.splitlines()
#write disassembler output to file
dis(out_file_dis, my_list)

#initialize pipeline
controller = CONTROL(my_list, out_file_pipeline)
controller.next_cycle()
controller.next_cycle()

#start Clock Cycle

#WHILE INSTRUCTION IS NOT BREAK...

#try to fetch instructions
#check: 1. stall 2. PIB room 3. instruction type
if controller.ifetch.isStall == False:
    if controller.pib.isFull() > 0:
        print()# if











# class MEM():

# class ALU():

# class WB:





