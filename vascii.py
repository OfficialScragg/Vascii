import cv2, time, sys, os
from PIL import Image
 
# USAGE: python3 vascii.py <scale (0.1:0.3)> <contrast (1:3)> <invert (0|1)>

# Variables
scale = 0.15
contrast = 1
invert = 0
cols = os.get_terminal_size().columns
 
if len(sys.argv) > 1:
    scale = float(sys.argv[1])
    if len(sys.argv) > 2:
        contrast = float(sys.argv[2])
        if len(sys.argv) > 3:
            invert = float(sys.argv[3])

 
cap = cv2.VideoCapture(0)
 
def img2ascii(pixels, width):
    chars = ["@", "$", "%", "#", "*", "+", "=", "-", ":", ".", " "]
    if invert == 1:
        chars.reverse()
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    padding = " " * int(((cols-width)/2))
    new_pixels_count = len(new_pixels)
    ascii_image = [padding+new_pixels[index:index + width] for index in range(0, new_pixels_count, width)]
    ascii_image = "\n".join(ascii_image)
    print("\r"+ascii_image)
 
# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")
 
while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    width = len(frame[0])*2
    gscale = []
    for b, i in enumerate(frame):
        meh = []
        for a, x in enumerate(i):
            sum = int(((x[0] + x[1] + x[2])/3)*contrast)
            x = [sum, sum, sum]
            i[a] = x
            gscale.append(sum)
            gscale.append(sum)
        frame[b] = i
    #cv2.imshow('Input', frame) # Used to show webcam output in a little window.
    img2ascii(gscale, width)
    cols = os.get_terminal_size().columns
    time.sleep(0.1)
    c = cv2.waitKey(1)
    if c == 27:
        break
 
cap.release()
cv2.destroyAllWindows()