import time
start_time = time.time()
import whisper

model = whisper.load_model("medium")

result = model.transcribe("audio_files/The_Internet_Said_So_EP158_seg1.mp3", fp16=False, language = 'Hindi', task='translate')
# result = model.transcribe("audio_files/sample_video_seg1.mp3")
text = result["text"]
print(result["text"])
with open('transcripted_files/transcripted_file.txt', 'w') as file:
        file.writelines(text)
print("Process finished --- %s seconds ---" % (time.time() - start_time))
# print(result)
