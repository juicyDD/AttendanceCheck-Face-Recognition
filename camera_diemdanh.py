import cv2, os, detection_recognition.head_pose as head_pose
from detection_recognition.inference import myInference
from detection_recognition.kmean_clustering import average_embeddings
import numpy as np
from detection_recognition.facemaskDetect import FacemaskDetect
import mediapipe as mp
import db
from camera_diemdanh import *
from detection_recognition.tools import model_restore_from_pb
imageArray=[]
coordinatesArray=[]
embeddingsArray=[]
facePrints=[]


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
    infer = myInference()
    img = 0
    sinhviencomat = []
    infer.distance_calculate_init(embeddings_ref=embeddings_ref)
    while(cap.isOpened()):
        ret,img =cap.read()
        
        if not ret:
            print("Error: failed to capture image")
            break
        
        embeddings=infer.vectoring(img)
        print(embeddings)
        cv2.imshow('Diem danh', img)
        arg = -1
        arg = infer.distance_calculate(img)
        print(arg)
        mssv_recognized = vectordactrung_theolop[arg][2]
        print(mssv_recognized)
        sinhviencomat.append(mssv_recognized)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty('Diem danh',cv2.WND_PROP_VISIBLE) < 1:
            sinhviencomat = set(sinhviencomat)
            for sv in sinhviencomat:
                db.update_diemdanh(db.connect(),sv,lophp, buoihoc)
                print('Sinh vien co mat: ',sv)
                return
            cap.release()
            cv2.destroyWindow('Diem danh')
            
            
            
        
        

        
    


