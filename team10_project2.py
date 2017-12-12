import sys
import getopt

"""
    KEVIN'S UPDATE NOTES
    
    IF now sends instructions to preissue buffer with relevant info
    preissue buffer sends to issue
    issue sorts and sends to preALU or preMEM
    ALU takes from preALU and does calculation
    
    as of now, ALU is changing the registers in our register array. this should happen
    in the WB component. can fix later
    
    premem gonna be hard cuz it involves a lot of cache hit shit that i dont get
    
    hazard checks aren't in... will prbly add after all components coded
    
    pc changes for branch instructions added
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

        #MACHINE COMPONENTS
        #things we need: pre-issue buffer
        self.cache = CACHE(iput)
        self.ifetch = IF()
        self.pib = PREISSUEBUFFER()
        self.issue = ISSUE()
        self.preALU = PREALU()
        self.preMEM = PREMEM()
        self.reg = REG()
        self.alu = ALU()
        self.postalu = POSTALU(self.alu)
        self.mem = MEM(self.preMEM, self.cache)
        self.postmem = POSTMEM(self.mem)
        self.wb = WB(self.reg, self.postmem, self.postalu)

    def print_state(self):  # function to output all states of current cycle
        self.output.write('--------------------\n')
        self.output.write('Cycle: ' + str(self.cycle) + '\n\n')
        # self.ifetch.print_prebuffer(self.oput)
        # stuff printed after fetch goes here
        self.reg.print_regs(self.output)
        # stuff printed after registers goes here

    def next_cycle(self):
        mem_miss = False
        fetch_miss = False
        # stuff that happens before instr fetch goes here
        self.wb.grab_and_write()
        mem_code = self.mem.instr_grab(self.reg, self.postmem)
        if mem_code > 0:  # function above returns the target address if there's a cache miss from MEM unit
            mem_miss = True
            self.stalled = True
        else:             # with this algorithm, a LW will only stall for one fetch, so not sure if this is correct
            self.stalled = False
        self.alu.execInstr(self.preALU, self.postalu, self.reg)
        self.issue.send_next(self)


        if not self.stalled:
            fetch_code = self.ifetch.fetch(self.cache, self.pc, self.pib)
            if fetch_code == -1:
                fetch_miss = True
            elif fetch_code == 0:
                self.break_found = True
        # stuff that happens after instr fetch goes here
        """THIS IS NOT CORRECT, WE'RE SUPPOSED TO BE CALLING SHIT IN REVERSE ORDER OF THE PIPELINE"""


        self.print_state()
        if mem_miss:
            self.cache.grab_mem(mem_code)
        if fetch_miss:
            self.cache.grab_mem(self.pc)    # at end of cycle, if we had cache miss, tell cache to grab the stuff
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

    def sw(self, target, value):
        request_tag = target >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        request_set = target & self.set_mask
        request_set = request_tag >> 3
        target_entry = 4
        if target % 8 == 0:
            target_entry = 4  # if address is %8 then we want the first word in block
        self.sets[request_set][self.assocblock][2] = 1
        self.sets[request_set][self.assocblock][target_entry] = int(value, 2)  # else we want second word in block

    def lw(self, target):
        request_tag = target >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        request_set = target & self.set_mask
        request_set = request_tag >> 3
        target_entry = 4
        if target % 8 == 0:
            target_entry = 4  # if address is %8 then we want the first word in block
        return int(self.sets[request_set][self.assocblock][target_entry])  # else we want second word in block

    def split_mem(self, mem):  # populates our lists at initialization
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

    def grab_mem(self, pc):  # pull the requested address from instructions or memory based on break_line value
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
        instr_check = self.instr_check()
        if instr_check[0] == -1: # case: BREAK found [-1,0,0,0]
            return 0
        elif instr_check[0] == 0: # case: nop or invalid instr - discard instruction [0,0,0,0]
            self.hitCheck = -1
        elif instr_check[0] == 1:   # case: jr instr [1,rs,0,0]
            pc = self.reg.r[instr_check[1]] - 4 # need to check if register is ready
        elif instr_check[0] == 2:   # case: jump [2,jump_address,0,0]
            pc = int(instr_check[1]) - 4
        elif instr_check[0] == 3:  # case: bltz [3,rs,label,0]
            if(self.reg.r[instr_check[1]] < 0):
                pc = pc + int(instr_check[2])
        elif instr_check[0] == 4:  # case: beq [4,rs,rt,label]
            if(self.reg.r[instr_check[1]] == self.reg.r[instr_check[2]]):
                pc = pc + int(instr_check[3])
        elif instr_check[0] == 5:  # case: sll [5, rd, rt, shamt]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 6:  # case: sub [6, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 7:  # case: add [7, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 8:  # case: srl [8, rd, rt, shamt]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 9:  # case: and [9, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 10:  # case: or [10, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 11:  # case: movz [11, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 12:  # case: mul [12, rd, rt, rs]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 13:  # case: addi [13, rt, rs, imm]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 14:  # case: sw [14, rt, rs, BOffset]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 15:  # case: lw [15, rt, rs, BOffset]
            pib.addToBuffer(instr_check)

        if pib.isFull() > 0 and self.hitCheck > 0:  # if hit and we have space, get next word also
            self.hitCheck = cache.ping(pc + 4)
            if self.hitCheck < 0:  # make sure we hit
                return -1
            # IF HITCHECK != BRANCH, NOP, INVALID, OR BREAK...
            # controller.pib.addToBuffer(self.hitCheck)   # add instruction to PIB
            instr_check = self.instr_check()
            if instr_check[0] == -1:  # case: BREAK found [-1,0,0,0]
                return 0
            elif instr_check[0] == 0:  # case: nop or invalid instr - discard instruction [0,0,0,0]
                self.hitCheck = -1
            elif instr_check[0] == 1:  # case: jr instr [1,rs,0,0]
                pc = self.reg.r[instr_check[1]] - 4  # need to check if register is ready
            elif instr_check[0] == 2:  # case: jump [2,jump_address,0,0]
                pc = int(instr_check[1]) - 4
            elif instr_check[0] == 3:  # case: bltz [3,rs,label,0]
                if (self.reg.r[instr_check[1]] < 0):
                    pc = pc + int(instr_check[2])
            elif instr_check[0] == 4:  # case: beq [4,rs,rt,label]
                if (self.reg.r[instr_check[1]] == self.reg.r[instr_check[2]]):
                    pc = pc + int(instr_check[3])
            elif instr_check[0] == 5:  # case: sll [5, rd, rt, shamt]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 6:  # case: sub [6, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 7:  # case: add [7, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 8:  # case: srl [8, rd, rt, shamt]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 9:  # case: and [9, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 10:  # case: or [10, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 11:  # case: movz [11, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 12:  # case: mul [12, rd, rt, rs]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 13:  # case: addi [13, rt, rs, imm]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 14:  # case: sw [14, rt, rs, BOffset]
                pib.addToBuffer(instr_check)
            elif instr_check[0] == 15:  # case: lw [15, rt, rs, BOffset]
                pib.addToBuffer(instr_check)

    def instr_check(self):
        return_field = [0, 0, 0, 0, 0]
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

        return_field[4] = inst_to_str(self.hitCheck)

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
            elif instruction_hex == 34:
                #sub Rd, Rs, Rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 6
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
                return return_field
            elif instruction_hex == 32:
                #add Rd, Rs, Rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 7
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
                return return_field
            elif instruction_hex == 2:
                #srl Rd, Rs, Shamt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Shamt = int(self.hitCheck[6:11], 2)
                return_field[0] = 8
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Shamt
                return return_field
            elif instruction_hex == 36:
                #and Rd, Rs, Rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 9
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
                return return_field
            elif instruction_hex == 37:
                #or rd, rs, rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 10
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
                return return_field
            elif instruction_hex == 10:
                #movz rd, rs, rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 11
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
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
            elif opcode_parse == 28:
                #mul rd, rs, rt
                Rd = int(self.hitCheck[16:21], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 12
                return_field[1] = Rd
                return_field[2] = Rt
                return_field[3] = Rs
                return return_field
            elif opcode_parse == 8:
                #addi Rt, Rs, imm
                Imm = to_int_2c(self.hitCheck[16:], 2)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                return_field[0] = 13
                return_field[1] = Rt
                return_field[2] = Rs
                return_field[3] = Imm
                return return_field
            elif opcode_parse == 11:
                # sw Rt, BOffset(Rs)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                BOffset = to_int_2c(self.hitCheck[16:])
                return_field[0] = 14
                return_field[1] = Rt
                return_field[2] = Rs
                return_field[3] = BOffset
            elif opcode_parse == 3:
                # lw Rt, Boffset(Rs)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                BOffset = to_int_2c(self.hitCheck[16:])
                return_field[0] = 15
                return_field[1] = Rt
                return_field[2] = Rs
                return_field[3] = BOffset

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
    # STILL NEEDS HAZARD CHECKS (SHOULD DO AFTER FINISHING PIPELINE)
    # IF INSTRUCTION IS LW OR SW, SEND TO PREMEM QUEUE. ALL OTHERS GO TO PREALU
    def send_next(self, controller):  # no idea what I was going for here
        maxSendPerCC = 0        # once counter hits 2, stop sending
        for x in range(0, 3):
            if maxSendPerCC <= 2:
                if not controller.pib.buffer[3-x] == 0:
                    instructionToSend = controller.pib.buffer[3 - x]
                    if instructionToSend[0] == 14 or instructionToSend[0] == 15:
                        controller.preMEM.addToBuffer(instructionToSend)
                        controller.pib.removeFromBuffer()
                        maxSendPerCC += 1
                    else:
                        controller.preALU.addToBuffer(instructionToSend)
                        controller.pib.removeFromBuffer()
                        maxSendPerCC += 1

class PREALU:
    def __init__(self):
        self.buffer = [0, 0]

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

class ALU:
    def execInstr(self, preALU, postalu, reg):
        instr = preALU.buffer[1]
        if instr != 0:
            preALU.removeFromBuffer()
            if instr[0] == 5:  # case: sll [5, rd, rt, shamt]
                instr.append(reg.r[instr[2]] << instr[3])
            elif instr[0] == 6:  # case: sub [6, rd, rt, rs]
                instr.append(reg.r[instr[3]] - reg.r[instr[2]])
            elif instr[0] == 7:  # case: add [7, rd, rt, rs]
                instr.append(reg.r[instr[3]] + reg.r[instr[2]])
            elif instr[0] == 8:  # case: srl [8, rd, rt, shamt]
                instr.append(reg.r[instr[2]] << instr[3])
            elif instr[0] == 9:  # case: and [9, rd, rt, rs]
                instr.append(reg.r[instr[3]] & reg.r[instr[2]])
            elif instr[0] == 10:  # case: or [10, rd, rt, rs]
                instr.append(reg.r[instr[3]] | reg.r[instr[2]])
            elif instr[0] == 11:  # case: movz [11, rd, rt, rs]
                if reg.r[instr[2]] == 0:
                    instr.append(reg.r[instr[3]])
            elif instr[0] == 12:  # case: mul [12, rd, rt, rs]
                instr.append(reg.r[instr[3]] * reg.r[instr[2]])
            elif instr[0] == 13:  # case: addi [13, rt, rs, imm]
                instr.append(reg.r[instr[2]] + reg.r[instr[3]])
            postalu.get_instr(instr)

class POSTALU(object):
    def __init__(self, alu):
        self.alu = alu
        self.queue = []

    def get_instr(self, instr):
        self.queue = instr

    def return_instr(self):
        if self.queue == []:
            return [-1]
        else:
            temp = self.queue
            self.queue = []
            return temp

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

    def ping(self):
        return self.buffer.index(0)


class MEM(object):
    """     elif instr_check[0] == 14:  # case: sw [14, rt, rs, BOffset]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 15:  # case: lw [15, rt, rs, BOffset]
        Rt = offsef(Rs)"""

    def __init__(self, premem, cache):
        self.premem = premem
        self.cache = cache

    def instr_grab(self, reg, postmem):
        pm_check = self.premem.ping()
        if not pm_check == 0:
            target = 96 #reg.r[pm_check[2]] # + to_int_2c(pm_check[3]) # calculates target address from contents of register[rs] + offset
            cache_check = self.cache.ping(target)
            if cache_check > 0:  # case cache hit
                self.premem.removeFromBuffer()
                if pm_check[0] == 14:   # case SW
                    self.cache.sw(target, pm_check[1])
                else:                   # case LW
                    pm_check.append(self.cache.lw(target))
                    postmem.get_instr()
                return -1
            else: # case cache miss
                return target
        return 0

class POSTMEM(object):
    def __init__(self, mem):
        self.mem = mem
        self.queue = []

    def get_instr(self, instr):
        self.queue = instr

    def return_instr(self):
        if self.queue == []:
            return [-1]
        else:
            temp = self.queue
            self.queue = []
            return temp


class WB(object):
    def __init__(self, reg, postmem, postalu):
        self.reg = reg
        self.postmem = postmem
        self.postalu = postalu

    def grab_and_write(self):
        mem_instr = self.postmem.return_instr()
        alu_instr = self.postalu.return_instr()
        if mem_instr[0] >= 0:
            self.reg.r[mem_instr[1]] = mem_instr[5]
        if alu_instr[0] >= 0:
            self.reg.r[alu_instr[1]] = mem_instr[5]


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


#start Clock Cycle
controller.next_cycle()
controller.next_cycle()
#WHILE INSTRUCTION IS NOT BREAK...

#try to fetch instructions
#check: 1. stall 2. PIB room 3. instruction type
if controller.ifetch.isStall == False:
    if controller.pib.isFull() > 0:
        print()# if


# class WB:





