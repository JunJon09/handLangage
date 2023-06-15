listA = [3.1, 2.1, 4]

# 値とそのインデックスのペアを作成
indexed_list = list(enumerate(listA))
print(indexed_list)
# 値でソート
sorted_list = sorted(indexed_list, key=lambda x: x[1])
print(sorted_list)
# 結果を表示
for i, (index, value) in enumerate(sorted_list, start=1):
    print(f"{i}: {value} index {index}")
