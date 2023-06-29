import os

for num in "a23456789tjqk":
    for suit in "shdc":
        filename = num + suit
        os.system("inkscape " + filename +
                  ".svg -w 357 -h 499 -o ../card/" + filename + ".png")

os.system("inkscape back.svg -w 357 -h 499 -o ../card/back.png")

# os.system("inkscape kc.svg -w 357 -h 499 -o ../card/kc.png")
# os.system("inkscape kd.svg -w 357 -h 499 -o ../card/kd.png")
# os.system("inkscape kh.svg -w 357 -h 499 -o ../card/kh.png")
# os.system("inkscape ks.svg -w 357 -h 499 -o ../card/ks.png")
