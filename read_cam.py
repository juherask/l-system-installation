import cv2
import os.path

def show_webcam(mirror=False):
    cam = cv2.VideoCapture(1)
    img_idx = 0
    while True:
        ret_val, img = cam.read()
        if mirror: 
            img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        
        key = cv2.waitKey(100)&255
        if key == 27: 
            break  # esc to quit
        if key == ord("p"):
            # press p to take a [p]icture and save it
            while True:
                imfile_name = "blocks%03d.png"%img_idx
                if not os.path.isfile(imfile_name):
                    break
                img_idx+=1
            cv2.imwrite(imfile_name,img)
            print "Stored image", imfile_name
    cv2.destroyAllWindows()

def main():
    show_webcam(mirror=True)

if __name__ == '__main__':
    main()
