import os
import requests
import json
import uuid
import random
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
import imageio

auth = "apikeyhere"

def prompt(msg):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth,
    }

    json_data = {
        'model': 'gpt-4o-mini',
        'messages': [
            {
        "role": "system",
        "content": "You are an assistant that generates JSON. You always return just the JSON with no additional description or context. never include any newline characters keep everything conformed."
        },
            {
                'role': 'user',
                'content': f'{msg}',
            },
        ],
        'temperature': 0.7,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    out = response.json()['choices'][0]['message']['content']
    output = json.loads(out)
    return output

def tts(json, id):
    arr=json
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth,
    }
    json_data = {
    'model': 'tts-1',
    'input': f'{arr}',
    'voice': 'nova',#onyx
    }
    response = requests.post('https://api.openai.com/v1/audio/speech', headers=headers, json=json_data)
    with open(f'{id}.mp3', "wb") as f:
        f.write(response.content)

def ttspromptvideo(audio_path, video_path, output_path):
    audio = AudioSegment.from_file(audio_path)
    audio_duration = len(audio) / 1000
    video = VideoFileClip(video_path)
    video_duration = video.duration
    if audio_duration > video_duration:
        raise ValueError("Audio duration is longer than the video duration.")
    start_time = random.uniform(0, video_duration - audio_duration)
    end_time = start_time + audio_duration
    video_snippet = video.subclip(start_time, end_time)
    mobile_video = video_snippet.resize(height=1920, width=1080).set_position(("center", "center")).on_color(size=(1080, 1920), color=(0, 0, 0))
    audio_clip = AudioFileClip(audio_path)
    final_video = mobile_video.set_audio(audio_clip)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=True, logger="bar")

def main(): #Define the story in the first line
    msg=""" 
       Write me a short story about a woman fighting a bear, 
        please return me it in 3 parts in the json formatting below:

        {"first": "first", "second": "second", "third": "third"}
       
        leave each part on a small clifhanger as i will be turning it into a 3part video, 
       please keep it conformed to only one person speaking instead of multiple characters and make sure its in a strict json format so i can read programatically and make sure the 3rd part has an ending
       """
    uniqueid = str(uuid.uuid4())
    directory = os.getcwd()
    path = os.path.join(directory, uniqueid)
    os.mkdir(path)
    jsondata = prompt(msg)
    output1=jsondata["first"]
    output2=jsondata["second"]
    output3=jsondata["third"]
    tts(output1, f"first-{uniqueid}")
    print("TTS - 1, Completed")
    tts(output2, f"second-{uniqueid}")
    print("TTS - 2, Completed")
    tts(output3, f"third-{uniqueid}")
    print("TTS - 3, Completed")
    ttspromptvideo(f"first-{uniqueid}.mp3", "background.mp4", f"{uniqueid}/first.mp4")
    print("Video - Part - 1, Completed")
    ttspromptvideo(f"second-{uniqueid}.mp3", "background.mp4", f"{uniqueid}/second.mp4")
    print("Video - Part - 2, Completed")
    ttspromptvideo(f"third-{uniqueid}.mp3", "background.mp4", f"{uniqueid}/third.mp4")
    print("Video - Part - 3, Completed")
    print("COMPLETED - COMPLETED - COMPLETED - COMPLETED")

main()