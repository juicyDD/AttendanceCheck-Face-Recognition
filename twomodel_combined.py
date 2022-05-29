import time, math
import numpy as np
import cv2,os
from detection_recognition.tools import model_restore_from_pb
import tensorflow.compat.v1 as tf
from detection_recognition.facemaskDetect import FacemaskDetect
import mediapipe as mp
tf.disable_v2_behavior()

img_format={'png','jpg','bmp'}

def video_init(camera_source=0,resolution="480",to_write=False,save_dir=None):
    #----var
    writer = None
    resolution_dict ={"480":[480,640],"720":[720,1280],"1080":[1080,1920]}

    #----camera source connection
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

    if to_write is True:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        save_path = 'demo.avi'
        if save_dir is not None:
            save_path = os.path.join(save_dir,save_path)
        writer = cv2.VideoWriter(save_path,fourcc,30,(int(width),int(height)))

    return cap,height,width,writer

def stream(pb_path,node_dict,ref_dir,camera_source=0,resolution="480",to_write=False,save_dir=None):

    #----var
    mp_facedetector = mp.solutions.face_detection
    mp_facedetection = mp_facedetector.FaceDetection(min_detection_confidence=0.7)

    # fmd2 = FacemaskDetect(r'facemask_model2.pb')
    fmd2 = FacemaskDetect(r'model\facemask_model_new.pb')

    frame_count = 0
    FPS = "loading"
    face_mask_model_path =r'face_mask_detection.pb'
    margin = 40
    batch_size=32
    threshold=0.8
    #----video streaming initialization
    cap,height,width,writer = video_init(camera_source=camera_source,resolution=resolution,to_write=to_write,save_dir=save_dir)

    #----face recognition init
    sess,tf_dict=model_restore_from_pb(pb_path,node_dict,GPU_ratio=None)
    tf_input =tf_dict['input']
    tf_phase_train=tf_dict['phase_train']
    tf_embeddings = tf_dict['embeddings']
    model_shape = tf_input.shape
    print("The model shape of face recognition:",model_shape)
    feed_dict ={tf_phase_train:False}
    if 'keep_prob' in tf_dict.keys():
        tf_keep_prob = tf_dict['keep_prob']
        feed_dict[tf_keep_prob] =1.0
    #----read images from the database
    d_t = time.time()
    paths=[file.path for file in os.scandir(ref_dir) if file.name[-3:] in img_format]
    len_ref_path = len(paths)
    if len_ref_path == 0:
        print("No images in ",ref_dir)
    else:
        ites = math.ceil(len_ref_path/batch_size)
        embeddings_ref = np.zeros([len_ref_path,tf_embeddings.shape[-1]],dtype=np.float32)

        for i in range(ites):
            num_start = i * batch_size
            num_end = np.minimum(num_start+batch_size,len_ref_path)

            batch_data_dim =[num_end - num_start]
            batch_data_dim.extend(model_shape[1:])
            batch_data= np.zeros(batch_data_dim,dtype = np.float32)

            for idx,path in enumerate(paths[num_start:num_end]):
                img = cv2.imread(path)
                if img is None:
                    print("read failed:",path)
                else:
                    img = cv2.resize(img,(int(model_shape[2]),int(model_shape[1])))
                    img = img[:,:,::-1] #change color format
                    batch_data[idx] = img
            batch_data/=255
            feed_dict[tf_input] = batch_data

            embeddings_ref[num_start:num_end] = sess.run(tf_embeddings,feed_dict=feed_dict)
        d_t=time.time()-1

        print("ref embedding shape",embeddings_ref.shape)
        print("It takes {} secs to get {} embeddings".format(d_t,len_ref_path))

    #tf setting for calculating distance
    if len_ref_path > 0:
        with tf.Graph().as_default():
            tf_tar = tf.placeholder(dtype=tf.float32, shape =tf_embeddings.shape[-1])
            tf_ref = tf.placeholder(dtype=tf.float32,shape =tf_embeddings.shape)
            tf_dis=tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(tf_ref,tf_tar)),axis=1))

            #GPU setting
            config = tf.ConfigProto(log_device_placement = True,
                                    allow_soft_placement = True)
            config.gpu_options.allow_growth = True
            sess_cal = tf.Session(config=config)
            sess_cal.run(tf.global_variables_initializer())
        feed_dict_2 ={tf_ref : embeddings_ref}
    #----get 1 img
    while(cap.isOpened()):
        res=''
        conf=''
        ret,img =cap.read()#the original img with bgr format

        if ret is True:

            #----image processing
            img_rgb =cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            bboxes = mp_facedetection.process(img_rgb)
            img_rgb = img_rgb.astype(np.float32)
            img_rgb/=255

            # if len(bboxes) >0:
            if bboxes.detections:
                for num, detection in enumerate(bboxes.detections):

                    #print(num,detection)
                    bBox = detection.location_data.relative_bounding_box

                    h, w, c = img.shape
                    bBox.ymin=bBox.ymin-bBox.height*0.25
                    bBox.height=bBox.height*1.25
                    bBox.xmin=bBox.xmin -bBox.width*0.05
                    bBox.width=bBox.width*1.1
                    bbox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)

                    img_temp = img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2]]
                    res,conf =fmd2.detect(img_temp)
                    color = getColorValue(res)
                    cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[0]+bbox[2],bbox[1]+bbox[3]),color,2)
                    #----FACE RECOGNITION
                    name =""
                    if len_ref_path>0:
                        img_fr=img_rgb[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2],:] #crop
                        img_fr=cv2.resize(img_fr,(int(model_shape[2]),int(model_shape[1]))) #resize
                        img_fr=np.expand_dims(img_fr,axis=0) #make 4 dimensions

                        feed_dict[tf_input] = img_fr
                        embeddings_tar=sess.run(tf_embeddings,feed_dict=feed_dict)
                        feed_dict_2[tf_tar] = embeddings_tar[0]

                        print(embeddings_tar[0])
                        distance =sess_cal.run(tf_dis,feed_dict=feed_dict_2)
                        arg =np.argmin(distance)

                        if distance[arg]<threshold:
                            name=paths[arg].split("\\")[-1].split(".")[0]
                            print(name)
                    cv2.putText(img, "%s: %s" % (str(res), str(name)),
                                (bbox[0] + 2, bbox[1] - 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
            #----FPS calculation
            if frame_count == 0:
                t_start = time.time()
            frame_count +=1
            if frame_count >=10:
                FPS ="FPS=%1f" %(10/(time.time() - t_start))
                frame_count = 0

            cv2.putText(img,FPS,(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
            #----image display
            cv2.imshow("demo",img)

            #----img writing
            if writer is not None:
                writer.write(img)

            #----keys handle
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key==ord('s'):
                #if len(bboxes) > 0:
                if bboxes:
                    img_temp=img[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2],:]
                    save_path ="img_crop.jpg"
                    save_path=os.path.join(ref_dir,save_path)
                    cv2.imwrite(save_path,img_temp)
                    print("an image is saved to ",save_path)

        else:
            print("get images failed")
            break

    cap.release()
    cv2.destroyWindow()
    if writer is not None:
        writer.release()

def getColorValue(myresult):
    if myresult=='correct_mask':
        return (0,255,0)
    elif myresult=='incorrect_mask':
        return (0,255,255)
    else:
        return (0,0,255)

if __name__ == "__main__":
    pb_path=r"model\pb_model.pb"
#
    node_dict={'input':'input:0',
               'keep_prob':'keep_prob:0',
               'phase_train': 'phase_train:0',
               'embeddings' : 'embeddings:0' }

    ref_dir=r"E:\PBL5\temp"
    stream(pb_path,node_dict,ref_dir,camera_source=0,resolution="480",to_write=False,save_dir=None)
