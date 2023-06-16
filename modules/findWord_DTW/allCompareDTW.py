import moveDTW
from sklearn.model_selection import train_test_split
import time
"""
多数の単語を比べて距離の近さから単語を考える
"""
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
            
            #順位の並び替え
            averageSorted_list = sortedRank(distanceList)
            dispersionSorted_list = sortedRank(dispersionList)

            # 結果を表示
            print("平均")
            oneAnswerCount, fiveAnswerCount = printAnswer(averageSorted_list, i, oneAnswerCount, fiveAnswerCount) #平均
            print("分散")
            dispersiononeAnswerCount, dispersionfiveAnswerCount = printAnswer(dispersionSorted_list, i, dispersiononeAnswerCount, dispersionfiveAnswerCount) #分散
            print("本当の答え:", wordList[i])
            print("*"*100)
        
        oneAnswerList.append(oneAnswerCount)
        fiveAnswerList.append(fiveAnswerCount)
        dispersiononeAnswerList.append(dispersiononeAnswerCount)
        dispersionfiveAnswerList.append(dispersionfiveAnswerCount)

    #全ての結果を表示
    printALlAnswer(oneAnswerList, fiveAnswerList)
    printALlAnswer(dispersiononeAnswerList, dispersionfiveAnswerList)



def split_data(data):
    train, test = train_test_split(data, test_size=5)
    return train, test

#順位の並び替え
def sortedRank(distanceList):
    indexList = list(enumerate(distanceList))
    sorted_list = sorted(indexList, key=lambda x: x[1])
    return sorted_list

#一単語の出力結果を表示
def printAnswer(sorted_list, i, oneAnswerCount, fiveAnswerCount):
    for k, (index, value) in enumerate(sorted_list, start=1):
        print(f"{k}: {value} 単語 {wordList[index]}")
        if wordList[index] == wordList[i]:
            if k == 1:
                oneAnswerCount += 1
            fiveAnswerCount += 1
        if k == 5:
            break
    return oneAnswerCount, fiveAnswerCount

#全ての出力結果を表示
def printALlAnswer(oneList, fiveList):
    one_sum = 0
    five_sum = 0
    for i, (one, five) in enumerate(zip(oneList, fiveList)):
        one_sum += one
        five_sum += five
        print(f"{wordList[i]}の正解数: 1位 {one}/5 {(one/5) *100}% 5位まで {five}/5 {(five/5)*100}%")
    print(f"全体の正解数: 1位 {one_sum}/100 {one_sum}% 5位まで {five_sum}/100 {five_sum}%")


if __name__ == "__main__": 
    main()