'''
run.py
运行run.py 启动大数据平台
'''

from flask import *
import warnings
warnings.filterwarnings("ignore")
from search import *
import pickle
import xgboost as xgb

app = Flask(__name__)
app.config.from_object(__name__)
db=Mongobase()

@app.route('/')
def index():
	return render_template('main.html')

@app.route('/novel1')
def novel1():
    '''返回第一篇分析
    :return:
    '''
    return render_template('novel1.html')

@app.route('/novel2')
def novel2():
    '''
    返回第二篇分析
    :return:
    '''
    return render_template('novel2.html')

@app.route('/novel3')
def novel3():
    '''
    :return:返回第三篇分析
    '''
    return render_template('novel3.html')

@app.route('/func',methods=("POST", "GET"))
def func():
    '''
    预测与查询功能界面
    :return:
    '''
    len=db.findlength()
    strlen=str(len*67)
    dt=db.firstnum(30)
    dt=dt.drop(['_id'],axis=1)

    return render_template('func.html',strlen=strlen,tables=[dt.to_html(classes='data', header="true")])

@app.route('/Search',methods=['POST','GET'])
def Search():
    '''
    表单查询功能
    :return:
    '''
    id=request.form.get('id')
    vendor = request.form.get("vendor")
    passenger=request.form.get("passenger")
    tripduration=request.form.get("trip")
    starttime=request.form.get("start_date")
    endtime=request.form.get("end_date")
    starttime=str(starttime)
    endtime=str(endtime)

    print(id,'\n',vendor,'\n',passenger,'\n',tripduration,'\n',starttime,'\n',endtime)

    if(id):
        #id存在的情况
        print(id)
        data=db.searchbyid(id)

    else:
        #id不存在的情况
        vdid=int(vendor)
        passengers=int(passenger)
        tripdurationst=int(tripduration.split('-')[0])
        tripdurationed = int(tripduration.split('-')[1])
        data=db.searchby(vdid,passengers,tripdurationst,tripdurationed,starttime,endtime)

    len = db.findlength()
    strlen = str(len * 67)
    #if "_id" in data.columns:
     #   data = data.drop(['_id'], axis=1)

    return render_template('func.html', strlen=strlen, tables=[data.to_html(classes='data', header="true")])

@app.route('/Predict',methods=['POST','GET'])
def Predict():
    '''
    :return:读入上传的文件，进行预测
    '''
    file=request.files.get("upload")
    len = db.findlength()
    strlen = str(len * 67)
    dt = db.firstnum(30)
    dt = dt.drop(['_id'], axis=1)

    if(file):
        name=file.filename
        path = "./static/model/"+name
        file.save(path)

        fileuse=open(path)
        data=pd.read_csv(fileuse)
        fileuse.close()
        model= pickle.load(open("./static/model/pima.pickle.dat","rb"))

        datause=xgb.DMatrix(data)
        res=model.predict(datause)

        data['predicttime']=res

        return render_template('func.html', strlen=strlen, tables=[dt.to_html(classes='data', header="true")],predictions=[data.to_html(classes='data', header="true")])
    else:
        return render_template('func.html', strlen=strlen, tables=[dt.to_html(classes='data', header="true")])



if __name__ == '__main__':
    app.run(debug=True)