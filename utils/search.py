'''
连接数据库：查询，更新等
'''

import json
import pymongo
import warnings
import pandas as pd
import gc
warnings.filterwarnings("ignore")

class Mongobase(object):
    def __init__(self):
        self.conn = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.conn['taxi']

    def repr(self):
        print('connect successfully!')

    def closedb(self):
        '''
        关闭数据库
        :return:
        '''
        self.conn.close()

    def getall(self):
        '''
        返回所有数据
        :return:
        '''
        collection=self.db['t2']
        data = collection.find()
        data = pd.DataFrame(data)
        return data

    def firstnum(self,num):
        '''
        返回十条记录
        :return:
        '''
        collection = self.db['t2']
        data = collection.find().limit(num)
        data=pd.DataFrame(data)
        return  data

    def searchbyid(self,id):
        '''
        返回当前数据
        :param id: 订单编号查询
        :return:
        '''
        collection = self.db['t2']
        data=collection.find({"id":id})
        data=pd.DataFrame(data)

        return data

    def insert(self,data):
        '''
        插入数据
        :param data: Dataframe
        :return:
        '''
        collection = self.db['t2']
        collection.insert(json.loads(data.T.to_json()).values())

    def findlength(self):
        '''
        返回数据库中所有数据
        :return:
        '''
        collection = self.db['t2']
        return collection.find().count()

    def avgtime(self):
        '''
        返回平均时间，vendorid
        :return:
        '''
        all=self.getall()
        m=all['trip_duration'].mean()
        v1=len(all[all['vendor_id']==1])
        v2 = len(all[all['vendor_id'] == 2])
        del all
        gc.collect()

        return m,v1,v2

    def searchby(self,vdid,passengers,tripdurationst,tripdurationed,starttime,endtime):
        '''
        通过字段查询
        :param vdid:
        :param passengers:
        :param tripdurationst:
        :param tripdurationed:
        :param starttime:
        :param endtime:
        :return:
        '''
        collection=self.db['t2']
        data=collection.find({"$and": [{"vendor_id": vdid}, {"passenger_count": passengers},
                                  {"trip_duration": {"$gte": tripdurationst, "$lte": tripdurationed}},
                                  {"pick_date": {"$gte": starttime, "$lte": endtime}}]})
        data=pd.DataFrame(data)
        return data

'''
测试函数
'''
if __name__ == '__main__':
    db=Mongobase()
    #测试id查询
    data=db.searchbyid("id2875421")
    print(data)

    #测试前十条数据查询
    data2=db.firstten()
    print(data2)

    #测试数据条数
    data3=db.findlength()
    print(data3)

    data4,d5,d6=db.avgtime()
    print(data4,d5,d6)
