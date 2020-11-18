import numpy as np
import pickle
import cv2
from scipy.cluster.vq import vq
from math import log10, sqrt 
from matplotlib import pyplot as plt

def block_view(A, block):
    # Reshape the array into a 2D array of 2D blocks, with the resulting axes in the
    # order of:
    #    block row number, pixel row number, block column number, pixel column number
    # And then rearrange the axes so that they are in the order:
    #    block row number, block column number, pixel row number, pixel column number
    return A.reshape(A.shape[0]//block[0], block[0], A.shape[1]//block[1], block[1])\
            .transpose(0, 2, 1, 3)


def PSNR(original, compressed): 
    mse = np.mean((original - compressed) ** 2) 
    if(mse == 0):  # MSE is zero means no noise is present in the signal . 
                  # Therefore PSNR have no importance. 
        return 100
    max_pixel = 255.0
    psnr = 20 * log10(max_pixel / sqrt(mse)) 
    return psnr 
    

def cos_sim(vec_a, vec_b):
    # Dot and norm
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a*a for a in vec_a) ** 0.5
    norm_b = sum(b*b for b in vec_b) ** 0.5
    # Cosine similarity
    val = dot / (norm_a*norm_b)
    
    return val

img_url = 'img.jpg'
img_o = cv2.imread(img_url)
img = (img_o[:,:,::-1])[:,:,1]

file_name = 'codebook_v3.pkl'
img2_url = 'img2.jpg'
img2_o = cv2.imread(img2_url)
img2 = (img2_o[:,:,::-1])[:,:,1]

open_file = open(file_name, "rb")
loaded_list = pickle.load(open_file)
open_file.close()

code_book = np.array(loaded_list)

# print(code_book.shape)
# Output: (256, 16) -> (y, x)

blocks = block_view(img2, (4, 4))
img_size_h = blocks.shape[0]
img_size_w = blocks.shape[1]
vq_img = np.zeros(img_size_h*img_size_w).reshape(img_size_h, img_size_w)


for i in range(img_size_h):
    for j in range(img_size_w):
        blc = blocks[i,j].reshape(1,16)
        # print(i,j, vq(blc, code_book)[1])
        vq_img[i][j] = vq(blc, code_book)[0]



max = 0
vq_img_size_h = vq_img.shape[0]
vq_img_size_w = vq_img.shape[1]
encode_str = ''
vq_img_steg = np.zeros(vq_img_size_h*vq_img_size_w).reshape(vq_img_size_h, vq_img_size_w)

vq_img_soc = vq_img_steg.copy()
de_vq_img = np.zeros(256*256).reshape(256, 256)

sec_num = 4096
secret = list(np.random.randint(2, size=sec_num))

# De vq
li_code_book = code_book.tolist()

for i in range(vq_img_size_h):
    for j in range(vq_img_size_w):
        # De vq pic
        indx = int(vq_img[i][j])
        row_code = li_code_book[indx].copy()
 
        for y in range(4):
            for x in range(4):
                de_vq_img[(i * 4)+y][(j * 4)+x] = row_code.pop(0)
        # soc
        m = i
        n = j - 1
        curr_pixl = vq_img[i][j]
        repeat_bag = []
        confict_pixel = False
        # print(curr_pixl)
        while n >= 0 and m >= 0 and n < vq_img_size_w and m < vq_img_size_h and not confict_pixel:
            if vq_img[m][n] not in repeat_bag:
                repeat_bag.append(vq_img[m][n])
                if vq_img[m][n] == curr_pixl:
                    confict_pixel = True

            cos_val = cos_sim([0, -1], [m - i, n - j])
            # print(i,j,m,n, cos_val)
            if abs(m-i) == abs(n-j): # 2 side conner
                if cos_val > 0: #left side
                    n = n +1 # go right
                else:
                    if m + 1 < i: # not = i pos
                        m = m + 1 # go down
                    else:
                        m = i
                        n = (j - (n - j)) - 1 #go to start up
            else:
                if cos_val > 0.7: #left side
                    m = m -1 # go up
                else:
                    if cos_val < 0.7 and cos_val > -0.7: #up side
                        n = n +1 # go right
                    else:
                        if m + 1 < i: # not = i pos
                            m = m + 1
                        else:
                            m = i
                            n = (j - (n - j)) - 1 #go to start up

        s = 0
        if len(secret) > 0:
            s = secret.pop(0)

        if not confict_pixel:
            embed = f'1{int(curr_pixl):08b}'
            vq_img_soc[i][j] = int(f'{embed}', 2)
            if s == 0:
                embed = f'011{int(curr_pixl):08b}' 
            # encode_str = encode_str + embed
            # vq_img_steg[i][j] = int(f'{embed}', 2)
        else:
            if len(repeat_bag) > 3:
                # as OIV
                embed = f'1{int(curr_pixl):08b}' 
                vq_img_soc[i][j] = int(f'{embed}', 2)
                if s == 0:
                    embed = f'011{int(curr_pixl):08b}' 
            else:
                no = repeat_bag.index(curr_pixl)
                embed = f'0{int(no):02b}'
                vq_img_soc[i][j] = int(f'{embed}', 2)
                if s == 1:
                    embed = f'1{int(curr_pixl):08b}'

            # no = repeat_bag.index(curr_pixl)
            # if len(repeat_bag) > max:
            #     max = len(repeat_bag)
            # # print(repeat_bag, len(repeat_bag))
            # embed = f'0{int(no):07b}'
            # vq_img_soc[i][j] = int(f'{embed}', 2)
            # if s == 1:
            #     embed = f'1{int(curr_pixl):08b}' 



        encode_str = encode_str + embed
        vq_img_steg[i][j] = int(f'{embed}', 2)
        

# print(1000, PSNR(vq_img_soc, vq_img_steg))


columns = 2
rows = 2
fig = plt.figure(figsize=(8, 8))

fig.add_subplot(rows, columns, 1)
plt.title('codebook picture',fontsize=12, color='#333333')
plt.imshow(img, cmap='gray')

fig.add_subplot(rows, columns, 2)
plt.title('original',fontsize=14, color='#333333')
plt.imshow(img2, cmap='gray')

# 
fig.add_subplot(rows, columns, 3)
plt.title('VQ index',fontsize=14, color='#333333')
# plt.text(20, 240, f'PSNR:{PSNR(img2, vq_img)}' ,fontsize=12, color='red', style='italic')
plt.imshow(vq_img, cmap='gray')

fig.add_subplot(rows, columns, 4)
plt.title('decompress',fontsize=14, color='#333333')
plt.text(15, 240, f'PSNR:{PSNR(img2, de_vq_img)}' ,fontsize=14, color='red', style='italic')
plt.imshow(de_vq_img, cmap='gray')

# fig.add_subplot(rows, columns, 1)
# plt.title(f'SOC img',fontsize=12, color='#333333')
# plt.imshow(vq_img_soc, cmap='gray')

# fig.add_subplot(rows, columns, 1)
# plt.title(f'SOC and Embed {sec_num}',fontsize=12, color='#333333')
# plt.text(10, 70, f'PSNR:{PSNR(vq_img, vq_img_steg)}' ,fontsize=14, color='red', style='italic')
# plt.imshow(vq_img_steg, cmap='gray')
plt.show()
