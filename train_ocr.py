import cv2
import numpy as np
import sys

MAX_CHAR_SIZE_IN_PIX = 60
MIN_CHAR_NARROW_SIZE_IN_PIX = 10
MIN_CHAR_WIDE_SIZE_IN_PIX = 30


def threshold_img(blur):
    #ret,thresh = cv2.threshold(blur,60,255,cv2.THRESH_BINARY)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 27, 5) 
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    thresh = cv2.erode(thresh, kernel, iterations=2)
    return thresh
    
def boundig_square(brect):
    x,y,w,h = brect
    if w>h:
        sw = w
        sy = y-(sw-h)/2
        sx = x
    else:
        sw = h
        sx = x-(sw-w)/2
        sy = y
    return sx,sy,sw,sw
    
def teach_webcam():
    samples =  np.empty((0,100))
    rejected =  np.empty((0,100))
    responses = []
    exiting = False
        
    while True:
        cam = cv2.VideoCapture(1)
        ret_val, im = cam.read()
        cam.release()

        gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)
    
        thresh = threshold_img(blur)
        
        #out_gray = gray.copy()
        #cv2.imshow('norm',thresh)
        #key = cv2.waitKey(0)
        #sys.exit()
                    

        #################      Now finding Contours         ###################
        contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

        
        for cnt in contours:
            if cv2.contourArea(cnt)>50:
                brect = cv2.boundingRect(cnt)
                x,y,w,h = brect
                
                bsquare = boundig_square(brect)
                sx,sy,sw,sh = bsquare
                
                #feature = gray[sy:sy+sw, sx:sx+sw]
                #max_fw = np.max(feature)
                #feature_edges = cv2.Canny(feature,max_fw-20,max_fw)
                #borderism = np.count_nonzero(feature_edges)/float(sw*sw)
                #out_gray[sy:sy+sw, sx:sx+sw] = feature_edges
                
                large_enough = (w>MIN_CHAR_NARROW_SIZE_IN_PIX and
                               h>MIN_CHAR_NARROW_SIZE_IN_PIX)
                not_too_big = (w<MAX_CHAR_SIZE_IN_PIX and
                               h<MAX_CHAR_SIZE_IN_PIX)
                rect_letter = (w>MIN_CHAR_WIDE_SIZE_IN_PIX and
                               h<MIN_CHAR_WIDE_SIZE_IN_PIX)
                thin_horiz = (w>MIN_CHAR_WIDE_SIZE_IN_PIX and
                               h>MIN_CHAR_NARROW_SIZE_IN_PIX)
                thin_vert = (h>MIN_CHAR_WIDE_SIZE_IN_PIX and
                               w>MIN_CHAR_NARROW_SIZE_IN_PIX)
                if (large_enough and not_too_big) and\
                   (rect_letter or thin_horiz or thin_vert):
                    
                    #cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),2)
                    cv2.rectangle(im,(sx,sy),(sx+sw,sy+sh),(0,255,0),2)
                    
                    try:
                        roi = thresh[sy:sy+sh,sx:sx+sw]
                        roismall = cv2.resize(roi,(10,10))
                        cv2.imshow('norm',im)
                        key = cv2.waitKey(0)
                        
                        if key == 27:  # (escape to quit)
                            exiting = True
                            break
                        
                        if chr(key)!=" ":
                            print x,y,w,h,chr(key)
                                                        
                            if key>=48 and key<=122:
                                responses.append(ord(chr(key)))
                                sample = roismall.reshape((1,100))
                                samples = np.append(samples,sample,0)
                        else:
                            sample = roismall.reshape((1,100))
                            rejected = np.append(rejected,sample,0)
                            
                    except:
                        pass
        if exiting:
            break
            
    print "training complete"
    responses = np.array(responses,np.float32)
    responses = responses.reshape((responses.size,1))
    np.savetxt('rejected.data',rejected)
    np.savetxt('samples.data',samples)
    np.savetxt('responses.data',responses)
    sys.exit()
        

def main():
    teach_webcam()

if __name__ == '__main__':
    main()
