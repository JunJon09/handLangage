from sklearn.model_selection import train_test_split
import pickle
def info():
    f = open('../findWord_DTW/word.txt', 'r', encoding='UTF-8')
    data = f.readlines()
    wordList = [d.replace("\n", "") for d in data]
    
    trainLeftList = []
    trainRightList = []
    trainBodyList = []
    testLeftList = []
    testRightList = []
    testBodyList = []
    for word in wordList:
        left, right, body = getData(word)
        train, test = split_data(left)
        trainLeftList.append(train)
        testLeftList.append(test)

        train, test = split_data(right)
        trainRightList.append(train)
        testRightList.append(test)

        train, test = split_data(body)
        trainBodyList.append(train)
        testBodyList.append(test)
    
    return trainLeftList, trainRightList, trainBodyList, testLeftList, testRightList, testBodyList, wordList
    
def split_data(data):
    train, test = train_test_split(data, test_size=5)
    return train, test

def getData(word):
    Path = "../findWord_DTW/DTWList/"
    left = []
    right = []
    body = []
    for i in range(30):
        absolutePath = Path + word + str(i)
        leftPath = absolutePath+ "_left.bin"
        rightPath = absolutePath + "_right.bin"
        bodyPath = absolutePath + "_body.bin"
        try:
            with open(leftPath, "rb") as p:
                l = pickle.load(p)
            left.append(l)
            with open(rightPath, "rb") as p:
                l = pickle.load(p)
            right.append(l)
            with open(bodyPath, "rb") as p:
                l = pickle.load(p)
            body.append(l)
        except Exception as e:
            continue

    
    return left, right, body

info()