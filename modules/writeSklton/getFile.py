import os
import changeMovie
import re
def main():
    path = "../../data/単語集"
    files = os.listdir(path)
    wordList = ["measure", "presentation", "vaccination", "government", "emergency", "coronavirus", "today", "state", "committee", "human", "china", "confirm", "japan", "minister", "policy", "america", "expand", "tokyo", "infection", "osaka"]
    learningList = ["train/", "test/", "val/"]
    count = 0
    for file_name in files:
        if file_name == ".DS_Store" or file_name == "全部":
            continue
        filePath = path + "/" + file_name + "/"
        wordFiles = os.listdir(filePath)
        wordFiles = [text for text in wordFiles if not text ==".DS_Store"]
        wordFiles = sorted(wordFiles, key=natural_keys)
        flag = 1
        learn = ""
        for i, file in enumerate(wordFiles):
            if flag >= 1:
                learn = learningList[flag-1]
                folderpath = "./word/" + learn + wordList[count]
                os.mkdir(folderpath)
                flag = 0
            inputFile = "../../data/単語集/" + file_name + "/"  + file
            outputFile = "./word/" + learn + wordList[count] + "/" + wordList[count] + str(i+1) + ".mp4"
            # testFile = "./word/" + wordList[count] + "/" + wordList[count] + str(i+1) + "_out.mp4"
            testFile = "./output.mp4"
            try:
                changeMovie.main(inputFile, outputFile, testFile)
            except Exception as e:
                print(e)
                print("エラー")
            if i == 19:
                flag = 2
            elif i == 26:
                flag = 3
        count += 1
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

if __name__ == "__main__":
    main()