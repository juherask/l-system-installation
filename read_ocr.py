import cv2
import numpy as np
from train_ocr import threshold_img, bounding_square, is_candidate_number_contour
from os import path
from collections import OrderedDict

from sklearn.ensemble import RandomForestClassifier

MAX_CHAR_SIZE_IN_PIX = 60
MIN_CHAR_NARROW_SIZE_IN_PIX = 10
MIN_CHAR_WIDE_SIZE_IN_PIX = 30

# if none, use camera
img_source_folder = None
img_source_folder = "trainingdata"

label_map = {
    "n":"",
    "9":">",
    "8":"<",
    "i":"F",
    "f":"-",
    "e":"-",
    "x":"+",
    "z":"+",
    "p":"X"
}


def create_block_classifier_model():
    #######   training part    ############### 
    samples = np.loadtxt('tietoprovinssi2/samples.data',np.float32)
    rejected = np.loadtxt('tietoprovinssi2/rejected.data',np.float32)
    responses = np.loadtxt('tietoprovinssi2/responses.data',np.float32)
    responses = responses.reshape((responses.size,1))

    #reject_samples = np.append(samples, rejected)
    #reject_labels = np.zeros(len(reject_samples))
    #reject_labels[len(reject_samples):] = 1

    #reject_clf = RandomForestClassifier(max_depth=5, random_state=0)
    #reject_clf.fit(samples, responses)

    #ocr_model = cv2.KNearest()
    #ocr_model.train(samples,responses)

    ocr_clf = RandomForestClassifier(max_depth=5, random_state=0)
    ocr_clf.fit(samples, responses)
    
    return ocr_clf 

def detect_from_image(img, ocr_clf):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh = threshold_img(gray)

    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for cnt in contours:
        if is_candidate_number_contour(cnt):
            brect = cv2.boundingRect(cnt)
            bsquare = bounding_square(brect)
            sx,sy,sw,sh = bsquare
            
            #cv2.rectangle(im,(sx,sy),(sx+sw,sy+sh),(0,255,0),2)
            
            try:
                roi = thresh[sy:sy+sh,sx:sx+sw]
                roismall = cv2.resize(roi,(10,10))
                roismall = roismall.reshape((1,100))
                roismall = np.float32(roismall)
                
                string = chr(int((ocr_clf.predict(roismall))))
                results.append( (sx+sw/2, sy+sh/2, string) ) 
            except:
                pass
    return results

def detection_results_to_rules(detection_results):
    detection_results.sort()
    rows = []
    for r in detection_results:
        x,y,s = r
        
        # not a char
        if s == "n":
            continue
        
        #check which row
        row_it_belongs_to = None
        for row in rows:
            row_y, row_l = row
            if abs(row_y-y)<MAX_CHAR_SIZE_IN_PIX:
                row_it_belongs_to = row
                break
        
        if not row_it_belongs_to:
            rows.append(  [y, [r]] )
        else:
            row_it_belongs_to[1].append(r)
            row_it_belongs_to[0] = sum(lr[1] for lr in row_it_belongs_to[1])\
                                   /float(len(row_it_belongs_to[1]))
    
    rows.sort()
    
    rules = OrderedDict()
    start = None
    for _, row_l  in rows:
        if len(row_l)==1:
            start = label_map[row_l[0][2]]
        else:
            _,_,first_s=row_l[0]
            rule_from = label_map[first_s]
            rule_to = "".join(label_map[s] for _,_,s in row_l[1:])
            
            if rule_from in rules:
                print "Warning, ruleset already has the key %s with string %s", (rule_from, rule_to)
            
            rules[rule_from]=rule_to
            if start == None:
                start = rule_from
    return start, rules
    
############################# testing part  #########################

def main():
    if img_source_folder!=None:
        import glob
        img_file_names = list(glob.glob(path.join(img_source_folder,'*')))
        img_file_names.sort()
        img_file_idx = 0

    ocr_clf = create_block_classifier_model()


    while True:
        
        if img_source_folder==None:
            cam = cv2.VideoCapture(1)
            ret_val, im = cam.read()
            cam.release()
        else:
            img_file_idx+=1
            if img_file_idx==len(img_file_names):
                img_file_idx = 0
            im = cv2.imread(img_file_names[img_file_idx])
            
        out = np.zeros(im.shape,np.uint8)
        
        detection_results = detect_from_image(im, ocr_clf)
        for x,y,s in detection_results:
            cv2.putText(out,s,(x,y),0,1,(0,255,0))    
        start, rules = detection_results_to_rules(detection_results)
        print "start", start
        for rule_from, rule_to in rules.items():
            print rule_from, ":", rule_to 
        
            
        cv2.imshow('im',im)
        cv2.imshow('out',out)
        key = cv2.waitKey(0) & 255
        if key==27:
            break

if __name__=="__main__":
    main()
