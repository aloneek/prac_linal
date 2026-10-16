import sympy as sp

from hill import extended_gcd, to_digits, to_word, shifr, deshifr, alphabet, n

message = 'I_LOVE_ITMO!' ### придумываем ценное сообщение (пункт 2)

m2 = sp.Matrix([[1,1],[2,8]])
m3 = sp.Matrix([[7, 0, 28],[4,4,4],[8,1,2]])
m4 = sp.Matrix([[3,3,17,18],[22,9,1,15],[10,7,8,8],[20,11,7,20]]) 

mats = [m2,m3,m4] ### придумываем 3 матрицы ключа (пункт 3)

det_m2 = m2.det()
det_m3 = m3.det()
det_m4 = m4.det()


key_m2 = m2.adjugate()*extended_gcd(det_m2,n)[1]%n
key_m3 = m3.adjugate()*extended_gcd(det_m3,n)[1]%n
key_m4 = m4.adjugate()*extended_gcd(det_m4,n)[1]%n

keys = [key_m2,key_m3,key_m4]


### проверка обратности матриц
for i in range(len(mats)):
    if mats[i]*keys[i]%n == sp.Matrix.eye(mats[i].rows,mats[i].cols):
        print(f"матрицы {mats[i]} и {keys[i]} обратны")


for i in range(len(mats)):
    start_shifr = shifr(to_digits(message),mats[i]) ### шифруем сообщение (пункт 4)
    temp_word = to_word(start_shifr)
    print(f"зашифрованное собщение до подмены символов: {temp_word}")
    ### подмена символов в слове (пункт 5)
    h,j,k = 0,1,3
    temp_word = temp_word[:h] + 'Z' + temp_word[h+1:]
    temp_word = temp_word[:j] + 'X' + temp_word[j+1:]
    temp_word = temp_word[:k] + 'C' + temp_word[k+1:]

    print(f"зашифрованное собщение после подмены символов: {temp_word}")
    end_deshifr = deshifr(to_digits(temp_word),keys[i]) ### дешифруем слово со внедренными символами по индексам h,j,k (пункт 6)
    print(f"расшифрованное сообщение с подменой символов: {to_word(end_deshifr)}")
