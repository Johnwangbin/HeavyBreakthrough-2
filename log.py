#coding:utf-8


class Log():
    def __init__(self):
        self.f  = open("log.txt", "a")
        self.fr = open("log.txt", "r")
    def log(self, label, txt):
        if isinstance(txt, list):
            txt = ",".join([str(i) for i in txt])
        text = label + ":" + txt + '\n'
        self.f.write(text.encode('utf-8'))

    def getLine(self, index):
        return self.fr.readlines()[index]

    def __del__(self):
        self.f.close()

if __name__ == "__main__":
    pass