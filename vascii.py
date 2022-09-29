#!/usr/bin/env python3
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
server_ip = "127.0.0.1"
cols = os.get_terminal_size().columns
rows = os.get_terminal_size().lines
paddingSize = 10
remoteCols = 100
remoteRows = 70
bufferSize = 102400
send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
recv_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Main function
def main():
    # Set parameters from cmd arguments
    global invert, contrast, scale, cols, rows, mode, remoteCols, remoteRows, paddingSize
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])
        if len(sys.argv) > 2:
            scale = float(sys.argv[2])
            if len(sys.argv) > 3:
                contrast = float(sys.argv[3])
                if len(sys.argv) > 4:
                    invert = int(sys.argv[4])

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

        # Adjust remote stream scale
        adjustScale()
    
    # Processing loop
    while True:
        # Capture a frame from the webcam
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        width = len(frame[0])*2
        height = len(frame)

        if mode == 1:
            if (width > remoteCols) or (height > remoteRows):
                scale-=0.005
            elif ((width < remoteCols) or (height < remoteRows)) and not ((width == remoteCols) or (height == remoteRows)):
                scale+=0.05
        else:
            if (width > cols) or (height > rows):
                scale-=0.005
            elif ((width < cols) or (height < rows)) and not ((width == cols) or (height == rows)):
                scale+=0.05

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
        if mode == 1:
            if cols != os.get_terminal_size().columns:
                cols = os.get_terminal_size().columns
                rows = os.get_terminal_size().lines
                adjustScale()
        else:
            if cols != os.get_terminal_size().columns:
                cols = os.get_terminal_size().columns
                rows = os.get_terminal_size().lines
        time.sleep(0.1)
        c = cv2.waitKey(1)
        if c == 27:
            break
    # Release the webcam
    cap.release()

# Convert greyscale pixel array to ascii string
def img2ascii(pixels, width):
    global invert, contrast, scale, cols, mode, rows, remoteCols, remoteRows, paddingSize
    # ASCII art charset
    chars = ["@", "%", "&", "$", "#", "+", "=", "-", ":", ".", " "]
    if invert == 1:
        chars.reverse()
    # Assigning a char to each pixel
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    # Padding to move the frame to the center of the terminal
    if mode == 0:
        paddingSize = int(((cols-width)/2))
    else:
        paddingSize = int(((remoteCols-width)/2))
    padding = " " * paddingSize
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

# Adjust scale
def adjustScale():
    global send_sock, cols, rows
    scaleMsg = str.encode("ROWS "+str(rows)+" COLS "+str(cols)+"|")
    send_sock.sendall(scaleMsg)

# Receive and display an ascii string image
def recvStream(self):
    global recv_sock, remoteRows, remoteCols
    while True:
        frame = recv_sock.recv(bufferSize)
        data = frame.decode('utf-8')
        if data[0:4] == "ROWS":
            arr = data.split("|")
            info = data.split(" ")
            remoteRows = int(info[1])
            remoteCols = int(info[3].split("|")[0])
            frame = arr[1]
            print('rows:', remoteRows, ' cols:', remoteCols)
            print(frame)
        else:
            print(data)

if __name__ == "__main__":
    main()