import cv2

def screenshot(camera, nome):
    ret, frame = camera.read()
    if ret:
        cv2.imshow("Screenshot", frame)
        cv2.imwrite(f'images/{nome}.png', frame)
        return True
    return False 
