import numpy as np
#tính vector khoảng cách (128x1) giữa vector lưu trong db(ref) và embeddings lấy từ webcam(target)
def distancevector(target,reference):
    result =[]
    for i in range(len(target)):
        result.append((target[i]-reference[i]))
        
#tính các chuẩn vector
def vector_norm(vector):
    #norm 1, 2(euclidean),3,4, inf norm
    # sau đó tính sum tất cả các norm 
    normArr = []
    #norm 1
    norm_tmp = np.linalg.norm(vector,1,axis=0)
    normArr.append(norm_tmp)
    #norm 2
    norm_tmp = np.linalg.norm(vector,2,axis=0)
    norm_tmp 
    normArr.append(norm_tmp)
    #norm 3
    norm_tmp = np.linalg.norm(vector,3,axis=0)
    normArr.append(norm_tmp)
    #norm 4
    norm_tmp = np.linalg.norm(vector,4,axis=0)
    normArr.append(norm_tmp)
    
    #max norm
    norm_tmp = abs(np.amax(vector))
    # norm_tmp *= 20
    normArr.append(norm_tmp)
    
    
    sum_norm = np.sum(normArr)
    return sum_norm
    
    
        

    