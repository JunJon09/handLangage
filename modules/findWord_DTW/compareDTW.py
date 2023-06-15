import moveDTW
from sklearn.model_selection import train_test_split

"""
二つの単語を比べて分類するプログラムです
"""
def compareDTW():
    word1 = "America"
    word2 = "Japan"
    data1_left, data1_right, data1_body = moveDTW.getData(word1)
    data2_left, data2_right, data2_body = moveDTW.getData(word2)

    train_left_data1, test_left_data1 = split_data(data1_left)
    train_right_data1, test_right_data1 = split_data(data1_right)
    train_body_data1, test_body_data1 = split_data(data1_body)
    train_left_data2, test_left_data2 = split_data(data2_left)
    train_right_data2, test_right_data2 = split_data(data2_right)
    train_body_data2, test_body_data2 = split_data(data2_body)

    #train1とtest1のdistance
    distance_1 = moveDTW.learning(train_left_data1, test_left_data1, train_right_data1, test_right_data1, train_body_data1, test_body_data1)

    #train1とtest2のdistance
    distance_2 = moveDTW.learning(train_left_data1, test_left_data2, train_right_data1, test_right_data2, train_body_data1, test_body_data2)

    #train2とtest2のdistance
    distance_3 = moveDTW.learning(train_left_data2, test_left_data2, train_right_data2, test_right_data2, train_body_data2, test_body_data2)

    #train2とtest1のdistance
    distance_4 = moveDTW.learning(train_left_data2, test_left_data1, train_right_data2, test_right_data1, train_body_data2, test_body_data1)

    print(distance_1, distance_2, distance_3, distance_4)

def split_data(data):
    train, test = train_test_split(data, test_size=1)
    return train, test


compareDTW()


