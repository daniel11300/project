import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    array1 = ''

    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]
    result,encimg=cv2.imencode('.jpg',gray,encode_param)
    file_bytes = np.asarray(bytearray(frame), dtype=np.uint8)
    decoded = cv2.imdecode(encimg, 1)

    # Display the resulting frame
    cv2.imshow('frame',decoded)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()