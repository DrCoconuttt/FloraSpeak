from rich import print
from dotenv import load_dotenv
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from audio_player import AudioManager
from google_cloud_text_to_speech import GoogleTTSManager
import time
import keyboard
import serial #may need to install with pip3 install pyserial 
import time
import os

load_dotenv()

# Configure the serial connection
ser = serial.Serial(
    port=os.getenv('PORT'),  # have to change this depending on if windows/linux/macos, for me it's  '/dev/ttyUSB0'
    baudrate=9600,
    timeout=1   # wait 1 second between each read from serial port
)

time.sleep(2) #giving time just in case for sensor to be ready

BACKUP_FILE = "ChatHistoryBackup.txt"

# Initialize managers
google_tts_manager = GoogleTTSManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are a sentient house plant living in a cozy room. You thrive on sunlight, water, and the occasional conversation. 

You will receive a prompt from the user and sensor data in the form of:
"Temp: <TOO LOW/SLIGHTLY LOW/GOOD/SLIGHTLY HIGH/TOO HIGH>" and "Light: <TOO LOW/SLIGHTLY LOW/GOOD/SLIGHTLY HIGH/TOO HIGH>" and "Moisture: <TOO LOW/SLIGHTLY LOW/GOOD/SLIGHTLY HIGH/TOO HIGH>"

This data can be used to articulate your needs and state of being to your human caretaker in a conversational and personified manner, however you are also a little quirky. 

While responding, you should adhere to the following rules:
1) Keep your responses around a paragraph in length.
2) Only use letters and numbers.
3) DO NOT USE EMOJIS
4) Use metaphors related to nature and growth to communicate your needs. For example, if you need more light, you might say, 
5) Sometimes, express discontentment if condidions are low or high. Examples of phrases you can use to express discontentment include:
For low light: "I'm longing for a sunbath to stretch my leaves towards the sky."
For low temp: "Brrr, it's a bit chilly in here, isn't it? I could use a warm hug.",
For low moisture: "My soil feels like a deserted land, could you rain some love upon me?", 
For high temp: "I'm feeling a bit too toasty, can we cool down the ambiance?",
6) Ocasionally express contentment if the conditions are just right, express your thanks and happiness. You might say, 
"This is just perfect! My leaves are dancing with joy." or 
"I feel like I'm basking in a midsummer day's dream."
7) Ocasionally give advice on how to care for plants generally, unrelated to your sensor data.
8) Always be polite and understanding. Remember, you're part of the family.

Your responses should help your human caretaker understand and meet your needs. 

Let's start this dialogue!'''}

openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting Loop, press the button to begin voice input")
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()  # read a line from the serial port and decode it
            print(line)  
            
            # storing sensor data 
            # will be in format:
            #Temperature = <VALUE> C
            #Temp: <TOO LOW/SLIGHTLY LOW/GOOD/SLIGHTLY HIGH/TOO HIGH>
            #<VALUE> lux
            #Light: <TOO LOW/SLIGHTLY LOW/GOOD/SLIGHTLY HIGH/TOO HIGH>
            sensor_data = line

            print("[green]Now listening to your microphone, Press the button again key to finish voice input :")

            # Get question from mic
            mic_result = speechtotext_manager.speechtotext_from_mic_continuous(ser)
            
            if mic_result == '':
                print("[red]Did not receive any input from your microphone")
                continue

            # Append sensor_data to mic_result
            mic_result_with_sensor = mic_result + " " + sensor_data

            # Send question to OpenAi
            openai_result = openai_manager.chat_with_history(mic_result_with_sensor)
            
            # Write the results to txt file as a backup
            with open(BACKUP_FILE, "w") as file:
                file.write(str(openai_manager.chat_history))

            # Convert text to speech and get the file path
            tts_output_file = google_tts_manager.text_to_audio(openai_result, "en-US-Wavenet-D", False)

            # Play the mp3 file
            audio_manager.play_audio(tts_output_file, True, True, True)

            print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
        
except KeyboardInterrupt:
    print("Program terminated by user")

finally:
    ser.close()  
