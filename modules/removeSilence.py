import soundfile as sf
import numpy as np

#https://nantekottai.com/2020/06/14/video-cut-silence/
#読み込んだ時点で振幅は−１〜１の間に治る．無音のところもノイズがあるため０．０５以下は無音とする
#duration=1は音が鳴ってる判定でmin_voice_durationがdurationの中で会話してるとされるところ

def get_no_silence_time(src_file):
	data, samplerate = sf.read(src_file)

	thres = 0.05
	amp = np.abs(data)
	b = amp > thres

	min_silence_duration = 1

	silences = []
	prev = 0
	entered = 0
	for i, v in enumerate(b):
		if prev == 1 and v == 0: # enter silence
			entered = i
		if prev == 0 and v == 1: # exit silence
			duration = (i - entered) / samplerate #無音から終了まで
			if duration > min_silence_duration:
				silences.append({"from": entered, "to": i})
				entered = 0
		prev = v
	if entered > 0 and entered < len(b): #最後区切ることができなかった場合
		silences.append({"from": entered, "to": len(b)})


	min_keep_duration = 0.2

	cut_blocks = []
	blocks = silences

	tmp = blocks[0]
	while 1:
		if len(blocks) == 1:
			cut_blocks.append(tmp)
			break

		block = tmp
		next_blocks = [block]

		for i, b in enumerate(blocks):
			if i == 0:
				continue
			interval = (b["from"] - block["to"]) / samplerate
			if interval < min_keep_duration:
				block["to"] = b["to"]
				print(b)
				next_blocks.append(b)
			cut_blocks.append(block)
			blocks = list(filter(lambda b: b not in next_blocks, blocks))
		break


	cut_blocks = blocks

	keep_blocks = []
	for i, block in enumerate(cut_blocks):
		if i == 0 and block["from"] > 0:
			keep_blocks.append({"from": 0, "to": block["from"]})
		if i > 0:
			prev = cut_blocks[i - 1]
			keep_blocks.append({"from": prev["to"], "to": block["from"]})
		if i == len(cut_blocks) - 1 and block["to"] < len(data):
			keep_blocks.append({"from": block["to"], "to": len(data)})



    #duration=1は音が鳴ってる判定でmin_voice_durationがdurationの中で会話してるとされるところ
	min_voice_duration = 2 
	no_silence_blocks = []

	for i, block in enumerate(keep_blocks):
		fr = block["from"] / samplerate
		to = block["to"] / samplerate
		duration = to - fr
		padding_time = 0.8
		fr = max(block["from"] / samplerate - padding_time, 0)
		to = min(block["to"] / samplerate + padding_time, len(data) / samplerate)

	
		if duration > min_voice_duration:
			no_silence_blocks.append({"from": fr, "to": to})

	cut_inclusion_time(no_silence_blocks)

	print(no_silence_blocks)
	print("################")
	return no_silence_blocks

def cut_inclusion_time(blocks):
	# print(blocks)
	more = False
	for i in range(1,len(blocks)):
		# print(i)
		if blocks[i-1]["to"] > blocks[i]["from"]:
			blocks[i-1]["to"] = blocks[i]["to"]
			del blocks[i]
			more = True
			break
	if more:
		cut_inclusion_time(blocks)
