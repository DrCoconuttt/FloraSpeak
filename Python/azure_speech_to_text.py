from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import keyboard
import time
import os

class SpeechToTextManager:
    azure_speechconfig = None
    azure_audioconfig = None
    azure_speechrecognizer = None

    def __init__(self):
        
        load_dotenv()

        # Creates an instance of a speech config with specified subscription key and service region.
        # Replace with your own subscription key and service region (e.g., "westus").
        try:
            self.azure_speechconfig = speechsdk.SpeechConfig(subscription=os.getenv('AZURE_TTS_KEY'), region=os.getenv('AZURE_TTS_REGION'))
        except TypeError:
            exit("Ooops! You forgot to set AZURE_TTS_KEY or AZURE_TTS_REGION in your environment!")
        
        self.azure_speechconfig.speech_recognition_language="en-US"

    def speechtotext_from_mic_continuous(self, stop_key='5'):
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig)

        done = False
        
        # Optional callback to print out whenever a chunk of speech is being recognized. This gets called basically every word.
        #def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        #    print('RECOGNIZING: {}'.format(evt))
        #self.azure_speechrecognizer.recognizing.connect(recognizing_cb)
        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            print('RECOGNIZED: {}'.format(evt))
        self.azure_speechrecognizer.recognized.connect(recognized_cb)

        # We register this to fire if we get a session_stopped or cancelled event.
        def stop_cb(evt: speechsdk.SessionEventArgs):
            print('CLOSING speech recognition on {}'.format(evt))
            nonlocal done
            done = True

        # Connect callbacks to the events fired by the speech recognizer
        self.azure_speechrecognizer.session_stopped.connect(stop_cb)
        self.azure_speechrecognizer.canceled.connect(stop_cb)

        # This is where we compile the results we receive from the ongoing "Recognized" events
        all_results = []
        def handle_final_result(evt):
            all_results.append(evt.result.text)
        self.azure_speechrecognizer.recognized.connect(handle_final_result)

        # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
        # Other tasks can be performed on this thread while recognition starts...
        # wait on result_future.get() to know when initialization is done.
        # Call stop_continuous_recognition_async() to stop recognition.
        result_future = self.azure_speechrecognizer.start_continuous_recognition_async()
        result_future.get()  # wait for voidfuture, so we know engine initialization is done.
        print('Continuous Speech Recognition is now running, say something.')

        while not done:
            if keyboard.read_key() == stop_key:
                print("\nEnding azure speech recognition\n")
                self.azure_speechrecognizer.stop_continuous_recognition_async()
                time.sleep(1) #Time to let speech process unporcessed speech said right before button press
                break

        final_result = " ".join(all_results).strip()
        print(f"\n\nHeres the result we got!\n\n{final_result}\n\n")
        return final_result
