import sys
import getopt

"""
STILL NEED:
print timing
-"""


# DISASSEMBLER METHODS
def to_int_2c(bin):
    if type(bin) == int or type(bin) == long:
        if bin < 0:
            return bin
        else:
            str(bin)
    if int(bin) < 0:
        return int(bin)
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
            Imm = str(to_int_2c(x[16:32]))
            return 'ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm
        elif instruction_hex == 11:
            # sw Rt, BOffset(Rs)
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            BOffset = str(to_int_2c(x[16:32]))
            return 'SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'
        elif instruction_hex == 3:
            # lw Rt, Boffset(Rs)
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            BOffset = str(to_int_2c(x[16:32]))
            return 'LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')'
        elif instruction_hex == 1:
            # bltz Rs, label
            Rs = str(int(x[6:11], 2))
            label = str(to_int_2c(x[16:32]))
            return 'BLTZ' + '\t' + 'R' + Rs + ', #' + label
        elif instruction_hex == 4:
            # beq Rs, Rt, label
            Rt = str(int(x[11:16], 2))
            Rs = str(int(x[6:11], 2))
            label = str(to_int_2c(x[16:32]))
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
        return R()
    elif opcode_parse == 2:
        return J()
    else:
        return I()


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
                            Imm = str(to_int_2c(x[16:32]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'ADDI' + '\t' + 'R' + Rt + ', R' + Rs + ', #' + Imm + '\n')
                        elif instruction_hex == 11:
                            # sw Rt, BOffset(Rs)
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            BOffset = str(to_int_2c(x[16:32]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'SW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                        elif instruction_hex == 3:
                            # lw Rt, Boffset(Rs)
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            BOffset = str(to_int_2c(x[16:32]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'LW' + '\t' + 'R' + Rt + ', ' + BOffset + '(R' + Rs + ')' + '\n')
                        elif instruction_hex == 1:
                            # bltz Rs, label
                            Rs = str(int(x[6:11], 2))
                            label = str(to_int_2c(x[16:32]))
                            output_file.write (x[0] + ' ' + x[1:6] + ' ' + x[6:11] + ' ' + x[11:16] + ' ' + x[16:21] + ' ' + x[21:26] + ' ' + x[26:] + '\t' + mem_address_str + '\t' + 'BLTZ' + '\t' + 'R' + Rs + ', #' + label + '\n')
                        elif instruction_hex == 4:
                            # beq Rs, Rt, label
                            Rt = str(int(x[11:16], 2))
                            Rs = str(int(x[6:11], 2))
                            label = str(to_int_2c(x[16:32]))
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
        self.holds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def print_regs(self, output):
        output.write('\n\nRegisters\nR00:')
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
        self.still_running = True
        self.pipeline_has_stuff = False
        self.mem_miss = False
        self.fetch_miss = False
        self.mem_code = -1

        #MACHINE COMPONENTS
        self.reg = REG()
        self.cache = CACHE(iput)
        self.ifetch = IF(self.reg)
        self.pib = PREISSUEBUFFER()
        self.issue = ISSUE()
        self.preALU = PREALU()
        self.preMEM = PREMEM()
        self.alu = ALU()
        self.postalu = POSTALU(self.alu)
        self.mem = MEM(self.preMEM, self.cache)
        self.postmem = POSTMEM(self.mem)
        self.wb = WB(self.reg, self.postmem, self.postalu)

    def print_state(self):  # function to output all states of current cycle
        self.output.write('--------------------\n')
        self.output.write('Cycle: ' + str(self.cycle) + '\n\n')
        self.pib.printPrebuffer(self.output)
        self.preALU.print_state(self.output)
        self.postalu.print_state(self.output)
        self.preMEM.print_state(self.output)
        self.postmem.print_state(self.output)
        self.reg.print_regs(self.output)
        self.cache.print_state(self.output)

    def next_cycle(self):
        if self.mem_miss:
            self.cache.grab_mem(self.mem_code)
        if self.fetch_miss:
            self.cache.grab_mem(self.pc)    # at end of cycle, if we had cache miss, tell cache to grab the stuff

        self.wb.grab_and_write()
        self.mem_code = self.mem.instr_grab(self.reg, self.postmem)
        if self.mem_code > 0:  # function above returns the target address if there's a cache miss from MEM unit
            self.mem_miss = True
        else:             # with this algorithm, a LW will only stall for one fetch, so not sure if this is correct
            self.stalled = False
            self.mem_miss = False
        self.alu.execInstr(self.preALU, self.postalu, self.reg)
        self.issue.send_next(self)
        if not self.stalled and not self.break_found:
            fetch_code = self.ifetch.fetch(self.reg, self.cache, self.pc, self.pib)
            if fetch_code == -1:
                self.fetch_miss = True
            elif fetch_code == 0:
                self.break_found = True
            elif fetch_code > 0:
                self.pc = fetch_code
                self.fetch_miss = False
            else:
                self.pc += 8  # if no cache miss, increment PC
                self.fetch_miss = False
        self.pipeline_has_stuff = self.check_pipeline_for_stuff()
        if not self.pipeline_has_stuff and self.break_found:
            # self.cache.wb_all()
            self.still_running = False
        self.print_state()
        self.cycle += 1


    def check_pipeline_for_stuff(self):
        if self.pib.is_clear() and self.preALU.is_clear() and self.preMEM.is_clear() and self.postmem.is_clear() and self.postalu.is_clear():
            return False
        else:
            return True


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
        request_set = request_set >> 3
        if self.sets[request_set][0][2] == request_tag:       # check first block in matching set for hit
            self.assocblock = 0
            self.hit = True
            self.LRU[request_set] = 1
        elif self.sets[request_set][1][2] == request_tag:     # check second block
            self.assocblock = 1
            self.hit = True
            self.LRU[request_set] = 0
        else:
            self.hit = False
            return 'miss'
        if pc % 8 == 0:
            return self.sets[request_set][self.assocblock][3]       # if address is %8 then we want the first word in block
        else:
            return self.sets[request_set][self.assocblock][4]       # else we want second word in block


    def sw(self, target, value):
        request_tag = target >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        request_set = target & self.set_mask
        request_set = request_tag >> 3
        target_entry = 4
        # self.LRU[request_set] = 0
        if target % 8 == 0:
            target_entry = 3  # if address is %8 then we want the first word in block
            # self.LRU[request_set] = 1
        self.sets[request_set][self.assocblock][1] = 1
        self.sets[request_set][self.assocblock][target_entry] = value  # else we want second word in block

    """
    THIS ENTIRE FUNCTION IS UNNECESSARY. LW IS HANDLED IN MEM WHEN IT PINGS CACHE FOR A VALUE...
    def lw(self, target):
        request_tag = target >> 5  # maybe not correct, this whole block attempts to decode the fetch request address
        request_set = target & self.set_mask
        request_set = request_tag >> 3
        target_entry = 4
        if target % 8 == 0:
            target_entry = 4  # if address is %8 then we want the first word in block
        return int(self.sets[request_set][self.assocblock][target_entry])  # else we want second word in block"""

    def split_mem(self, mem):  # populates our lists at initialization
        is_not_break = True
        for line in mem:
            if is_not_break:
                x = line
                self.instructions.append(x[0:32])
                self.num_instructions += 1
                if x[0:32] == '10000000000000000000000000001101':
                    is_not_break = False
                else:
                    self.break_line += 4  # finds the mem location for BREAK so we can determine which list to pull from
            else:
                x = line
                self.memory.append(x[0:32])

    def grab_mem(self, Pc):  # pull the requested address from instructions or memory based on break_line value
        if Pc % 8 == 0:
            pc = Pc
        else:
            pc = Pc - 4
        block_to_grab = 0
        block_to_grab2 = (pc - 96)/4
        block_tag = pc >> 5
        block_set = pc & self.set_mask
        block_set = block_set >> 3
        if self.sets[block_set][0][2] == block_tag:       # check first block in matching set for hit
            return
        elif self.sets[block_set][1][2] == block_tag:     # check second block
            return
        if pc < self.break_line:
            block_to_grab = self.instructions[int(block_to_grab2)]
            if block_to_grab != len(self.instructions) - 1:
                block_to_grab2 = self.instructions[int(block_to_grab2) + 1]
            else:
                block_to_grab2 = self.memory[0]
        else:
            block_to_grab = self.memory[block_to_grab2 - self.num_instructions]
            block_to_grab2 = self.memory[block_to_grab2 - self.num_instructions + 1]
            block_to_grab = to_int_2c(block_to_grab)
            block_to_grab2 = to_int_2c(block_to_grab2)

        if self.sets[block_set][self.LRU[block_set]][1] == 1:  # detect if writeback necessary
            self.write_back(block_set, self.sets[block_set][self.LRU[block_set]][2], self.sets[block_set][self.LRU[block_set]][3], self.sets[block_set][self.LRU[block_set]][4])
        self.sets[block_set][self.LRU[block_set]][0] = 1
        self.sets[block_set][self.LRU[block_set]][2] = block_tag
        self.sets[block_set][self.LRU[block_set]][3] = block_to_grab
        self.sets[block_set][self.LRU[block_set]][4] = block_to_grab2
        if self.LRU[block_set] == 1:
            self.LRU[block_set] = 0
        else:
            self.LRU[block_set] = 1

    def write_back(self, set, tag, word1, word2):
        mem_to_write_to = (set << 3) + (tag << 5)
        target = (mem_to_write_to - 96)/4
        if mem_to_write_to < self.break_line:
            self.instructions[target] = word1
            self.instructions[target + 1] = word2
        else:
            self.memory[(target - self.num_instructions)] = word1
            self.memory[(target - self.num_instructions) + 1] = word2

    def wb_all(self):
        for x in range(len(self.sets)):
            for y in range(len(self.sets[x])):
                if self.sets[x][y][1] == 1:
                    self.sets[x][y][1] = 0
                    self.write_back(x, self.sets[x][y][2], self.sets[x][y][3], self.sets[x][y][4])

    def print_state(self, output):
        output.write('\n\nCache')
        for x in range(4):
            output.write('\nSet ' + str(x) + ': LRU=' + str(self.LRU[x]))
            for y in range(2):
                output.write('\n\tEntry ' + str(y) + ':[(' + str(self.sets[x][y][0]) + ',' + str(self.sets[x][y][1]) + ',' + str(self.sets[x][y][2]) + ')<' + str(self.sets[x][y][3]) + ',' +str( self.sets[x][y][4]) + '>]')
        output.write('\n\nData')
        data_start = (self.num_instructions * 4) + 96
        num_data = len(self.memory)
        for x in range(num_data):
            if x % 8 == 0:
                output.write('\n' + str((data_start + (x * 4))) + ':')
            if x % 8 == 7:
                if type(self.memory[x]) == int:
                    output.writestr((self.memory[x]))
                else:
                    output.write(str(to_int_2c(str(self.memory[x]))))
            else:
                if type(self.memory[x]) == int:
                    output.write(str((self.memory[x])))
                else:
                    output.write(str(to_int_2c(str(self.memory[x]))))
                output.write('\t')
        output.write('\n')


class IF:
    def __init__(self, reg):
        self.hitCheck = 0       # in case of cache miss, returns -1 to controller so that it doesnt increment pc
        self.isStall = False    # if fetch unit is stalled, no instruction fetch
        self.reg = reg

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

    def fetch(self, reg, cache, pc, pib):         # requests information at address: pc from cache
        """SOHAILS NOTES: I'm setting this function to return 4 possible values back to the controller:
            -1 if its a miss - controller tells cache to grab that mem block at end of cycle
            -2 if we have a BEQ/BLTZ and we need a stall - NOT IMPLEMENTED IDK WHAT TO DO FOR THIS, HOW DOES IT KNOW IF THE REGISTERS ARE READY OR NOT
            PC values if we have a jump/jr/branch and registers are ready - controller updates pc value at end of cycle - NOT IMPLEMENTED SEE ABOVE
            0 if we found BREAK

            note: nops and invalid instructions are just discarded I guess so the controller doesn't need to know bout that   """

        self.hitCheck = cache.ping(pc)
        if self.hitCheck == 'miss':     # make sure we hit
            return -1
        # IF HITCHECK != BRANCH, NOP, INVALID, OR BREAK...
        # controller.pib.addToBuffer(self.hitCheck)   # add instruction to PIB
        instr_check = self.instr_check()
        if instr_check[0] == -1:  # case: BREAK found [-1,0,0,0]
            return 0
        elif instr_check[0] == 0:  # case: nop or invalid instr - discard instruction [0,0,0,0]
            self.hitCheck = 1
        elif instr_check[0] == 1:   # case: jr instr [1,rs,0,0]
            if reg.holds[instr_check[1]] == 0:
                return reg.r[instr_check[1]] + 4
            else:
                return pc
        elif instr_check[0] == 2:   # case: jump [2,jump_address,0,0]
            return instr_check[1] + 4
        elif instr_check[0] == 3:  # case: bltz [3,rs,label,0]
            if self.reg.holds[instr_check[1]] == 0:
                if self.reg.r[instr_check[1]] < 0:
                    return pc + instr_check[2] + 4
            else:
                return pc
        elif instr_check[0] == 4:  # case: beq [4,rs,rt,label]
            if self.reg.holds[instr_check[1]] == 0 and self.reg.holds[instr_check[2]] == 0:
                if self.reg.r[instr_check[1]] == self.reg.r[instr_check[2]]:
                    return instr_check[3] + 4
            else:
                return pc
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

        if pib.isFull() > 0 and self.hitCheck != 'miss':  # if hit and we have space, get next word also
            self.hitCheck = cache.ping(pc + 4)
            if self.hitCheck == 'miss':
                return pc + 4
            instr_check = self.instr_check()
            if instr_check[0] == -1:  # case: BREAK found [-1,0,0,0]
                return 0
            elif instr_check[0] == 0:  # case: nop or invalid instr - discard instruction [0,0,0,0]
                self.hitCheck = -1
            elif instr_check[0] == 1:  # case: jr instr [1,rs,0,0]
                if reg.holds[instr_check[1]] == 0:
                    return reg.r[instr_check[1]] + 4
                else:
                    return pc + 4
            elif instr_check[0] == 2:  # case: jump [2,jump_address,0,0]
                return instr_check[1] + 4
            elif instr_check[0] == 3:  # case: bltz [3,rs,label,0]
                if self.reg.holds[instr_check[1]] == 0:
                    if self.reg.r[instr_check[1]] < 0:
                        return pc + instr_check[2] + 4
                else:
                    return pc + 4
            elif instr_check[0] == 4:  # case: beq [4,rs,rt,label]
                if self.reg.holds[instr_check[1]] == 0 and self.reg.holds[instr_check[2]] == 0:
                    if self.reg.r[instr_check[1]] == self.reg.r[instr_check[2]]:
                        return instr_check[3] + 4
                else:
                    return pc + 4
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
        if self.hitCheck[0] == '0': #invalid instr check
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
                    Rt = int(self.hitCheck[11:16], 2)
                    Shamt = int(self.hitCheck[21:26], 2)
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
                label = to_int_2c(self.hitCheck[16:32])
                return_field[0] = 3
                return_field[1] = Rs
                return_field[2] = label
                return return_field
            elif opcode_parse == 4:
                # beq Rs, Rt, label
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                label = to_int_2c(self.hitCheck[16:32])
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
                Imm = to_int_2c(self.hitCheck[16:32])
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
                BOffset = to_int_2c(self.hitCheck[16:32])
                return_field[0] = 14
                return_field[1] = Rt
                return_field[2] = Rs
                return_field[3] = BOffset
            elif opcode_parse == 3:
                # lw Rt, Boffset(Rs)
                Rt = int(self.hitCheck[11:16], 2)
                Rs = int(self.hitCheck[6:11], 2)
                BOffset = to_int_2c(self.hitCheck[16:32])
                return_field[0] = 15
                return_field[1] = Rt
                return_field[2] = Rs
                return_field[3] = BOffset

        return return_field

    # BRANCH, BREAK, NOP, AND INVALID INSTRUCTIONS ARE ALL FETCHED. IF WILL HANDLE THEM.


class PREISSUEBUFFER:
    def __init__(self):
        self.buffer = []

    def addToBuffer(self, instruction):
        self.buffer.append(instruction)

    def removeFromBuffer(self, x):
            self.buffer.pop(x)

    def isFull(self):
        slotsAvailable = 4 - len(self.buffer)
        if slotsAvailable == 0:
            return 0
        if slotsAvailable == 1:
            return 1
        else:
            return 2

    def printPrebuffer(self, output):
        output.write('Pre-Issue Buffer:')
        for x in range (4):
            output.write('\n\tEntry ' + str(x) + ':')
            if len(self.buffer) >= x + 1:
                output.write('\t[' + self.buffer[x][4] + ']')

    def is_clear(self):
        if len(self.buffer) > 0:
            return False
        else:
            return True


class ISSUE():
    # STILL NEEDS HAZARD CHECKS (SHOULD DO AFTER FINISHING PIPELINE)
    # IF INSTRUCTION IS LW OR SW, SEND TO PREMEM QUEUE. ALL OTHERS GO TO PREALU
    def send_next(self, controller):
        sent = 0
        items_to_remove = []
        item_number = 0
        sw_passed_up = False
        for x in controller.pib.buffer:
            if sent >= 2:
                break
            instructionToSend = x
            if instructionToSend[0] == 14 or instructionToSend[0] == 15: # case SW or LW - sending to preMEM
                if (instructionToSend[0] == 14 or controller.reg.holds[instructionToSend[1]] == 0) and controller.preMEM.isFull() > 0 and not sw_passed_up:
                    items_to_remove.append(item_number)
                    controller.preMEM.addToBuffer(instructionToSend)
                    sent += 1
                    if instructionToSend[0] == 15:
                        controller.reg.holds[instructionToSend[1]] = 1
                elif instructionToSend[0] == 14:
                    sw_passed_up = True
            elif not (instructionToSend[0] == 14 or instructionToSend[0] == 15) and (controller.reg.holds[instructionToSend[1]] == 0) and controller.preALU.isFull() > 0:  # case anything else
                if instructionToSend[0] == 5:  # case: sll [5, rd, rt, shamt]
                    if controller.reg.holds[instructionToSend[2]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 6:  # case: sub [6, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 7:  # case: add [7, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 8:  # case: srl [8, rd, rt, shamt]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 9:  # case: and [9, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 10:  # case: or [10, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 11:  # case: movz [11, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 12:  # case: mul [12, rd, rt, rs]
                    if controller.reg.holds[instructionToSend[2]] == 0 and controller.reg.holds[instructionToSend[3]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
                elif instructionToSend[0] == 13:  # case: addi [13, rt, rs, imm]
                    if controller.reg.holds[instructionToSend[2]] == 0:
                        controller.reg.holds[instructionToSend[1]] = 1
                        controller.preALU.addToBuffer(instructionToSend)
                        items_to_remove.append(item_number)
                        sent += 1
            item_number += 1
        items_to_remove.reverse()
        for x in items_to_remove:
            controller.pib.removeFromBuffer(x)


class PREALU:
    def __init__(self):
        self.buffer = []

    def isFull(self):
        return 2 - len(self.buffer)

    def addToBuffer(self, instruction):
        self.buffer.append(instruction)

    def removeFromBuffer(self):
            self.buffer.pop(0)

    def is_clear(self):
        if len(self.buffer) > 0:
            return False
        else:
            return True
    def print_state(self, output):
        output.write('\nPre_ALU Queue:')
        for x in range (2):
            output.write('\n\tEntry ' + str(x) + ':')
            if len(self.buffer) >= x + 1:
                output.write('\t[' + self.buffer[x][4] + ']')



class ALU:
    def execInstr(self, preALU, postalu, reg):
        if preALU.buffer != []:
            instr = preALU.buffer[0]
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
                instr.append(reg.r[instr[2]] + instr[3])
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

    def is_clear(self):
        if len(self.queue) > 0:
            return False
        else:
            return True
    def print_state(self, output):
        output.write('\nPost_ALU Queue:')
        output.write('\n\tEntry 0:')
        if len(self.queue) > 0:
            output.write('\t[' + str(self.queue[4]) + ']')


class PREMEM:
    def __init__(self):
        self.buffer = []

    def isFull(self):
        return 2 - len(self.buffer)

    # add instruction [0,0] --> [0,I1]
    def addToBuffer(self, instruction):
        self.buffer.append(instruction)

    # remove instruction[I2,I1] --> [0,I2]
    def removeFromBuffer(self):
        # if first in line is occupied, POP and add 0 at end of line
        if self.buffer != []:
            return self.buffer.pop(0)
        else:
            return 0

    def is_clear(self):
        if len(self.buffer) > 0:
            return False
        else:
            return True
    def print_state(self, output):
        output.write('\nPre_MEM Queue:')
        for x in range(2):
            output.write('\n\tEntry ' + str(x) + ':')
            if len(self.buffer) >= x + 1:
                output.write('\t[' + self.buffer[x][4] + ']')


class MEM(object):
    """     elif instr_check[0] == 14:  # case: sw [14, rt, rs, BOffset]
            pib.addToBuffer(instr_check)
        elif instr_check[0] == 15:  # case: lw [15, rt, rs, BOffset]
        Rt = offsef(Rs)"""

    def __init__(self, premem, cache):
        self.premem = premem
        self.cache = cache

    def instr_grab(self, reg, postmem):
        if self.premem.buffer != []:
            pm_check = self.premem.buffer[0]
            target = reg.r[pm_check[2]] + pm_check[3] # calculates target address from contents of register[rs] + offset
            cache_check = self.cache.ping(target)
            if cache_check != 'miss':  # case cache hit
                self.premem.removeFromBuffer()
                if pm_check[0] == 14:   # case SW
                    self.cache.sw(target, reg.r[pm_check[1]])
                    return -2 # case SW successful, remove hold on LW
                else:                   # case LW
                    pm_check.append(cache_check)
                    postmem.get_instr(pm_check)
                return -1
            else: # case cache miss
                return target
        return 0


class POSTMEM(object):
    def __init__(self, mem):
        self.mem = mem
        self.queue = []

    def get_instr(self, instr):
        self.queue.append(instr)

    def return_instr(self):
        if self.queue == []:
            return [-1]
        else:
            return self.queue.pop(0)

    def is_clear(self):
        if len(self.queue) > 0:
            return False
        else:
            return True
    def print_state(self, output):
        output.write('\nPost_MEM Queue:')
        x = 0
        output.write('\n\tEntry ' + str(x) + ':')
        if len(self.queue) >= x + 1:
            output.write('\t[' + self.queue[x][4] + ']')



class WB(object):
    def __init__(self, reg, postmem, postalu):
        self.reg = reg
        self.postmem = postmem
        self.postalu = postalu

    def grab_and_write(self):
        mem_instr = self.postmem.return_instr()
        alu_instr = self.postalu.return_instr()
        if not mem_instr[0] < 0:
            self.reg.r[mem_instr[1]] = mem_instr[5]
            if mem_instr[0] == 15:
                self.reg.holds[mem_instr[1]] = 0
        if not alu_instr == '0' and not alu_instr[0] < 0:
            self.reg.r[alu_instr[1]] = alu_instr[5]
            if alu_instr[0] == 5:  # case: sll [5, rd, rt, shamt]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
            elif alu_instr[0] == 6:  # case: sub [6, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 7:  # case: add [7, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 8:  # case: srl [8, rd, rt, shamt]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
            elif alu_instr[0] == 9:  # case: and [9, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 10:  # case: or [10, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 11:  # case: movz [11, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 12:  # case: mul [12, rd, rt, rs]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
                self.reg.holds[alu_instr[3]] = 0
            elif alu_instr[0] == 13:  # case: addi [13, rt, rs, imm]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
            elif alu_instr[0] == 14:  # case: sw [14, rt, rs, BOffset]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0
            elif alu_instr[0] == 15:  # case: lw [15, rt, rs, BOffset]
                self.reg.holds[alu_instr[1]] = 0
                self.reg.holds[alu_instr[2]] = 0


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


# start Clock Cycle
while controller.still_running:
    controller.next_cycle()
    do = "shit"
controller.cache.wb_all()
controller.print_state()





