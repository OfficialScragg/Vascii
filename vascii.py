#!/usr/share/env python3
# +-------------------------------------------------------------------------------------+
# | USAGE:                                                                              |
# |    python3 vascii.py <mode (0|1)> <scale (0.1:0.3)> <contrast (1:3)> <invert (0|1)> |
# +-------------------------------------------------------------------------------------+

# Imports
import cv2, time, sys, os, socket, threading

# Global variables and objects
scale = 0.15
contrast = 1
invert = 0
mode = 0
server_ip = "192.168.8.103"
cols = os.get_terminal_size().columns
bufferSize = 102400
send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
recv_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Main function
def main():
    # Set parameters from cmd arguments
    global invert, contrast, scale, cols
    if len(sys.argv) > 1:
        scale = float(sys.argv[1])
        if len(sys.argv) > 2:
            scale = float(sys.argv[2])
            if len(sys.argv) > 3:
                contrast = float(sys.argv[3])
                if len(sys.argv) > 4:
                    invert = float(sys.argv[4])

    # Connect to webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    # Set mode: Stream to server or local terminal
    if mode == 1:
        send_sock.connect((server_ip, 20001))
        recv_sock.connect((server_ip, 20002))

        # Start receiver thread
        receive = threading.Thread(target=recvStream, args=(1,))
        receive.start()
    
    # Processing loop
    while True:
        # Capture a frame from the webcam
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        width = len(frame[0])*2

        # Convert frame to greyscale
        gscale = []
        for b, i in enumerate(frame):
            for a, x in enumerate(i):
                sum = int(x[0])+int(x[1])+int(x[2])
                sum/=3
                sum*=contrast
                sum = int(sum)
                x = [sum, sum, sum]
                i[a] = x
                gscale.append(sum)
                gscale.append(sum)
            frame[b] = i
        img2ascii(gscale, width)
        cols = os.get_terminal_size().columns
        time.sleep(0.1)
        c = cv2.waitKey(1)
        if c == 27:
            break
    # Release the webcam
    cap.release()

# Convert greyscale pixel array to ascii string
def img2ascii(pixels, width):
    global invert, contrast, scale, cols
    # ASCII art charset
    chars = ["@", "$", "%", "#", "*", "+", "=", "-", ":", ".", " "]
    if invert == 1:
        chars.reverse()
    # Assigning a char to each pixel
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    # Padding to move the frame to the center of the terminal
    padding = " " * int(((cols-width)/2))
    new_pixels_count = len(new_pixels)
    # Construct the final frame string
    ascii_image = [padding+new_pixels[index:index + width] for index in range(0, new_pixels_count, width)]
    ascii_image = "\n".join(ascii_image)
    # Display or send
    if mode == 1:
        sendFrame("\r"+ascii_image)
    else:
        print("\r"+ascii_image)

# Send an ascii string image to server
def sendFrame(frame):
    global send_sock
    bytesToSend = str.encode(frame)
    send_sock.sendall(bytesToSend)

# Receive and display an ascii string image
def recvStream(self):
    global recv_sock
    while True:
        frame = recv_sock.recv(bufferSize)
        print(bytes.decode(frame))

if __name__ == "__main__":
    main()