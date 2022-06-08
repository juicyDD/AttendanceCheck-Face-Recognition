import configparser
import sys

import mysql.connector
from mysql.connector import Error
import base64
import numpy as np



def read_db_params():
    # reading the env file
    config = configparser.ConfigParser()
    config.read('config/local.env')
    return config

def connect():
    try:
        # method will read the env file and return the config object
        params = read_db_params()
 
        # connect to database
        # reading the database parameters from the config object
        conn = mysql.connector.connect(
            host=params.get('DB', 'host'),
            database=params.get('DB', 'database'),
            user=params.get('DB', 'username'),
            password=params.get('DB', 'password'),
            port=params.get('DB', 'port')
        )
 
        return conn
    except(Exception, Error) as error:
        print(error)
        
def getSV(conn, mssv):
    # creating a cursor to perform a sql operation
    cursor = conn.cursor()
    sv = None
    query = "SELECT * FROM students_attendance_app_sinhvien WHERE id = {};".format(mssv)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            sv = record
            break
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            # print('\nConnection closed')
    return sv
def getEmailSV(conn,mssv):
    cursor = conn.cursor()
    emailsv = None
    query = "SELECT email FROM students_attendance_app_sinhvien WHERE id = {};".format(mssv)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            emailsv = record
            break
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return emailsv
    
def getLopHocPhan(conn, magv):
    cursor = conn.cursor()
    lophocphan = []
    query = "SELECT * FROM students_attendance_app_lophocphan WHERE giangvien_id = {};".format(magv)
    
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            temp = list(record)
            mamon = temp[4]
            temp[4] = getMon(connect(), mamon)
            lophocphan.append(temp)
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return lophocphan

def getGV(conn,msgv):
    cursor = conn.cursor()
    gv = None 
    query = "SELECT * FROM students_attendance_app_giangvien WHERE id = {};".format(msgv)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            gv = record
            break
    except(Exception, Error) as error:
        cursor.close()
        conn.close()
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return gv

def getMon(conn,mamon):
    cursor = conn.cursor()
    mon = None 
    query = "SELECT * FROM students_attendance_app_monhoc WHERE id = {};".format(mamon)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            mon = record[1]
            break
    except(Exception, Error) as error:
        cursor.close()
        conn.close()
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return mon

def getKhoa(conn, makhoa):
    cursor= conn.cursor()
    khoa = None
    query = "SELECT * FROM students_attendance_app_khoa WHERE id = '{}';".format(makhoa)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            khoa = record[1]
            break
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return khoa
        
def save_embeddings(conn, mssv, embeddings):
    cursor = conn.cursor()
    query = "INSERT INTO students_attendance_app_vectordactrung (vector_dt , sinhvien_id) VALUES (%s , %s)"
    for embedding in embeddings:
        try:
            embeddingstr = ''
            for foo in embedding:
                embeddingstr+= str(foo)
                embeddingstr+= '//'
            # embedding = base64.b64encode(embedding)
            print(embeddingstr)
            data=(embeddingstr, mssv)
            # query.format(embedding, mssv)
            cursor.execute(query,data)
            conn.commit()
        except (Exception, Error) as error:
            print(error)
        #Connection Close 
    conn.close()
def decode_vectors(vector):
    # vector = str.encode(vector)
    # r = base64.decodebytes(vector)
    # q = np.frombuffer(r, dtype=np.float64)
    vectorarr = []
    vectorarr = vector.split('//')
    q = []
    # print(vectorarr)
    for bar in vectorarr:
        try:
            bar = float(bar)
            q.append(bar)
        except (Exception,Error) as error:
            continue
    return q
    
def get_embeddings(conn, mssv):
    cursor = conn.cursor()
    embeddings = []
    query = "SELECT * FROM students_attendance_app_vectordactrung WHERE sinhvien_id = '{}';".format(mssv)
    result=[]
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
        if records:
            for record in records:
                temp = decode_vectors(record[1])
                lst=list(record)
                lst[1]=temp
                record=tuple(lst)
                result.append(record)
            return result
                # print(record)
def get_student_of_class(conn, lophocphan):
    cursor = conn.cursor()
    sinhviens = []
    print(lophocphan)
    query = "SELECT * FROM students_attendance_app_diemdanh WHERE lophocphan_id = '{}';".format(lophocphan)
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for record in records:
            sinhviens.append(record[17]) #get tất cả mssv của sv trong 1 lớp học phần
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
    return sinhviens

def delete_embeddings(conn, mssv):
    cursor = conn.cursor()
    query = "DELETE FROM students_attendance_app_vectordactrung WHERE sinhvien_id = '{}';".format(mssv)
    try:
        cursor.execute(query)
        conn.commit()
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            
def update_diemdanh(conn, sinhvienid, lophocphanid, buoihoc):
    cursor = conn.cursor()
    query = "UPDATE students_attendance_app_diemdanh SET {} = 1 WHERE sinhvien_id = '{}' AND lophocphan_id = '{}';".format(buoihoc, sinhvienid, lophocphanid)
    try:
        cursor.execute(query)
        conn.commit()
    except(Exception, Error) as error:
        print(error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()

                
# if __name__ == '__main__':
#     # connect to database and get all data
#     record =getSV(connect(),'102190281')
#     print(record[1])