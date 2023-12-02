#对于预测模型的训练

import pandas as pd
from matplotlib.pyplot import *
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split

#读取使用的文件
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

#Datetyping the dates
train['pickup_datetime'] = pd.to_datetime(train.pickup_datetime)
test['pickup_datetime'] = pd.to_datetime(test.pickup_datetime)

train.drop(['dropoff_datetime'], axis=1, inplace=True) #as we don't have this feature in the testset

#Date features creations and deletions
train['month'] = train.pickup_datetime.dt.month
train['week'] = train.pickup_datetime.dt.week
train['weekday'] = train.pickup_datetime.dt.weekday
train['hour'] = train.pickup_datetime.dt.hour
train['minute'] = train.pickup_datetime.dt.minute
train['minute_oftheday'] = train['hour'] * 60 + train['minute']
train.drop(['minute'], axis=1, inplace=True)

test['month'] = test.pickup_datetime.dt.month
test['week'] = test.pickup_datetime.dt.week
test['weekday'] = test.pickup_datetime.dt.weekday
test['hour'] = test.pickup_datetime.dt.hour
test['minute'] = test.pickup_datetime.dt.minute
test['minute_oftheday'] = test['hour'] * 60 + test['minute']
test.drop(['minute'], axis=1, inplace=True)

train.drop(['pickup_datetime'], axis=1, inplace=True)

#One-hot encoding binary categorical features
train = pd.concat([train, pd.get_dummies(train['store_and_fwd_flag'])], axis=1)
test = pd.concat([test, pd.get_dummies(test['store_and_fwd_flag'])], axis=1)

train.drop(['store_and_fwd_flag'], axis=1, inplace=True)

train = pd.concat([train, pd.get_dummies(train['vendor_id'])], axis=1)
test = pd.concat([test, pd.get_dummies(test['vendor_id'])], axis=1)

train.drop(['vendor_id'], axis=1, inplace=True)

def ft_haversine_distance(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    AVG_EARTH_RADIUS = 6371 #km
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = np.sin(lat * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * np.arcsin(np.sqrt(d))
    return h

#Add distance feature
train['distance'] = ft_haversine_distance(train['pickup_latitude'].values,
                                                 train['pickup_longitude'].values,
                                                 train['dropoff_latitude'].values,
                                                 train['dropoff_longitude'].values)
test['distance'] = ft_haversine_distance(test['pickup_latitude'].values,
                                                test['pickup_longitude'].values,
                                                test['dropoff_latitude'].values,
                                                test['dropoff_longitude'].values)

#Function aiming at calculating the direction
def ft_degree(lat1, lng1, lat2, lng2):
    AVG_EARTH_RADIUS = 6371 #km
    lng_delta_rad = np.radians(lng2 - lng1)
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    y = np.sin(lng_delta_rad) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(lng_delta_rad)
    return np.degrees(np.arctan2(y, x))

#Add direction feature
train['direction'] = ft_degree(train['pickup_latitude'].values,
                                train['pickup_longitude'].values,
                                train['dropoff_latitude'].values,
                                train['dropoff_longitude'].values)
test['direction'] = ft_degree(test['pickup_latitude'].values,
                                  test['pickup_longitude'].values,
                                  test['dropoff_latitude'].values,
                                  test['dropoff_longitude'].values)

train = train[(train.distance < 200)]
train['speed'] = train.distance / train.trip_duration
#Remove speed outliers
train = train[(train.speed < 30)]
train.drop(['speed'], axis=1, inplace=True)

feature_cols = ['passenger_count','pickup_longitude','pickup_latitude',
                'dropoff_longitude','dropoff_latitude',
                'N','Y','month','week','weekday','hour',
                'minute_oftheday','distance','direction']

x_train = train[feature_cols]
y_train = np.log1p(train['trip_duration'])
x_test = test[feature_cols]


x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.2, random_state=1)
Xcv,Xv,Zcv,Zv = train_test_split(x_valid, y_valid, test_size=0.4, random_state=1)
data_tr  = xgb.DMatrix(x_train, label=y_train)
data_cv  = xgb.DMatrix(Xcv   , label=Zcv)
evallist = [(data_tr, 'train'), (data_cv, 'valid')]

parms = {'max_depth':10,
         'objective':'reg:linear',
         'eta'      :0.05,
         'subsample':0.8,#SGD will use this percentage of data
#         'lambda '  :4, #L2 regularization term,>1 more conservative
#         'colsample_bytree ':0.9,
         'colsample_bylevel':1,
         'min_child_weight': 10,
         'nthread'  :3}  #number of cpu core to use

clf = xgb.train(parms, data_tr, num_boost_round=1000, evals = evallist,
                  early_stopping_rounds=100, maximize=False,
                  verbose_eval=100)

pickle.dump(clf, open("../static/model/pima.pickle.dat", "wb"))#保存模型