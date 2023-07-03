import writeSkeltonCsv
import moveDTW
import allCompareDTW
import glob
import pickle

def main():

    # left_hand_positionList, right_hand_positionList, body_positionList = writeSkeltonCsv.getSkltooPosition("./0.mp4")
    # left = [writeSkeltonCsv.fixList(left_hand_positionList)]
    # right = [writeSkeltonCsv.fixList(right_hand_positionList)]
    # body = [writeSkeltonCsv.fixList(body_positionList)]
    # f = open('./GPT単語情報/text1/拡大/*', 'r', encoding='UTF-8')

    files = glob.glob("./GPT単語情報/text2/拡大/*")
    
    with open(files[0], "rb") as p:
        body = [pickle.load(p)]
    with open(files[1], "rb") as p:
        left = [pickle.load(p)]
    with open(files[2], "rb") as p:
        right = [pickle.load(p)]
    
    
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
        preliminary_left, preliminary_right, preliminary_body = moveDTW.getData(word)
        trainLeftList.append(preliminary_left)
        trainRightList.append(preliminary_right)
        trainBodyList.append(preliminary_body)
    distanceList = []
    for i in range(len(trainLeftList)): #20
        print(i, wordList[i])
        distance, dispersion = moveDTW.learning(trainLeftList[i], left, trainRightList[i], right, trainBodyList[i], body)
        print(distance)
        distanceList.append(distance)
    averageSorted_list = allCompareDTW.sortedRank(distanceList)
    oneAnswerCount, fiveAnswerCount = allCompareDTW.printAnswer(averageSorted_list, 2, 0, 0, wordList) #平均
        
        

        


if __name__ == "__main__":
    main()