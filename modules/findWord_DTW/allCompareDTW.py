import moveDTW
from sklearn.model_selection import train_test_split
import time
"""
多数の単語を比べて距離の近さから単語を考える
"""
def main():
    f = open('word.txt', 'r', encoding='UTF-8')
    data = f.readlines()
    wordList = [d.replace("\n", "") for d in data]
    
    trainLeftList = []
    trainRightList = []
    trainBodyList = []
    testLeftList = []
    testRightList = []
    testBodyList = []
    for word in wordList:
        left, right, body = moveDTW.getData(word)
        print(word)
        train, test = split_data(left)
        trainLeftList.append(train)
        testLeftList.append(test)

        train, test = split_data(right)
        trainRightList.append(train)
        testRightList.append(test)

        train, test = split_data(body)
        trainBodyList.append(train)
        testBodyList.append(test)

    oneAnswerList = []
    fiveAnswerList = []
    dispersiononeAnswerList = []
    dispersionfiveAnswerList = []
    for i in range(len(testLeftList)):
        oneAnswerCount = 0 
        fiveAnswerCount = 0
        dispersiononeAnswerCount = 0
        dispersionfiveAnswerCount = 0
        for k in range(5):
            distanceList = []
            dispersionList = []
            left = []
            right = []
            body = []
            left.append(testLeftList[i][k])
            right.append(testRightList[i][k])
            body.append(testBodyList[i][k])
            for j in range(len(trainLeftList)):
                distance, dispersion = moveDTW.learning(trainLeftList[j], left, trainRightList[j], right, trainBodyList[j], body)
                distanceList.append(distance)
                dispersionList.append(dispersion)
            indexList = list(enumerate(distanceList))
            dispersioninedxList = list(enumerate(dispersionList))
            sorted_list = sorted(indexList, key=lambda x: x[1])
            dispersionSorted_list = sorted(dispersioninedxList, key=lambda x: x[1])
            # 結果を表示
            for k, (index, value) in enumerate(sorted_list, start=1):
                print(f"{k}: {value} 単語 {wordList[index]}")
                if wordList[index] == wordList[i]:
                    if k == 1:
                        oneAnswerCount += 1
                    fiveAnswerCount += 1
                if k == 5:
                    break
            print("分散")
            for k, (index, value) in enumerate(dispersionSorted_list, start=1):
                print(f"{k}: {value} 単語 {wordList[index]}")
                if wordList[index] == wordList[i]:
                    if k == 1:
                        dispersiononeAnswerCount += 1
                    dispersionfiveAnswerCount += 1
                if k == 5:
                    break
            
            print("本当の答え:", wordList[i])
            print("*"*100)
        oneAnswerList.append(oneAnswerCount)
        fiveAnswerList.append(fiveAnswerCount)
        dispersiononeAnswerList.append(dispersiononeAnswerCount)
        dispersionfiveAnswerList.append(dispersionfiveAnswerCount)

    one_sum = 0
    five_sum = 0
    for i, (one, five) in enumerate(zip(oneAnswerList, fiveAnswerList)):
        one_sum += one
        five_sum += five
        print(f"{wordList[i]}の正解数: 1位 {one}/5 {(one/5) *100}% 5位まで {five}/5 {(five/5)*100}%")
    print(f"全体の正解数: 1位 {one_sum}/100 {one_sum}% 5位まで {five_sum}/100 {five_sum}%")

    #分散
    print("分散")
    one_sum = 0
    five_sum = 0
    for i, (one, five) in enumerate(zip(dispersiononeAnswerList, dispersionfiveAnswerList)):
        one_sum += one
        five_sum += five
        print(f"{wordList[i]}の正解数: 1位 {one}/5 {(one/5) *100}% 5位まで {five}/5 {(five/5)*100}%")
    print(f"全体の正解数: 1位 {one_sum}/100 {one_sum}% 5位まで {five_sum}/100 {five_sum}%")



def split_data(data):
    train, test = train_test_split(data, test_size=5)
    return train, test


if __name__ == "__main__": 
    main()