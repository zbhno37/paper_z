#:encoding:utf-8
#!/usr/bin/python

from __future__ import division
import numpy as np
import random
import sys
from datetime import datetime

MAX_INT = 99999999999999

class myData:

    def __init__(self,dataName,inputTrainFileName,speed,regUser,regItem,regBaise,CONST_K,myPrint):
        self.dataName = dataName
        self.inputTrainFileName = inputTrainFileName
        self.speed = speed
        self.regUser = regUser
        self.regItem = regItem
        self.regBaise = regBaise
        self.CONST_K = CONST_K
        self.myPrint = myPrint
        self.reset()

    def reset(self):
        self.scoreUserDic = {}
        self.scoreItemDic = {}

        self.userToIdDic = {}
        self.itemToIdDic = {}
        self.idToUserDic = {}
        self.idToItmeDic = {}

        self.userCount = 0
        self.itemCount = 0
        self.trainCount = 0
        self.correctCount = 0

        self.userBaise = None
        self.itemBaise = None
        self.globalBaise = None

        self.userV = None
        self.itemV = None

        self.lastTrainCost = MAX_INT

    def readData(self):
        # should make sure there are no duplicaset in  data
        self.readTrainData()

    def readTrainData(self):
        inputTrainFile = open(self.inputTrainFileName)

        self.userToIdDic = {}
        self.itemToIdDic = {}
        self.idToUserDic = {}
        self.idToItemDic = {}
        self.trainCount = 0

        duplicaset = set()

        while True:
            line = inputTrainFile.readline()
            if not line:
                break
            line = line.strip().split()

            user = line[0]
            item = line[1]
            score =  float(line[2])

            if (user + "/" + item) in  duplicaset:
                continue
            duplicaset.add(user + "/" + item)

            userId = self.userToIdDic.get(user, len(self.userToIdDic))
            itemId = self.itemToIdDic.get(item, len(self.itemToIdDic))
            self.userToIdDic[user] = userId
            self.itemToIdDic[item] = itemId

            self.idToUserDic[userId] = user
            self.idToItemDic[itemId] = item


            if not self.scoreUserDic.has_key(userId):
                self.scoreUserDic[userId] = {}
            if not self.scoreItemDic.has_key(itemId):
                self.scoreItemDic[itemId] = {}

            self.scoreUserDic[userId][itemId] = score
            self.scoreItemDic[itemId][userId] = score

            self.trainCount += 1

        self.userCount = len(self.userToIdDic)
        self.itemCount = len(self.itemToIdDic)

        self.testScore()
        inputTrainFile.close()

    def testScore(self):
        avg = 0.0
        count = 0
        for userId,arr in self.scoreUserDic.items():
            for itemId,score in arr.items():
                avg += score
                count += 1
                if score != self.scoreItemDic[itemId][userId]:
                    self.myPrint(0,"in test score#####################")
        self.myPrint(1,"in test score all sort sum:%d count:%d avg:%f"%(avg,count,avg/count))

    def genData(self):
        self.userV = np.random.random((self.userCount,self.CONST_K)) - 0.5
        self.itemV = np.random.random((self.itemCount,self.CONST_K)) - 0.5
        self.calBaise()

    def calBaise(self):

        self.userBaise = np.random.random(self.userCount) * 0.5 - 0.25
        self.itemBaise = np.random.random(self.itemCount) * 0.5 - 0.25


        self.globalBaise = 0.0
        countGlobal = 0

        for userId,arr in self.scoreUserDic.items():
            for itemId,score in arr.items():
                self.globalBaise += score
                countGlobal += 1

        self.globalBaise = self.globalBaise / countGlobal

        if countGlobal != self.trainCount:
            self.myPrint(0,"@@@@@@@@@error in cal baise, countGlobal", countGlobal)
            self.myPrint(0,"@@@@@@@@@error in cal baise, trainCount", self.trainCount)

    def calTrainCost(self):
        totalCost = 0.0
        for (userId,arr) in self.scoreUserDic.items():
            for (itemId,score) in arr.items():
                cost = np.dot(self.userV[userId],self.itemV[itemId]) + self.globalBaise + self.userBaise[userId] + self.itemBaise[itemId] - score
                cost = cost ** 2
                totalCost += cost

        for i in range(self.userCount):
            cost = np.dot(self.userV[i],self.userV[i])
            cost *= self.regUser
            totalCost += cost

        for j in range(self.itemCount):
            cost = np.dot(self.itemV[j],self.itemV[j])
            cost *= self.regItem
            totalCost += cost

        cost = np.dot(self.userBaise,self.userBaise)
        cost += np.dot(self.itemBaise,self.itemBaise)
        cost *= self.regBaise
        totalCost += cost

        avgCost = totalCost/self.trainCount

        if avgCost > self.lastTrainCost:
            self.myPrint(0,"EORROR in calTrainCost up !!")
        self.lastTrainCost = avgCost
        return avgCost

    def printInfo(self):
        self.myPrint(0,"----------------------model:%s---------------"%self.dataName)
        self.myPrint(0,"inputTrainFile:",self.inputTrainFileName)
        self.myPrint(0,"userCount:",self.userCount)
        self.myPrint(0,"itemCount:",self.itemCount)
        self.myPrint(0,"speed:",self.speed)
        self.myPrint(0,"globalBaise:",self.globalBaise)
        self.myPrint(0,"regUser:",self.regUser)
        self.myPrint(0,"regItem:",self.regItem)
        self.myPrint(0,"regBaise:",self.regBaise)
        self.myPrint(0,"CONST_K:",self.CONST_K)
        self.myPrint(0,"correctCount:",self.correctCount)
        self.myPrint(0,"trainCount:",self.trainCount)


        t = 10
        for i in range(t):
            userId = random.randint(0,self.userCount-1)
            while userId not in self.scoreUserDic:
                userId = random.randint(0,self.userCount-1)
            self.myPrint(1,"userV:",userId,self.userV[userId])

        for i in range(t):
            itemId = random.randint(0,self.itemCount-1)
            while itemId not in self.scoreItemDic:
                itemId = random.randint(0,self.itemCount-1)
            self.myPrint(1,"itemV:",itemId,self.itemV[itemId])

        for i in range(t):
            userId = random.randint(0,self.userCount-1)
            while userId not in self.scoreUserDic:
                userId = random.randint(0,self.userCount-1)
            self.myPrint(1,"userBaise:",userId,self.userBaise[userId])

        for i in range(t):
            itemId = random.randint(0,self.itemCount-1)
            while itemId not in self.scoreItemDic:
                itemId = random.randint(0,self.itemCount-1)
            self.myPrint(1,"itemBaise:",itemId,self.itemBaise[itemId])


def gradedecentRating(data,j):

    data,change = gradedecentRatingUser(data);
    cost = data.calTrainCost()



    change = int(change)
    myPrint(0,"i-th:%d,user>>>change:%8d,trainCost:%9.4f" %(j,change,cost))

    for i in range(2):
        data,change = gradedecentRatingItem(data)
        cost = data.calTrainCost()
        change = int(change)
        myPrint(0,"i-th:%d,item>>>change:%8d,trainCost:%9.4f" %(j,change,cost))

    for i in range(5):
        data,change = gradedecentBaise(data)
        cost = data.calTrainCost()
        change = int(change)
        myPrint(0,"i-th:%d,bais>>>change:%8d,trainCost:%9.4f" %(j,change,cost))

    return data

def gradedecentRatingUser(data):
    change = 0.0
    for userId in data.scoreUserDic:
        grad = np.zeros((1,data.CONST_K))
        for (itemId,score) in data.scoreUserDic[userId].items():
            u = np.dot(data.userV[userId],data.itemV[itemId]) + data.globalBaise + data.userBaise[userId] + data.itemBaise[itemId] - score
            u = u * data.itemV[itemId]
            grad = grad + u

        grad += data.regUser * data.userV[userId]

        data.userV[userId] = data.userV[userId] - data.speed * grad
        change += data.speed * np.dot(grad[0],grad[0])
    return data,change

def gradedecentRatingItem(data):
    change = 0.0
    for itemId in data.scoreItemDic:
        grad = np.zeros((1,data.CONST_K))
        for (userId,score) in data.scoreItemDic[itemId].items():
            v = np.dot(data.userV[userId],data.itemV[itemId]) + data.globalBaise + data.userBaise[userId] + data.itemBaise[itemId] - score
            v = v * data.userV[userId]
            grad = grad + v
        grad += data.regItem * data.itemV[itemId]

        data.itemV[itemId] = data.itemV[itemId] - data.speed * grad
        change += data.speed * np.dot(grad[0],grad[0])

    return data,change

def gradedecentBaise(data):
    grad = 0.0

    for userId,arr in data.scoreUserDic.items():
        gradU = 0.0
        for itemId,score in arr.items():
            gradU += np.dot(data.userV[userId],data.itemV[itemId]) + data.globalBaise + data.userBaise[userId] + data.itemBaise[itemId] - score
        gradU += data.regBaise * data.userBaise[userId]
        data.userBaise[userId] -= data.speed * gradU
        grad += gradU ** 2

    for itemId,arr in data.scoreItemDic.items():
        gradV = 0.0
        for userId,score in arr.items():
            gradV += np.dot(data.userV[userId],data.itemV[itemId]) + data.globalBaise + data.userBaise[userId] + data.itemBaise[itemId] - score
        gradV += data.regBaise * data.itemBaise[itemId]
        data.itemBaise[itemId] -= data.speed * gradV
        grad += gradV ** 2
    return data,grad * data.speed

def log(logstr, writer = sys.stdout):
    writer.write("%s\t%s\n" % (str(datetime.now()), logstr))
    writer.flush()

def myPrint(level,*args):
    if type(level) != int:
        print "error in myprint "
        sys.exit(1)
    if not printInfoOrNOt and level > 0:
        return
    if len(args) == 0:
        return
    message = [str(arg) for arg in args]
    message = " ".join(message)
    log(message)


def output(dataName, outPre, data):

    out_file = open(outPre + dataName + ".user", "w+")

    for userId in data.scoreUserDic:
        user = data.idToUserDic[userId]
        vector = [str(v) for v in  data.userV[userId]]
        vector.append(str(data.userBaise[userId]))

        line = "%s\t%s" % (user, " ".join(vector))
        out_file.write(line + "\n")

    out_file.close()
    out_file = open(outPre + dataName + ".item", "w+")

    for itemId in data.scoreItemDic:
        item  =  data.idToItemDic[itemId]
        vector = [str(v) for v in data.itemV[itemId]]
        vector.append(str(data.itemBaise[itemId]))

        line = "%s\t%s" % (item, " ".join(vector))
        out_file.write(line + "\n")

    out_file.close()


if __name__ ==  "__main__":

    if len(sys.argv) < 2:
        myPrint(0, "error in argv")
        sys.exit(1)
    argvDic = {}
    for  i in  range(1,len(sys.argv),2):
        argvDic[sys.argv[i]] = sys.argv[i+1]

    speed = float(argvDic["-speed"])
    regUser = float(argvDic["-regU"])
    regItem = float(argvDic["-regI"])
    regBaise = float(argvDic["-regB"])

    printInfoOrNOt = True
    numOfTrainTime = int(argvDic["-numTrain"])
    iterTime = int(argvDic["-iter"]) # for 20 iteration

    trainFileName = argvDic["-train"]
    dataName = argvDic["-dataName"]
    outPre = argvDic['-outPre']

    K = int(argvDic["-k"])


    minCostSum = 0
    minCost = MAX_INT
    count = 0
    myPrint(0,'begin...')
    for i in range(numOfTrainTime):
        data = myData(dataName,trainFileName,speed,regUser,regItem,regBaise,K,myPrint)
        data.readData()
        data.genData()
        myPrint(0,"----------------------start-------------------------------",iterTime)
        data.printInfo()
        for j in range(iterTime):
            data = gradedecentRating(data,j)
        temp = data.calTrainCost()
        if minCost > temp:
            minCost = temp
        minCostSum += temp
        myPrint(0,"----------------------end----------dataName,iterTime,i-th,mincost:",dataName,iterTime,i,minCost)
        data.printInfo()
        output(dataName, outPre, data)
    myPrint(0,"-end-all--:dataName,iterTime,min,avg,file:",dataName,iterTime,minCost,minCostSum/numOfTrainTime,trainFileName)

