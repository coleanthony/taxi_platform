'''
存储数据，将本地csv存入mongodb集群
2016/2017

'''

import pymongo
import pandas as pd
import sys
import json
import gc

class Mongobase(object):
    def __init__(self,collection):
        self.conn=pymongo.MongoClient('mongodb://localhost:27017/')
        self.db=self.conn['taxi']
        self.collection=self.db[collection]

    def repr(self):
        print('connect successfully!')

    def closedb(self):
        self.conn.close()

    def dataprocess(self,data):
        datause = data[(data['pickup_longitude'] < -70) & (data['pickup_longitude'] > -76) & (
                data['pickup_latitude'] < 43) & (data['pickup_latitude'] > 37) & (
                                           data['dropoff_longitude'] < -70) & (
                                           data['dropoff_longitude'] > -76) & (
                                           data['dropoff_latitude'] < 43) & (data['dropoff_latitude'] > 37)]

        datause['pick_date']=datause['pickup_datetime'].apply(lambda x:x.split(" ")[0])
        datause = datause.drop(columns=['improvement_surcharge', 'total_amount'], axis=1)
        datause = datause.dropna()
        print('data process successfully')

        return datause

def main():
    mongo=Mongobase('d2')
    mongo.repr()
    file=open('C:\\Users\cwh\\train.csv')
    datause=pd.read_csv(file)
    file.close()
    print('open data successfully')
    datause=mongo.dataprocess(datause)

    length=len(datause)
    part=length//10

    mongo.collection.insert(json.loads(datause.T.to_json()).values())

    mongo.closedb()
    print('insert successfully')

if __name__ == '__main__':
    main()