import numpy as np
import random
from decimal import Decimal
from fractions import Fraction
import cv2
from matplotlib import pyplot as plt
import binascii
from math import log10, sqrt 
# http://coding.nutc.edu.tw/student/lesson/D08/
# https://stackoverflow.com/questions/477486/how-to-use-a-decimal-range-step-value

# img = cv2.imread('baboon.bmp', cv2.IMREAD_GRAYSCALE)
# img = cv2.imread('52325.jpg', 0)
# img = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)
img_o = cv2.imread('img.jpg')
# print(img.shape)
# GBR_2_RGB
# img = img_o[:,:,::-1]
img = (img_o[:,:,::-1])[:,:,1]


text = 'quantizationlosspayl'

def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits='11000010110001001100011'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()


    # binary_int = int(bits, 2)
    # byte_number = binary_int.bit_length() + 7 // 8

    # binary_array = binary_int.to_bytes(byte_number, "big")
    # ascii_text = binary_array.decode()
    # return ascii_text

def binaryToDecimal(binary, length):
    # Fetch the radix point 
    point = binary.find('.')
 
    # Update point if not found 
    if (point == -1) :
        point = length 
 
    intDecimal = 0
    fracDecimal = 0
    twos = 1
 
    # Convert integral part of binary 
    # to decimal equivalent 
    for i in range(point-1, -1, -1) : 
        # Subtract '0' to convert 
        # character into integer 
        intDecimal += ((ord(binary[i]) - ord('0')) * twos) 
        twos *= 2
    
    # Convert fractional part of binary 
    # to decimal equivalent 
    twos = 2
    # print(point + 1, length)
    for i in range(point + 1, length):
        fracDecimal += ((ord(binary[i]) - ord('0')) / twos)
        twos *= 2.0

    # Add both integral and fractional part 
    ans = intDecimal + fracDecimal

    return ans

def decimal_converter(num):  
    while num > 1: 
        num /= 10
    return num 
    
def float_bin(number, places = 160):
    n = str(number)
    num_len = len(n)
    prefix_zero = ''
    res = ''

    for x in range(places):
        n = str(int(n) * 2)

        if prefix_zero != '':
            n += prefix_zero
            prefix_zero = ''

        if len(n) <= num_len:
            res += '0'
        else:
            res += n[0]
            n = n[1:]

        ck_len = len(str(int(n))) - len(n)

        if ck_len > 0:
            prefix_zero = ''.join(['0' for v in range(0, ck_len)])
  
    return res 

def PSNR(original, compressed): 
    mse = np.mean((original - compressed) ** 2) 
    if(mse == 0):
        return 100
    max_pixel = 255.0
    psnr = 20 * log10(max_pixel / sqrt(mse)) 
    return psnr 


# https://stackoverflow.com/questions/34599159/creating-a-binary-fraction-in-python


# Binary Fractions(二進制分數)
# w = ''.join('0'+format(ord(i), 'b') for i in text)
w = text_to_bits(text)
wp = '0.' + w
w_decimal = binaryToDecimal(wp, len(wp))


def getRangeW(R):
    r = {
        'min' : 0,
        'max' : 0,
        # R0,R1,R3 ....
        'wIndx' : 0
    }
    for i in range(len(R)):
        if w_decimal > R[i - 1] and w_decimal <= R[i]:
            r['min'] = R[i - 1]
            r['max'] = R[i]
            r['wIndx'] = i 
            # print(r['min'], w_decimal, r['max'])
    
    return r

def genLSB(L, img):
    # QL(S)
    QlS = (np.floor_divide(img, L)) * L

    Sw = QlS.copy()
    # Arithmetic Coding
    R = list(np.linspace(0,1, L + 1))
    w_collection = []
    n = 1
    
    # print(R, w_decimal)
    while n < L:
        n = n + 1
        r = getRangeW(R)
        # print('min:', r['min'], w_decimal, r['max'])
        # print(R,'----')
        R = list(np.linspace(r['min'], r['max'], L + 1))
        w_collection.append(r['wIndx'])

    # Sw = QL(S) + w 
    for i in range(len(w_collection)):
        Sw[0][i] = QlS[0][i] + w_collection[i]
        # print(Sw[0][i], QlS[0][i])

    # Extract hidden information
    # print('R:', R[0], R[len(R) - 1])
    w_range_any_decimal = random.uniform(R[0], R[len(R) - 1])
    w_range_any_decimal = str(w_range_any_decimal)[2:16]
    for x in range(1,4):
        w_range_any_decimal += w_range_any_decimal
    w_range_any_bin = float_bin(w_range_any_decimal, len(w))
    
    bit8 = 8
    bin_arr = [w_range_any_bin[i:i+bit8] for i in range(0, len(w_range_any_bin), bit8)]
    # txt_arr = [ bits_to_text(code[1:]) for code in bin_arr]

    ans_txt = ''
    for x in bin_arr:
        ans_txt += bits_to_text(x[1:])


    return {
        'QlS' : QlS,
        'Sw' : Sw,
        'w_collection' : w_collection,
        'decode_decimal' : '0.' + w_range_any_decimal,
        'last_r' : R,
        'ans_txt' : ans_txt,
        'PSNR' : str(PSNR(img, Sw))
    }

L3 = genLSB(3, img)
L8 = genLSB(8, img)
L12 = genLSB(12, img)
# cv2.imshow('My Image', img)
# show
print('To Encode Text: ', text)
print('Text to binary: ', wp)
print('Binary to decimal: ', w_decimal)

print('>>>>>>>>>>>>>>')
columns = 2
rows = 2
fig = plt.figure(figsize=(8, 8))

fig.add_subplot(rows, columns, 1)
plt.title('original',fontsize=12, color='#123123')
plt.imshow(img, cmap='gray')

fig.add_subplot(rows, columns, 2)
plt.title('L3',fontsize=12, color='#123123')
plt.text(20, 250, 'PSNR:'+ L3['PSNR'] ,fontsize=12, color='red', style='italic')
plt.imshow(L3['Sw'], cmap='gray')
print('L3 Decode text decimal:', L3['decode_decimal'])
print('L3 PSNR:', L3['PSNR'])
print('L3 Decode text:', L3['ans_txt'])
print('---------------------------')

fig.add_subplot(rows, columns, 3)
plt.title('L8',fontsize=12, color='#123123')
plt.text(20, 250, 'PSNR:'+ L8['PSNR'] ,fontsize=12, color='red', style='italic')
plt.imshow(L8['Sw'], cmap='gray')
print('L8 Decode text decimal:', L8['decode_decimal'])
print('L8 PSNR:', L8['PSNR'])
print('L8 Decode text:', L8['ans_txt'])
print('---------------------------')

fig.add_subplot(rows, columns, 4)
plt.title('L12',fontsize=12, color='#123123')
plt.text(20, 250, 'PSNR:'+ L12['PSNR'] ,fontsize=12, color='red', style='italic')
plt.imshow(L12['Sw'], cmap='gray')
print('L12 Decode text decimal:', L12['decode_decimal'])
print('L12 PSNR:', L12['PSNR'])
print('L12 Decode text: ', L12['ans_txt'])
print('---------------------------')

# for i in range(1, columns*rows +1):
#     img = np.random.randint(10, size=(5,5))
#     fig.add_subplot(rows, columns, i)
#     plt.imshow(img)

plt.show()
# print(type(img), img.shape)

# 顯示圖片
# plt.imshow(img)
# plt.show()
# cv2.imshow('My Image', img)

# 按下任意鍵則關閉所有視窗
# cv2.waitKey(0)
# cv2.destroyAllWindows()