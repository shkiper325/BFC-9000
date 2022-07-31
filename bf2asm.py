import argparse
from pickletools import read_unicodestringnl
from tkinter.messagebox import RETRY

MEMORY_SIZE = 30000
CHARACTERS = ('>', '<', '+', '-', '.', ',', '[', ']')

RESULT = ['.code32']
RESULT.append('.bss')
RESULT.append('memory:')
RESULT.append('.space ' + str(MEMORY_SIZE) + ', 0')

RESULT.append('.data')
RESULT.append('head_pos:')
RESULT.append('.long 0')
RESULT.append('char_buffer:')
RESULT.append('.byte 0')

RESULT.append('.text')
RESULT.append('.globl main')
RESULT.append('main:')

def parse_cmd_and_load():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bf-code', type=str, default='')
    parser.add_argument('--out', type=str, default='out.s')
    args = parser.parse_args()

    bf_code = ''
    if args.bf_code == '':
        while True:
            bf_code = bf_code + input()
            if bf_code[-2:] == '!\n':
                break
    else:
        fd = open(args.bf_code, 'r')
        bf_code = fd.read()
        fd.close()
      
    bf_code = [ch for ch in bf_code if ch in CHARACTERS]
    ''.join(bf_code)  

    return bf_code, args.out

def save(filename):
    fd = open(filename, 'w')
    fd.write('\n'.join(RESULT))
    fd.close()

POINTS = 0
def get_point():
    global POINTS
    ret = 'point_' + str(POINTS)
    POINTS += 1
    return ret

def find_first_close_bracket(text, start):
    depth = 0
    i = start

    while True:
        if i >= len(text):
            print('Error: code with bad brackets is given to find_first_close_bracket()')
            quit(1)

        if text[i] == '[':
            depth += 1
        elif text[i] == ']':
            if depth == 1:
                return i
            else:
                depth -= 1

        i += 1

def get_power(code, ch, start):
    power = 0
    for i in range(start, len(code)):
        if code[i] == ch:
            power += 1
        else:
            break
     
    return power

def parse_bf_code(code): # Remove non-bf symbols and optimize >, <, +, -
    ret = []

    i = 0
    while i < len(code):
        ch = code[i]

        if ch in ['[', ']', '.', ',', '-', '>', '<']:
            ret.append((ch, None))
            i += 1 
        elif ch in ['+']:
            power = get_power(code, ch, i)
            ret.append((ch, power))
            i += power
        else:
            print('Error: non-brainfuck symbol found in code in parse_bf_code()')
            quit(1)

    return ret

def main():
    bf_code, out_filename = parse_cmd_and_load()
    bf_code = parse_bf_code(bf_code)

    open_brackets = []
    close_brackets = []

    for i in range(len(bf_code)):
        ch, val = bf_code[i]
        if ch == '+':
            val %= 256

            RESULT.append('movl $memory, %ebx')
            RESULT.append('addl (head_pos), %ebx')
            RESULT.append('movw $0, %ax')
            RESULT.append('movb (%ebx), %al')
            RESULT.append('addw $' +  str(val) + ', %ax')
            RESULT.append('movb %al, (%ebx)')
        elif ch == '-':
            RESULT.append('movl $memory, %ebx')
            RESULT.append('addl (head_pos), %ebx')
            RESULT.append('movb (%ebx), %al')
            RESULT.append('cmp $0, %al')
            point_underflow = get_point()
            point_end = get_point()
            RESULT.append('je ' + point_underflow)
            RESULT.append('decb %al')
            RESULT.append('jmp ' + point_end)
            RESULT.append(point_underflow + ':')
            RESULT.append('movb $255, %al')
            RESULT.append(point_end + ':')
            RESULT.append('movb %al, (%ebx)')
        elif ch == '.':
            RESULT.append('movl $4, %eax')
            RESULT.append('movl $1, %ebx')
            RESULT.append('movl $memory, %ecx')
            RESULT.append('addl (head_pos), %ecx')
            RESULT.append('movl $1, %edx')
            RESULT.append('int $0x80')
        elif ch == '>':
            RESULT.append('movl (head_pos), %eax')
            RESULT.append('cmp $' + str(MEMORY_SIZE - 1) + ', %eax')
            point_overflow = get_point()
            point_end = get_point()
            RESULT.append('je ' + point_overflow)
            RESULT.append('incl %eax')
            RESULT.append('movl %eax, (head_pos)')
            RESULT.append('jmp ' + point_end)
            RESULT.append(point_overflow + ':')
            RESULT.append('movl $0, %eax')
            RESULT.append('movl %eax, (head_pos)')
            RESULT.append(point_end + ':')
        elif ch == '<':
            RESULT.append('movl (head_pos), %eax')
            RESULT.append('cmp $0, %eax')
            point_underflow = get_point()
            point_end = get_point()
            RESULT.append('je ' + point_underflow)
            RESULT.append('decl %eax')
            RESULT.append('movl %eax, (head_pos)')
            RESULT.append('jmp ' + point_end)
            RESULT.append(point_underflow + ':')
            RESULT.append('movl $' + str(MEMORY_SIZE - 1) + ', %eax')
            RESULT.append('movl %eax, (head_pos)')
            RESULT.append(point_end + ':')
        elif ch == ',':
            RESULT.append('movl $3, %eax')
            RESULT.append('movl $0, %ebx')
            RESULT.append('movl $char_buffer, %ecx')
            RESULT.append('movl $1, %edx')
            RESULT.append('int $0x80')
            RESULT.append('movb (char_buffer), %al')
            RESULT.append('movl $memory, %ebx')
            RESULT.append('addl (head_pos), %ebx')
            RESULT.append('movb %al, (%ebx)')
        elif ch == '[':
            point_open = get_point()
            point_close = get_point()
            open_brackets.append(point_open)
            close_brackets.append(point_close)

            RESULT.append(point_open + ':')
            RESULT.append('movl $memory, %eax')
            RESULT.append('addl (head_pos), %eax')
            RESULT.append('movb (%eax), %al')
            RESULT.append('cmp $0, %al')
            RESULT.append('je ' + point_close)
        elif ch == ']':
            point_open = open_brackets.pop()
            point_close = close_brackets.pop()

            RESULT.append('movl $memory, %eax')
            RESULT.append('addl (head_pos), %eax')
            RESULT.append('movb (%eax), %al')
            RESULT.append('cmp $0, %al')
            RESULT.append('jne ' + point_open)
            RESULT.append(point_close + ':')
 
    save(out_filename)

if __name__ == '__main__':
    main()