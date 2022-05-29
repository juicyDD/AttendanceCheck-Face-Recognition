import cv2, os, detection_recognition.head_pose as head_pose
from detection_recognition.inference import myInference
from detection_recognition.kmean_clustering import average_embeddings
import numpy as np
from detection_recognition.facemaskDetect import FacemaskDetect
import mediapipe as mp
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

# def getColorValue(myresult):
#     if myresult=='correct_mask':
#         return (0,255,0)
#     elif myresult=='incorrect_mask':
#         return (0,255,255)
#     else:
#         return (0,0,255)
# def attendance_check_stream(cap):
#     #----var
#     mp_facedetector = mp.solutions.face_detection
#     mp_facedetection = mp_facedetector.FaceDetection(min_detection_confidence=0.7)
    
#     fmd2 = FacemaskDetect(r'model/facemask_model_new.pb')
    
#     #----face recognition init
#     sess,tf_dict=model_restore_from_pb(pb_path,node_dict,GPU_ratio=None)
#     tf_input =tf_dict['input']
#     tf_phase_train=tf_dict['phase_train']
#     tf_embeddings = tf_dict['embeddings']
#     model_shape = tf_input.shape
#     print("The model shape of face recognition:",model_shape)
#     feed_dict ={tf_phase_train:False}
#     if 'keep_prob' in tf_dict.keys():
#         tf_keep_prob = tf_dict['keep_prob']
#         feed_dict[tf_keep_prob] =1.0
        
#     while(cap.isOpened()):
#         res=''
#         conf=''
#         ret,img =cap.read()#the original img with bgr format
        
#         if ret is True:
#             #----image processing
#             img = cv2.flip(img, 1) #flip img
#             img_rgb =cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             bboxes = mp_facedetection.process(img_rgb)
#             img_rgb = img_rgb.astype(np.float32)
#             img_rgb/=255
            
#             if bboxes.detections: #nếu detect được có khuôn mặt trong ảnh
#                 for num, detection in enumerate(bboxes.detections):
#                     bBox = detection.location_data.relative_bounding_box
#                     h, w, c = img.shape
#                     bBox.ymin=bBox.ymin-bBox.height*0.25 #modify the bounding box (padding)
#                     bBox.height=bBox.height*1.25
#                     bBox.xmin=bBox.xmin -bBox.width*0.05
#                     bBox.width=bBox.width*1.1
#                     bbox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)
                    
#                     img_temp = img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2]]
#                     res,conf =fmd2.detect(img_temp)
#                     color = getColorValue(res)
#                     cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[0]+bbox[2],bbox[1]+bbox[3]),color,2)
                    
#                     #FACE RECOGNITION
#                     name =""
#                     img_fr=img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2],:] #crop
#                     img_fr=cv2.resize(img_fr,(int(model_shape[2]),int(model_shape[1]))) #resize
#                     img_fr=np.expand_dims(img_fr,axis=0) #make 4 dimensions

#                     feed_dict[tf_input] = img_fr
#                     embeddings_tar=sess.run(tf_embeddings,feed_dict=feed_dict)
#                     feed_dict_2[tf_tar] = embeddings_tar[0]

#                     print(embeddings_tar[0])
#                     distance =sess_cal.run(tf_dis,feed_dict=feed_dict_2)
#                     arg =np.argmin(distance)

#                     if distance[arg]<threshold:
#                         name=paths[arg].split("\\")[-1].split(".")[0]
#                         print(name)
#                     cv2.putText(img, "%s: %s" % (str(res), str(name)),
#                                 (bbox[0] + 2, bbox[1] - 2),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
            
def stream(cap):
    posedict={"Looking up":0,"Looking down":0,"Looking left":0,"Looking right":0,"Forward":0}
  
    img = 0
    while(cap.isOpened()):
        ret,img =cap.read()
        
        if not ret:
            print("Error: failed to capture image")
            break
        # img_clone = img
        context = head_pose.headPose(img)
        if context == None:
            continue
        imageArray.append(img)
        coordinatesArray.append(context['coordinates'])
        print(context['pose'])
        posedict[context['pose']] +=1
        for key in posedict:
            if posedict[key]<=15:
                cv2.putText(img, key, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                break
            
        tempdict={k for k,v in posedict.items() if v>15}
        # print(tempdict)
        cv2.imshow('New Embeddings', img)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty('New Embeddings',cv2.WND_PROP_VISIBLE) < 1 or len(tempdict)==5:
            cap.release()
            cv2.destroyWindow('New Embeddings')
            infer = myInference()
            for img in imageArray:
                embeddings=infer.vectoring(img)
                embeddingsArray.append(embeddings)
            
            faceprints = average_embeddings(embeddingsArray,coordinatesArray)
            print("end")
            return faceprints
            #break
        
        
        
        
    


