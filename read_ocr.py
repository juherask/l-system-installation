import cv2
import numpy as np
from train_ocr import threshold_img, boundig_square

from sklearn.ensemble import RandomForestClassifier

MAX_CHAR_SIZE_IN_PIX = 60
MIN_CHAR_NARROW_SIZE_IN_PIX = 10
MIN_CHAR_WIDE_SIZE_IN_PIX = 30

#######   training part    ############### 
samples = np.loadtxt('first/samples.data',np.float32)
rejected = np.loadtxt('first/rejected.data',np.float32)
responses = np.loadtxt('first/responses.data',np.float32)
responses = responses.reshape((responses.size,1))

reject_samples = np.append(samples, rejected)
reject_labels = np.zeros(len(reject_samples))
reject_labels[len(reject_samples):] = 1
reject_model = cv2.KNearest()
reject_model.train(samples,responses)

ocr_model = cv2.KNearest()
ocr_model.train(samples,responses)

ocr_clf = RandomForestClassifier(max_depth=2, random_state=0)
ocr_clf.fit(samples, responses)

############################# testing part  #########################

cam = cv2.VideoCapture(1)    
ret_val, im = cam.read()
out = np.zeros(im.shape,np.uint8)
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
thresh = threshold_img(gray)

contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if cv2.contourArea(cnt)>50:
        brect = cv2.boundingRect(cnt)
        x,y,w,h = brect
        
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
            
            bsquare = boundig_square(brect)
            sx,sy,sw,sh = bsquare
                
            #cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.rectangle(im,(sx,sy),(sx+sw,sy+sh),(0,255,0),2)
            
            try:
                roi = thresh[sy:sy+sh,sx:sx+sw]
                roismall = cv2.resize(roi,(10,10))
                roismall = roismall.reshape((1,100))
                roismall = np.float32(roismall)
                
                #retval, results, neigh_resp, dists = reject_model.find_nearest(roismall, k = 1)
                #if results[0][0]==1.0:                
                #retval, results, neigh_resp, dists = ocr_model.find_nearest(roismall, k = 1)
                #string = chr(int((results[0][0])))
                
                string = chr(int((ocr_clf.predict(roismall))))
                cv2.putText(out,string,(x,y+h),0,1,(0,255,0))
            except:
                print "pass"
                

cv2.imshow('im',im)
cv2.imshow('out',out)
cv2.waitKey(0)
