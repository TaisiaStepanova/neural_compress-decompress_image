from PIL import Image
from lib import *
import pickle
import os

if __name__ == '__main__':
    print("----------MENU----------")
    print("1) Training\n2) Comress\n3) Decompress\n")
    menu = input("Enter number: ")

    if menu == '1':

        alpha = 0.001
        # считывание файлов
        print('Filename: ')
        for filename in os.listdir("img"):
            if filename != '.ipynb_checkpoints':
                print('- ', filename)
        filename = input()

        image = Image.open('img/' + filename)
        width, height = image.size
        print('Please, enter size of blocks: ')
        m = int(input('width=height: '))
        n = m
        if m > width or n > height or width%m!=0 or height%n!=0 :
            print('Error')
            m = int(input('width=height: '))
            n = int(m)

        p = int(input('Count of neurons: '))
        e = int(input('Enter error: '))

        training(image, n, m, p, height, width, e, alpha)

    elif menu == '2':
        print('Enter filename: ')
        for filename in os.listdir("img"):
            if filename != '.ipynb_checkpoints':
                print('- ', filename)
        filename = input()

        compress(filename)

    elif menu == '3':
        print('Enter filename: ')
        for filename in os.listdir("compress"):
            if filename != '.ipynb_checkpoints':
                print('- ', filename)
        filename = input()

        decompress(filename)