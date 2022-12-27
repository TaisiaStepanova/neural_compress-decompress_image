from PIL import Image
import random
import json
import pickle
import copy

def get_data_img(img):
    pixelData = img.getdata()
    pixels = list(pixelData)
    for i in range(len(pixels)):
        pixels[i] = list(pixels[i])
    return pixels

def set_data_img(img, pixels, h, w):
    for i in range(len(pixels)):
        pixels[i] = tuple(pixels[i])
    for i in range(0, (h * w)):
        img.putpixel((i % w, i // w), pixels[i])

def init_matrix(p, n , m):
    W = [[random.randint(-1, 1)/100 for j in range(p)] for i in range(n * m * 3)]
    return W

def transp(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]

def multipl(A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    rows_B = len(B)
    cols_B = len(B[0])
    try:
        C = [[0 for row in range(cols_B)] for col in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    C[i][j] += A[i][k] * B[k][j]
        return C
    except IndexError:
        print("Cannot multiply the two matrices. Incorrect dimensions")

def color_conv(color):
    return (2*color/255) - 1

def rev_color_conv(color):
    return 255*(color + 1)/2

def data_to_refer(A, n, m, h, w):
    refer_v = []
    L = (h//n)*(w//m)
    for i in range(L):
        row = i//(w//m)
        col = i % (w//m)
        X = []
        for j in range(row * n, row * n + n):
            for k in range(col * m, col * m + m):
                for a in range(3):
                    #value = A[j * w + k][a]
                    value = color_conv(A[j*w + k][a])
                    X.append([value])
        refer_v.append(X)
    return refer_v

def refer_to_data(A, n, m, h, w):
    data = [[0 for row in range(3)] for col in range(int(h*w))]
    x = -1
    for i in range(h // m):
        for j in range(w // n):
            y = 0
            x = x + 1
            for a in range(i * m, i * m + m):
                for b in range(j * n, j * n + n):
                    for z in range(3):
                        data[a*w + b][z]= int(rev_color_conv(A[x][y][0]))
                        y = y + 1
    return data

def delta(m1, m2):
    return [[m1[i][j] - m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]

def count_error(delta_x):
    result = 0
    for i in range(len(delta_x[0])):
        result = result + delta_x[0][i] * delta_x[0][i]
    return result

def alpha_matrix(matrix, alpha):
    return [[alpha * matrix[i][j] for j in range(len(matrix[0]))] for i in range(len(matrix))]

def sum_error(E):
    result = 0
    for i in range(len(E)):
        result = result + E[i]
    return result

def set_data_in_file(n, m, p, w1, w2):
    with open('data.json', 'w', encoding="utf-8") as w:
        temp_dict = {"n": n, "m": m, "neurons": p, "w1": w1, "w2": w2}
        json.dump(temp_dict, w, indent=2)

def get_data_from_file():
    with open('data_600.json', 'r', encoding="utf-8") as file:
        info = json.load(file)
        return info['n'], info['m'], info['neurons'], info['w1'], info['w2']

def training(image, n, m, p, height, width, e, alpha):
    W1 = init_matrix(p, n, m)
    W2 = transp(W1)
    img = data_to_refer(get_data_img(image), n, m, height, width)
    E = [999999]
    counter = 0
    while sum_error(E) > e:
        E = []
        counter += 1
        for i in range(int(height / n * width / m)):
            X = transp(img[i])
            Y = (multipl(X, W1))
            result = multipl(Y, W2)
            delta_x = delta(result, X)
            buffer = copy.deepcopy(W2)
            W2 = delta(W2, alpha_matrix(multipl(transp(Y), delta_x), alpha))
            W1 = delta(W1, alpha_matrix(multipl(transp(X), multipl(delta_x, transp(buffer))), alpha))
            E.append(count_error(delta_x))
        print("Step " + str(counter) + '\n')
        print(sum_error(E))
    set_data_in_file(n, m, p, W1, W2)

def compress(filename):
    n, m, p, W1, W2 = get_data_from_file()
    image = Image.open('img/' + filename)
    width, height = image.size
    img = data_to_refer(get_data_img(image), n, m, height, width)
    compress_img = []
    for i in range(int(height / n * width / m)):
        X = transp(img[i])
        Y = (multipl(X, W1))
        compress_img.append(Y)
    with open('compress_img.bin', "wb") as file:
        pickle.dump([compress_img, width, height], file)
    print("End")

def decompress(filename):
    width, height, Y = [], [], []
    with open("compress/" + filename, "rb") as file:
        data = pickle.load(file)
        Y = data[0]
        width = data[1]
        height = data[2]
    n, m, p, W1, W2 = get_data_from_file()
    new_img = []
    for i in range(int(height / n * width / m)):
        result = multipl(Y[i], W2)
        new_img.append(transp(result))

    img_new = refer_to_data(new_img, n, m, height, width)
    result = Image.new("RGB", (width, height), "#FF0000")
    set_data_img(result, img_new, height, width)
    result.show()