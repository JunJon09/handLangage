import moveDTW
from sklearn.model_selection import train_test_split
def main():
    f = open('word.txt', 'r', encoding='UTF-8')
    data = f.readlines()
    global wordList
    wordList = [d.replace("\n", "") for d in data]
    
    trainLeftList = []
    trainRightList = []
    trainBodyList = []
    testLeftList = []
    testRightList = []
    testBodyList = []
    for word in wordList:
        left, right, body = moveDTW.getData(word)
        train, test = split_data(left)
        trainLeftList.append(train)
        testLeftList.append(test)

        train, test = split_data(right)
        trainRightList.append(train)
        testRightList.append(test)

        train, test = split_data(body)
        trainBodyList.append(train)
        testBodyList.append(test)

def split_data(data):
    train, test = train_test_split(data, test_size=5)
    return train, test


if __name__ == "__main__":
    main()