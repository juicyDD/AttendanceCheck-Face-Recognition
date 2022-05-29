from detection_recognition.tools import model_restore_from_pb
import cv2
import numpy as np
import mediapipe as mp
class myInference:
    def __init__(self):
        self.pb_path = r"E:\Aa_CodePractice\Python\py-desktop-app\model\pb_model.pb"

        self.node_dict={'input':'input:0',
            'keep_prob':'keep_prob:0',
            'phase_train': 'phase_train:0',
            'embeddings' : 'embeddings:0' }

        self.batch_size = 32
        self.sess,self.tf_dict=model_restore_from_pb(self.pb_path,self.node_dict,GPU_ratio=None)
        
        self.tf_input =self.tf_dict['input']
        self.tf_phase_train=self.tf_dict['phase_train']
        self.tf_embeddings = self.tf_dict['embeddings']
        
        self.model_shape = self.tf_input.shape
        print("The model shape of face recognition:",self.model_shape)
        
        self.feed_dict ={self.tf_phase_train:False} #không phải phase train liuliu
        if 'keep_prob' in self.tf_dict.keys(): #nếu trong model dictionary có param keep_prob (dropout tránh overfit) thì set = 1 (không dropout lun)
            tf_keep_prob = self.tf_dict['keep_prob']
            self.feed_dict[tf_keep_prob] =1.0
            
        self.mp_facedetector = mp.solutions.face_detection
        self.mp_facedetection = self.mp_facedetector.FaceDetection(min_detection_confidence=0.7)
        
    def vectoring(self,img):
        img_rgb =cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        bboxes = self.mp_facedetection.process(img_rgb)
        img_rgb = img_rgb.astype(np.float32)
        img_rgb/=255
        
        if bboxes.detections: #nếu detect được khuôn mặt
            for num, detection in enumerate(bboxes.detections):
                   #print(num,detection)
                bBox = detection.location_data.relative_bounding_box

                h, w, c = img.shape
                bBox.ymin=bBox.ymin-bBox.height*0.25 #padding đó 
                bBox.height=bBox.height*1.25 #padding đó 
                bBox.xmin=bBox.xmin -bBox.width*0.05 #padding đó 
                bBox.width=bBox.width*1.1 #padding đó 
                bbox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)

                 #crop và resize cho vừa vứi input của model
                img_fr=img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2],:] #crop
                img_fr=cv2.resize(img_fr,(int(self.model_shape[2]),int(self.model_shape[1]))) #resize
                img_fr=np.expand_dims(img_fr,axis=0) #make 4 dimensions
                
                self.feed_dict[self.tf_input] = img_fr
                embeddings_tar=self.sess.run(self.tf_embeddings,feed_dict=self.feed_dict)
                print(embeddings_tar[0])
                return embeddings_tar[0]
