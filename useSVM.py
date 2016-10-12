import subprocess
from libsvm.svmutil import *
import connectDB
from log import Log

def scaleTrainSet(data_src, scale_des, range):
    scalePath   = r"C:\libsvm-3.21\windows\svm-scale"
    cmd1 = scalePath + " -l -1 -u 1 -s " + range + " " +  \
           data_src + " > " +  scale_des
    popen = subprocess.Popen(cmd1,stdout=subprocess.PIPE,shell=True)
    popen.wait()


def scaleTestSet(test_src, scale_des, range):
    scalePath   = r"C:\libsvm-3.21\windows\svm-scale"
    cmd2 = scalePath + " -r " + range + " " + \
           test_src + " > " + scale_des
    popen = subprocess.Popen(cmd2,stdout=subprocess.PIPE,shell=True)
    popen.wait()

def useSVM(filename):
    log = open(connectDB.log + "log.txt", "a")
    # cmd = r"python C:/libsvm-3.21/tools/grid.py -s 2" + connectDB.svmdata + "data.txt"
    cmd = r"python C:/libsvm-3.21/tools/grid.py " + filename
    data=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
    txt = data.stdout.read()
    log.write(txt)
    log.close()
    return txt.strip().split("\n")[-1]

def getSVMModel(g, filename, modelname):
    y, x    = svm_read_problem(connectDB.svmdata + filename)
    options = '-s 2 -t 0 -c 0.03125 -g %s' % str(g)
    m       = svm_train(y, x, options)
    svm_save_model(connectDB.models + modelname, m)

def getTwoClassSVMModel(g, filename, modelname):
    y, x    = svm_read_problem(connectDB.svmdata + filename)
    m       = svm_train(y, x, '-c 128.0 -t 0 -g %s' % str(g))
    svm_save_model(connectDB.models + modelname, m)

def getDetailByIndex(index_array):
    f = open(connectDB.datasource + "random.csv", "r")
    lines   = f.readlines()
    detail  = ""
    for index in index_array:
        items   = lines[index].split(",")
        detail = detail + ",".join(items[:3]) + "\n"
    return detail

# when svm src file is modified, this function can return required stocks
# corresponding to new samples.
def getNewSVMModel(filename, modelname):
    result = useSVM(filename)
    g    = result.split(" ")[1]
    getSVMModel(g, filename, modelname)

def getNewTwoSVMModel(filename, modelname):
    result = useSVM(filename)
    g    = result.split(" ")[1]
    getTwoClassSVMModel(g, filename, modelname)

def judgeBySVMModel(filename, data_txt):
    m       = svm_load_model(connectDB.models + filename)
    y, x    = svm_read_problem(connectDB.svmdata + data_txt)
    res = svm_predict(y, x, m)
    print res
    log = Log()
    details = ""

    '''
    array   = []
    for i, label in enumerate(res[0]):
        if label == 1.0:
            array.append(i)
    details = getDetailByIndex(array)
    log.log("Required Stocks\n", details)
    '''


if __name__ == "__main__":
    # getNewSVMModel()
    # getNewTwoSVMModel()
    judgeBySVMModel("heavy.model", "test.scale")

    # judgeBySVMModel(connectDB.models + "heavy2.model")