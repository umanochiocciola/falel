from sys import argv

if len(argv) < 2:
    print("arguments:\nfile [flags]")
    print("flags:\n\t-c or --compile\t\tautomatically compyle using gcc\n\t--clean\t\t\tremove out.c\n\t-o <name>\t\tname of output file")
    
    exit(1)
    


try:
    with open(argv[1], 'r') as f:
        program = f.read()
except:
    print("no such file"); exit(1)

flags = []
for i in argv[1:]:
    if i[0] in ['-', '--']:
        flags.append(i.replace('-', ''))


def debug(txt, typ='info'):
    print(f'[{typ}] {txt}')
    0


debug('building references')

keys = {
    'mov': 2,
    'add': 1,
    'sub': 1,
    'fls': 1,
    'saz': 0,
    'wnz': 1,
    'slh': 0,
    'uib': 1,
}

repls = {
    'mov': '$1 = $0',
    'add': 'tape[2] += $0; while(tape[2]>255){tape[2] -= 255;}',
    'sub': 'tape[2] -= $0; while(tape[2]<0){tape[2] += 255;}',
    'fls': 'printf("%$0", tape[0])',
    'saz': 'tape[2] = 0',
    'wnz': 'while ($0){',
    'slh': '}',
    'uib': 'scanf("%$0", &tape[1])',
}

RegNames = {
    'acc': 'x2',
    'out': 'x0',
    'inb': 'x1'
}

debug('reading constants')

NewProgrBuff = []
for line in program.split('\n'):
    for comm in line.split(';'):
        comm = comm.strip(' ')
        #print(comm)
        if comm.split(' ')[0] == 'const':
            try:
                RegNames[comm.split(' ')[1]] = comm.split(' ')[2]
            except: debug(f'{comm}:  const statement not completed', 'error')
        else:
            NewProgrBuff.append(comm)

program = NewProgrBuff

#print(RegNames)
debug('setting up')

cells = 255

init = '#include <stdio.h>\n#define CELLS ' + str(cells) + '\n\nint main(){\nint tape[CELLS] = {0};'
OUTPUT = '/*transpiled with falelC*/\n'+init+'\n'


debug('transpiling')

#print(program)
POG = 0
while POG < len(program):

    cian = program[POG]
    POG += 1
        
    key = cian.split(' ')[0]
    args = cian.strip(key+' ').split(' ')
    if args == ['']: args = []

    #print(f'{key} {args}')

    if not(key in keys):
        continue
    
    if len(args) != keys[key]:
        debug(f'line {POG}: {key} takes {keys[key]} arguments, but {len(args)} were given.', 'error')
    
    buildbuff = repls[key]
    
    for i in range(keys[key]):
        if args != []: buildbuff = buildbuff.replace(f'${i}', args[i])

    
    for name in RegNames:
        buildbuff = buildbuff.replace(name, RegNames[name])
    
    fixedbuff= ''
    ficser = 0
    for ch in buildbuff:
        if ch == 'x':
            ficser = 1
            fixedbuff += 'tape['
            
        
        elif ficser and not (ch in '1234567890'):
            fixedbuff += ']'+ch
            ficser = 0

        else:
            fixedbuff += ch

    if ficser: fixedbuff += ']'
    
    OUTPUT += fixedbuff+';'
    if OUTPUT[-2] == '}': OUTPUT = OUTPUT[:-1]
    
    OUTPUT += '\n'

OUTPUT += 'return 0;}'

debug('writing to out.c')

with open('out.c', 'w') as f:
    f.write(OUTPUT)

if 'c' in flags or 'compile' in flags:
    out = 'out'
    if 'o' in flags:
        out = argv[argv.index('-o')+1]
    
    debug(f'compiling to {out}')
    import os
    os.system(f'gcc out.c -o {out} >.garbage 2>&1')
    os.system('rm .garbage')
    if 'clean' in flags:
        os.system('rm out.c')
    else:
        debug('to automatically remove out.c use --clean', 'note')
else:
    debug('to automatically compile use -c or --compile', 'note')

debug('done!')
