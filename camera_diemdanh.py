import cv2, os, detection_recognition.head_pose as head_pose
from detection_recognition.inference import myInference
from detection_recognition.kmean_clustering import average_embeddings
import numpy as np
from detection_recognition.facemaskDetect import FacemaskDetect
import mediapipe as mp
import db
from camera_diemdanh import *
from detection_recognition.tools import model_restore_from_pb
from email_sender.emailsender import EmailSender
imageArray=[]
coordinatesArray=[]
embeddingsArray=[]
facePrints=[]
'''
Camera stream
Author: Uyen Nhi
Created: May 2022
'''
def camera_init(camera_source=0,resolution="480"):
    global imageArray, coordinatesArray, embeddingsArray, facePrints
    imageArray=[]
    coordinatesArray=[]
    embeddingsArray=[]
    facePrints=[]
    
    resolution_dict ={"480":[480,640],"720":[720,1280],"1080":[1080,1920]}
    cap = cv2.VideoCapture(camera_source)

    #----resolution decision
    if resolution in resolution_dict.keys():
        width = resolution_dict[resolution][1]
        height = resolution_dict[resolution][0]
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    else:
        height=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width =cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        
    return cap, height, width

            
def stream(cap,embeddings_ref,vectordactrung_theolop,lophp, buoihoc):
    my_email_sender =EmailSender()
    infer = myInference()
    
    #fmd2 = FacemaskDetect(r'model\facemask_model_new.pb')
    fmd2 = FacemaskDetect(r'model\facemask_model_3_layers_32-64-128_rm_outliers.pb')
    
    img = 0
    sinhviencomat = []
    infer.distance_calculate_init(embeddings_ref=embeddings_ref)
    while(cap.isOpened()):
        ret,img =cap.read()
        ini_img = img
        if not ret:
            print("Error: failed to capture image")
            break
        # try: 
        embeddings,bbox=infer.vectoring(img)
        
        if bbox is None: 
            cv2.imshow('Diem danh',ini_img)
            
            print(bbox)
            continue
        # except:
        #     cv2.imshow('Diem danh',ini_img)
        #     continue
        
        img_rgb =cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img_rgb = img_rgb.astype(np.float32)
        # img_rgb/=255
        img_temp = img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2]]
        img_temp = img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2]]
        res,conf =fmd2.detect(img_temp)
        print(res)
        color = getColorValue(res)
        cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[0]+bbox[2],bbox[1]+bbox[3]),color,2)
        
        print(embeddings)
        
        arg = -1
        arg = infer.distance_calculate(img)
        print(arg)
        if arg!=-1:
            mssv_recognized = vectordactrung_theolop[arg][2]
        else:
            mssv_recognized='Undefined'
        print(res)
        print(mssv_recognized)
        if mssv_recognized!='Undefined':
            sinhviencomat.append(mssv_recognized)
        cv2.putText(img, "%s: %s" % (str(res), str(mssv_recognized)),
            (bbox[0] + 2, bbox[1] - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
        cv2.imshow('Diem danh', img) 
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty('Diem danh',cv2.WND_PROP_VISIBLE) < 1:
            # my_email_sender.sendEmail("aloooooo","ongnguyenuyennhi@gmail.com")
            if sinhviencomat is not None:
                sinhviencomat_set = set(sinhviencomat)
                for sv in sinhviencomat_set:
                    number_of_frames = sinhviencomat.count(sv)
                    if number_of_frames > 5:
                        db.update_diemdanh(db.connect(),sv,lophp, buoihoc)
                        print('MSSV ',sv,'có mặt')
                        my_email_sender.sendEmail(sv,lophp,buoihoc,db.getEmailSV(db.connect(),sv))
            my_email_sender.server.quit()
            return
            cap.release()
            cv2.destroyWindow('Diem danh')
    # cv2.imshow('Diem danh', img) 
            
def getColorValue(myresult):
    if myresult=='correct_mask':
        return (0,255,0)
    elif myresult=='incorrect_mask':
        return (0,255,255)
    else:
        return (0,0,255)
            
        
        

        
    


