from datalayer import *
from connectDB import *
from useSVM import *
from displayStocksInFile import DisplayStocksInFile

class SVDDModel():
    def __init__(self, name):
        range_suffix   = ".range"
        self.model_suffix   = ".model"

        self.src_suffix     = ".csv"
        self.data_suffix    = ".txt"
        self.scale_suffix   = ".scale"

        self.name   = name
        self.range_name = dRange + name + range_suffix
        self.model_name = models + "svdd_" + self.name + self.model_suffix

        self.train_src_name = datasource + name + self.src_suffix
        self.train_data_name = svmdata + name + self.data_suffix
        self.train_scale_name = scale + name + self.scale_suffix

    def saveModel(self, onlyCurve):
        # src, neg, data, scale, range_file, onlyCurve
        self.convertToSVMFormat(self.train_src_name, self.train_data_name, True, onlyCurve)

        scaleTrainSet(self.train_data_name, self.train_scale_name, self.range_name)
        result = useSVM(self.train_scale_name)
        g = result.split(" ")[1]
        y, x = svm_read_problem(self.train_scale_name)

        options = '-s 2 -t 0 -c 0.03125 -g %s' % str(g)
        m = svm_train(y, x, options)
        svm_save_model(self.model_name, m)

    def test(self,  model_tester):
        m = svm_load_model(self.model_name)
        y, x    = svm_read_problem(model_tester.scaleName())
        res = svm_predict(y, x, m)

        model_tester.initDisplay()

        for i, r in enumerate(res[0]):
            if r == 1.0:
                print i
                model_tester.display.displayOne(i)

    # can continue at last stopped point
    def convertToSVMFormat(self, src, des, polar, onlyCurve):
        getInfos = GetSelectedStockInfos()

        with open(src) as f:
            txt = f.read()

        count = 0
        w_lines = []
        w_txt = txt.split("\n\n")[:-1]
        for line in txt.split("\n\n")[-1].strip().split("\n"):
            line = line.strip()
            elements = line.split(",")
            date_str = "-".join(elements[0].split("/")) + " " + elements[2] + ":00"
            print date_str
            if not getInfos.saveToSVMFile(des, elements[1], FromStringTime(date_str) * 1000, polar, onlyCurve) \
                    == -1:
                count += 1
                w_lines.append(line)

        w_txt = "\n\n".join(w_txt) + "\n" + "\n".join(w_lines)

        with open(src, "w") as f:
            f.write(w_txt)

        elements = txt.split("\n\n")[-1].strip().split("\n")[-1].split(",")
        last_date = "-".join(elements[0].split("/")) + " " + elements[2] + ":00"

        return count, last_date

    def range(self):
        return self.range_name


class SVCModel(SVDDModel):
    def __init__(self, name):
        SVDDModel.__init__(self, name)
        self.train_neg_name = negexample + name + "_neg" + self.data_suffix
        self.model_name = models + "svc_" + self.name + self.model_suffix
        self.neg_num    = 60

    def saveModel(self, onlyCurve):
        amount, last_date = self.convertToSVMFormat(self.train_src_name, self.train_data_name, True, onlyCurve)
        set_producer = SetProducer()
        set_producer.generateTestSet(last_date, amount / self.neg_num + 1, self.neg_num)
        self.convertToSVMFormat(self.train_neg_name, self.train_data_name, False, onlyCurve)
        scaleTrainSet(self.train_data_name, self.train_scale_name, self.range_name)
        result = useSVM(scale)
        g = result.split(" ")[1]
        y, x = svm_read_problem(scale)

        return svm_train(y, x, '-c 128.0 -t 0 -g %s' % str(g))


class SetProducer():
    def __init__(self, name):
        self.src_name = name

    def generateTestSet(self, date, offset, num):
        end_date = datetime.strptime(date, "%Y-%m-%d")
        f = open(self.src_name, "w")
        f.close()

        for i in range(offset):
            end_date -= timedelta(days=1)
            if end_date.weekday() in [5, 6]:
                i -= 1
                continue
            self.generateRandomDate(end_date.strftime("%Y-%m-%d"), num)

    def generateRandomDate(self, date, num):
        start_time = datetime.strptime("10:30", "%H:%M")
        stocks_ids = getStocksIdsInDB("stocksInwdKLine.txt")

        f = open(self.src_name, "a")

        for i in range(num):
            end_time = start_time + timedelta(minutes=random.randint(0, 150))
            mid_time = datetime.strptime("11:30", "%H:%M")
            if end_time > mid_time:
                end_time += timedelta(hours=1.5)
            time = end_time.strftime("%H:%M")
            serials = stocks_ids[random.randint(0, len(stocks_ids) - 1)]
            f.write(date + "," + serials + "," + time + "\n")
        f.close()


class ModelTester():
    def __init__(self, name):
        src_suffix     = ".csv"
        data_suffix    = ".txt"
        scale_suffix   = ".scale"
        range_suffix   = ".range"

        self.name   = name
        self.range_name = dRange + name + range_suffix

        self.test_src_name = test + name + src_suffix
        self.test_data_name = svmdata + name + data_suffix
        self.test_scale_name = scale + name + scale_suffix

        self.display = None

    def convertAndScale(self, svm_trainer, onlyCurve):
        updateSVMDataFile(self.test_src_name, self.test_data_name, False, onlyCurve)
        # judge the svm scale range file's exist
        scaleTestSet(self.test_data_name, self.test_scale_name, svm_trainer.range())

    def initDisplay(self):
        self.display = DisplayStocksInFile(self.test_src_name)

    def displayTestSet(self):
        self.display.displaySome(0, 100)

    def scaleName(self):
        return self.test_scale_name

    '''
    def generateModel(self):
        updateSVMDataFile(self.train_src_name, self.train_data_name, True, True)
        scaleTrainSet(self.train_data_name, self.train_scale_name, self.range_name)
        getNewSVMModel(self.train_scale_name, self.model_name)

    def TestModel(self):
        scaleTestSet(self.test_data_name, self.test_scale_name, self.range_name)
        judgeBySVMModel(self.model_name, self.test_scale_name)

    def generateAndTestModel(self, name):
        self.generateModel()
        updateSVMDataFile(self.test_src_name, self.test_data_name, False, True)
        self.TestModel()
    '''

def train_two_models(name):
    svc_trainer     = SVCModel(name)
    svdd_trainer    = SVDDModel(name)
    svc_trainer.saveModel(True)
    svdd_trainer.saveModel(True)

def test_two_models(name):
    svc_trainer     = SVCModel(name)
    svdd_trainer    = SVDDModel(name)
    svc_tester      = ModelTester("svc_" + name)
    svdd_tester     = ModelTester("svdd_" + name)
    svc_tester.convertAndScale(svc_trainer, True)
    svdd_tester.convertAndScale(svdd_trainer, True)
    svdd_trainer.test(svdd_tester)
    svc_trainer.test(svc_tester)

if __name__ == "__main__":
    pass
