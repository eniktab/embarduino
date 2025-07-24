#!/usr/bin/env python3
import serial
import numpy as np
import cv2
import time
import struct
import os

# ───────────────── CONFIG ──────────────────
PORT            = '/dev/ttyACM0'    # adjust as needed
BAUDRATE        = 115200
WIDTH, HEIGHT   = 176, 144          # QCIF
BYTES_PER_PIXEL = 2
FRAME_SIZE      = WIDTH * HEIGHT * BYTES_PER_PIXEL
SAVE_DIR        = 'captures'        # where to dump saved frames

# make sure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ───────────────── SETUP SERIAL ──────────────────
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)             # allow Arduino to reset
ser.reset_input_buffer()  # drop any old data

try:
    while True:
        raw = ser.read(FRAME_SIZE)
        if len(raw) < FRAME_SIZE:
            # incomplete frame, skip
            continue

        # allocate empty BGR image
        image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # parse RGB565 stream
        for i in range(0, FRAME_SIZE, 2):
            two_bytes = raw[i:i+2]
            pixel = struct.unpack('>H', two_bytes)[0]
            r5 = (pixel >> 11) & 0x1F
            g6 = (pixel >>  5) & 0x3F
            b5 =  pixel        & 0x1F
            r8 = (r5 << 3) | (r5 >> 2)
            g8 = (g6 << 2) | (g6 >> 4)
            b8 = (b5 << 3) | (b5 >> 2)
            idx = i // 2
            y = idx // WIDTH
            x = idx %  WIDTH
            image[y, x] = (b8, g8, r8)

        # display live video
        cv2.imshow('OV7675 Live', image)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # quit on 'q'
            break
        elif key == ord('s'):
            # save on 's'
            ts = time.strftime('%Y%m%d_%H%M%S')
            fname = f'frame_{ts}.png'
            path = os.path.join(SAVE_DIR, fname)
            cv2.imwrite(path, image)
            print(f'[+] Saved frame to {path}')

finally:
    ser.close()
    cv2.destroyAllWindows()
