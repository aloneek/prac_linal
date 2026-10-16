import sympy as sp

abet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" ### русский алфавит из 32 букв, Ё выкинута (пункт 1)
word = "СОНЯ" ### интересное слово из 4 букв (пункт 2)

### порождающая и проверочная матрицы кода Хэмминга (7,4) (пункт 3)
### позиции 1,2,4 (степени двойки) отданы под проверочные биты p1,p2,p4, позиции 3,5,6,7 - под информационные
### проверочный бит pk стоит на позиции k и отвечает за бит веса k в номере позиции
### строки G это формулы для каждого бита кодового слова: c = G*d
G = sp.Matrix([[1,1,0,1],   ### p1 = d1+d2+d4
               [1,0,1,1],   ### p2 = d1+d3+d4
               [1,0,0,0],   ### d1
               [0,1,1,1],   ### p4 = d2+d3+d4
               [0,1,0,0],   ### d2
               [0,0,1,0],   ### d3
               [0,0,0,1]])  ### d4

### столбец j матрицы H это двоичная запись числа j, поэтому синдром сразу дает номер испорченного бита
H = sp.Matrix([[0,0,0,1,1,1,1],
               [0,1,1,0,0,1,1],
               [1,0,1,0,1,0,1]])

### матрица выборки информационных битов из кодового слова (позиции 3,5,6,7)
R = sp.Matrix([[0,0,1,0,0,0,0],
               [0,0,0,0,1,0,0],
               [0,0,0,0,0,1,0],
               [0,0,0,0,0,0,1]])


def to_binary(x):
    return f'{x:05b}'

def to_bits(message):
    return [int(i) for i in ''.join(to_binary(abet.index(x)) for x in message)]

def to_word(bits):
    s = ''.join(str(i) for i in bits)
    return ''.join(abet[int(s[i:i + 5], 2)] for i in range(0, len(s), 5))

def to_str(bits):
    return ''.join(str(i) for i in bits)

def split(bits, z):
    return [bits[i:i + z] for i in range(0, len(bits), z)]

def code(bits): ### кодирование, каждый блок из 4 битов превращается в 7 битов (пункт 4)
    coded = []
    for block in split(bits, 4):
        coded += [int(i) for i in (G * sp.Matrix(block) % 2)]
    return coded

def spoil(bits, positions): ### вредоносное вмешательство, биты нумеруются с единицы (пункт 5)
    spoiled = bits[:]
    for p in positions:
        spoiled[p - 1] ^= 1
    return spoiled

def where(p): ### в каком блоке и на какой локальной позиции стоит бит p сквозной нумерации
    return (p - 1) // 7 + 1, (p - 1) % 7 + 1

def kind(p): ### проверочный бит или информационный, по локальной позиции внутри блока
    names = {1: 'p1', 2: 'p2', 4: 'p4', 3: 'd1', 5: 'd2', 6: 'd3', 7: 'd4'}
    return names[where(p)[1]]

def decode(bits): ### декодирование с поиском и исправлением ошибки по синдрому (пункт 6)
    decoded = []
    syndromes = []
    fixed = []
    for block in split(bits, 7):
        block = block[:]
        s = [int(i) for i in (H * sp.Matrix(block) % 2)]
        pos = s[0] * 4 + s[1] * 2 + s[2] ### синдром это двоичная запись номера испорченного бита
        if pos != 0:
            block[pos - 1] ^= 1
        syndromes.append((to_str(s), pos))
        fixed.append(to_str(block)) ### блок после исправления, до выборки информационных битов
        decoded += [int(i) for i in (R * sp.Matrix(block) % 2)]
    return decoded, syndromes, fixed


### таблица соответствий букв и их пятибитовых номеров (пункт 1)
print("таблица алфавита:")
for i in range(len(abet)):
    print(f"{abet[i]} = {i} = {to_binary(i)}", end='  ' if (i + 1) % 8 else '\n')

### проверка того что H*G = 0, то есть каждое кодовое слово лежит в ядре H
if (H * G % 2) == sp.zeros(3, 4):
    print(f"H*G = 0, образ G лежит в ядре H")
### проверка того что R*G = E, то есть выборка информационных битов возвращает исходный блок
if (R * G % 2) == sp.Matrix.eye(4):
    print(f"R*G = E, информационные биты достаются из кодового слова без изменений")

bits = to_bits(word)
print(f"слово {word} в двоичном коде: {to_str(bits)} ({len(bits)} бит)")
print(f"блоки по 4 бита: {[to_str(b) for b in split(bits, 4)]}")

coded = code(bits)
print(f"закодированное сообщение: {to_str(coded)} ({len(coded)} бит)")
print(f"блоки по 7 бит: {[to_str(b) for b in split(coded, 7)]}")

### серия A: ошибки копятся внутри одного блока (третьего, биты 15-21)
### серия B: столько же ошибок, но разнесенных по разным блокам
series = {"A (все ошибки в третьем блоке)": [[17], [17, 19], [17, 19, 20], [17, 19, 20, 21]],
          "B (ошибки в разных блоках)": [[3], [3, 12], [3, 12, 22], [3, 12, 22, 35]]}

for name in series:
    print(f"\nсерия {name}")
    for positions in series[name]:
        spoiled = spoil(coded, positions)
        decoded, syndromes, fixed = decode(spoiled)
        print(f"  портим {len(positions)} бит на позициях {positions}")
        print(f"    это (блок, локальная позиция, бит): {[(*where(p), kind(p)) for p in positions]}")
        print(f"    испорченный код:  {[to_str(b) for b in split(spoiled, 7)]}")
        print(f"    синдромы (двоичный, номер бита): {syndromes}")
        print(f"    исправленный код: {fixed}" + ("" if fixed == [to_str(b) for b in split(coded, 7)] else "  <- отличается от исходного"))
        print(f"    декодированные биты: {to_str(decoded)}")
        print(f"    слово: {to_word(decoded)}" + ("" if to_word(decoded) == word else "  <- слово испорчено"))
