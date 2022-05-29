from sklearn.cluster import KMeans
import numpy as np
from statistics import mean

def Kmean_clustering(coordinatesArray):
    #5 góc mặt
    kmeans = KMeans(n_clusters=5, random_state=0).fit(coordinatesArray)
    return kmeans.labels_

def average_embeddings(embeddingsArray, coordinatesArray):
    print("5 vector đặc trưng của khuôn mặt:")
    #coordinatesArray là mảng các vector 3x1 lưu trữ góc quay của khuôn mặt face pose/ face angle/ face position
    labels = Kmean_clustering(coordinatesArray)
    vectordactrung =[]
    for i in range (5):
        #temp=embeddingsArray[j if labels[j]==i]
        temp = [t for idx,t in enumerate(embeddingsArray) if labels[idx]==i]
        arrays = [np.array(x) for x in temp]
        temp=[np.mean(k) for k in zip(*arrays)]
        # temp=temp.tolist()
        
        print(temp)
        print("---")
        print(len(temp))
        print("---")
        vectordactrung.append(temp)
    return vectordactrung
    
