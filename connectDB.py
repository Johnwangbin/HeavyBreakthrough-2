import MySQLdb


class DBManager():
    def __init__(self):
        self.db_name = "market"
        self.db=MySQLdb.connect(host="172.24.13.2",db=self.db_name,user="market",passwd="market")
        # self.db=MySQLdb.connect(host="localhost",db=self.db_name,user="root",passwd="")
        self.c=self.db.cursor()

    def __del__(self):
        self.c.close()
        self.db.commit()
        self.db.close()

db = DBManager()

datasource = "./datasource/"
log        = "./log/"
models     = "./models/"
svmdata    = "./svmdata/"
stocksinfo = "./stocks_info/"
scale      = "./scale/"
test       = "./test/"
dRange     = "./range/"
negexample = "./negexample/"