from PIL import Image
import os

# ls assets | awk '{print "assets/"$1"/logo.png"}' | xargs file

for address in os.listdir('assets'):
    # print(address)
    file = 'assets/' + address + '/logo.png'
    img = Image.open(file)
    a, b = img.size
    if a != b:
        print(a, b)
    # img = img.resize((256, 256), Image.ANTIALIAS)
    # img.save(file)
    if address == 'EQAS2elYb6_hqWyOl7gpuYTzf1sqmjLJQ0lQ4X_4d_MvtMWR':
        img.save('logo.jpg', optimize=True, quality=25)
    img.close()

    img = Image.open('logo.jpg')
    img.save('logo.png')