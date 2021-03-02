import matplotlib.image as img
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2 as cv
from PIL import Image, ImageDraw

def readData():
    # Läs bild data
    fabio = img.imread("fabio64.png")
    poke = img.imread("kingler64x64.png")
    lenaRGB = img.imread("lenargba.png")
    hemlis = img.imread("Untitled.png")

    # Konvertera till np array
    np_fabio = np.array(fabio)
    np_poke = np.array(poke)
    np_lenaRGB = np.array(lenaRGB)
    np_hemlis = np.array(hemlis)

    # Return datan
    return np_fabio, np_poke, np_lenaRGB, np_hemlis

def pokemonImg(poke):
    # Multiplicerar med 255 för att konvertera till heltal eftersom PIL inte vill fungera 
    # med annat än 0-255 skalan
    d = np.int_(poke*255)

    # Sparar varje färg i sin egen variabel
    # Konverterar alltså varje färg till en luminens greyscale m.h.a PIL:s Image
    imgR = Image.fromarray(np.uint8(d[:,:,0]), 'L')
    imgG = Image.fromarray(np.uint8(d[:,:,1]), 'L')
    imgB = Image.fromarray(np.uint8(d[:,:,2]), 'L')

    # Returnerar datan
    return imgR, imgG, imgB

def fabioImg():
    # Öppnar Fabio bilden
    fab = Image.open('fabio64.png')
    # Skapar en ny bild med text och en alpha kanal
    hemlis = Image.new("RGBA", fab.size)
    hemlisDraw = ImageDraw.ImageDraw(hemlis, "RGBA")
    # Texten och dess position i bilden
    hemlisDraw.text((10,10), "Hemlis :)")
    # Skapar en mask en alpha värdet 15
    mask = hemlis.convert("L").point(lambda x: min(x, 15))
    # PIL har som tur ett verktyg för att använda en bild som alpha kanal till en annan bild
    hemlis.putalpha(mask)
    # Så paste vi den hemliga texten på ursprungliga Fabio bilden och sparar den
    fab.paste(hemlis, None, hemlis)
    fab.save("secretFabio.png", "PNG")
    
def soundWave(hz):
    # Sample rate 44100Hz
    Fs = 44100
    sample = 1
    # Frekvensen
    f = hz
    # Hur lång tonen är
    dur = 1
    x = np.linspace(0, dur, Fs * dur)
    # Räknar ut sinusvågen, gånger tonens längd
    y = np.sin(2 * np.pi * f * x)
    return x, y

# Hämtar viktiga variabler från readData()
fabio, poke, lenaRGB, hemlis = readData()

# Uppg1: C, E och G tonernas frekvens hittas på nätet
q, c = soundWave(262)
w, e = soundWave(327)
r, g = soundWave(392)
# Uppg1: Kombinerar de tre tonerna för att få ett C-accord
# Får inte detta steg att fungera. Tonerna adderas bara på varandra istället för efter
# varandra. Testade med append(), extend() och addition.
x = q + w + r
y = c + e + g

# Uppg1: Kombinera till em dataframe
z = pd.DataFrame({"1" : x, "2" : y})
# Uppg1: Konvertera till CSV
z.to_csv("chord.csv", index=False, sep=" ")
# Uppg1: Linjegrafen
plt.plot(x,y)
plt.show()

# Uppg2: Skickar datan (arrayn) från pokemon bilden till pokemon funktionen, returnerar luminens bilder
pokeUppgR, pokeUppgG, pokeUppgB = pokemonImg(poke)

# Uppg3: Kör fabioImg()
fabioImg()
# Uppg3: Öppna bilden som variabel
alphaFabio = img.imread("secretFabio.png")

# Uppg3: Before/after figur med originalet samt endast alpha kanalen
plt.figure()
x, ax = plt.subplots(2,1)
ax[0].imshow(alphaFabio)
ax[1].imshow(alphaFabio[:,:,3], vmin=0.5, vmax=0.98)
plt.show()

# Bonus: läser in bild data med opencv
histFab = cv.imread("secretFabio.png",0)
histOrig = cv.imread("fabio64.png",0)
# Bonus: Skapar histogrammet från bild-filen
hist,bins = np.histogram(histFab.flatten(),256,range=(0,255))
hist2,bins2 = np.histogram(histOrig.flatten(),256,range=(0,255))

# Skapar figuren
plt.figure()
# Histogram med alpha hemlisen
y, axis = plt.subplots(2,1)
axis[0].hist(histFab.flatten(),256,range=(0,255), color = 'r')
axis[0].legend(('New histogram'), loc = 'upper left')

# Histogram av ursprungliga bilden
axis[1].hist(histOrig.flatten(),256,range=(0,255), color = 'r')
axis[1].legend(('Original histogram'), loc = 'upper left')
plt.show()

# Uppg2: Kombinerar kanalerna m.h.a dstack
rgb = np.dstack((pokeUppgR, pokeUppgG, pokeUppgB))
plt.imsave("Combined_poke.png", rgb)

# Uppg2: Visa bilderna
# plt.imshow() lite krånglig på vscode, hittade inget lättare sätt att visa bilderna correct
plt.figure()
f, axarr = plt.subplots(4,1)

# Uppg2: Visar i ordningen Röd, Grön, Blå, Kombinerad
axarr[0].imshow(pokeUppgR, cmap='gray')
axarr[1].imshow(pokeUppgG, cmap='gray')
axarr[2].imshow(pokeUppgB, cmap='gray')
axarr[3].imshow(rgb)
plt.show()