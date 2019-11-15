"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.branch_table = {}
        self.branch_table[0b10000010] = {
            "instruction": "LDI", "handle": self.handle_LDI}
        self.branch_table[0b01000111] = {
            "instruction": "PRN", "handle": self.handle_PRN}
        self.branch_table[0b10100010] = {
            "instruction": "MUL", "handle": self.handle_ALU}
        self.branch_table[0b10100000] = {
            "instruction": "ADD", "handle": self.handle_ALU}
        self.branch_table[0b01000101] = {
            "instruction": "PUSH", "handle": self.handle_PUSH}
        self.branch_table[0b01000110] = {
            "instruction": "POP", "handle": self.handle_POP}
        self.branch_table[0b01010000] = {
            "instruction": "CALL", "handle": self.handle_CALL}
        self.branch_table[0b00010001] = {
            "instruction": "RET", "handle": self.handle_RET}
        self.branch_table[0b00000001] = {
            "instruction": "HLT", "handle": self.handle_HLT}
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xf4

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("USAGE: ls8.py filename")
            sys.exit(1)

        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip()  # remove spaces

                if line == "":
                    continue

                val = int(line, 2)

                self.ram[address] = val

                address += 1

    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, pc, value):
        self.ram[pc] = value

    def reg_read(self, pc):
        return self.reg[pc]

    def reg_write(self, pc, value):
        self.reg[pc] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %i" % self.reg[i], end='')

        print()

    def handle_LDI(self, op):
        register = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)

        self.reg_write(register, value)

        self.pc += 3
        self.trace()

    def handle_ALU(self, op):
        """ALU operations."""
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            multiplication = self.reg_read(reg_a) * self.reg_read(reg_b)
            self.reg_write(reg_a, multiplication)
        else:
            raise Exception("Unsupported ALU operation")

        self.pc += 3
        self.trace()

    def handle_PUSH(self, op):
        self.reg[self.sp] -= 1  # f3
        reg_location = self.ram[self.pc + 1]
        reg_value = self.reg[reg_location]

        self.ram[self.reg[self.sp]] = reg_value

        self.pc += 2

    def handle_POP(self, op):
        value = self.ram[self.reg[self.sp]]
        reg_location = self.ram[self.pc + 1]
        self.reg[reg_location] = value

        self.reg[self.sp] += 1

        self.pc += 2

    def handle_CALL(self, op):
        return_address = self.pc + 2

        self.reg[self.sp] -= 1

        self.ram[self.reg[self.sp]] = return_address

        reg_location = self.ram[self.pc + 1]
        self.pc = self.reg[reg_location]

    def handle_RET(self, op):
        self.pc = self.ram[self.reg[self.sp]]

        self.reg[self.sp] += 1

    def handle_PRN(self, op):
        register_value = self.reg_read(self.ram_read(self.pc + 1))

        print(f"PRN: R{self.ram_read(self.pc + 1)}: {register_value}")

        self.pc += 2
        self.trace()

    def handle_HLT(self, op):
        print("HLT")
        sys.exit(1)

    def run(self):
        while True:
            instruction = self.ram_read(self.pc)
            retrieve = self.branch_table[instruction]
            retrieve["handle"](retrieve["instruction"])
