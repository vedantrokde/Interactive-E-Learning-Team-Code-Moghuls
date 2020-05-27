import json
import pyaudio  
import wave  
from os import remove
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('Igd1x4gYl_UE_ZKq8QKK-QMxKP1PKtNE9JZJzg1yCfK2')
service = TextToSpeechV1(authenticator=authenticator)
service.set_service_url('https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/dcfa76e6-aefb-4b1e-9c10-df4a9b6711d1')

def call(txt):
    file_path = './output.wav'
    class MySynthesizeCallback(SynthesizeCallback):
        def __init__(self):
            SynthesizeCallback.__init__(self)
            self.fd = open(file_path, 'ab')
            self.fd2 = open('current.wav','wb')

        def on_connected(self):
            print('Connection was successful')

        def on_error(self, error):
            print('Error received: {}'.format(error))

        def on_content_type(self, content_type):
            print('Content type: {}'.format(content_type))

        def on_timing_information(self, timing_information):
            print(timing_information)

        def on_audio_stream(self, audio_stream):
            self.fd.write(audio_stream)
            self.fd2.write(audio_stream)

        def on_close(self):
            # self.fd.close()
            print('Done synthesizing. Closing the connection')

    my_callback = MySynthesizeCallback()
    service.synthesize_using_websocket(txt,
                                    my_callback,
                                    accept='audio/wav',
                                    voice='en-US_AllisonVoice'
                                    )

def play(dir = 'current.wav'):
    chunk = 1024  
    f = wave.open(dir,"rb")  
    print('Playing the audio file . . .')
    p = pyaudio.PyAudio()  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  

    data = f.readframes(chunk)  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  

    stream.stop_stream()  
    stream.close()  
    p.terminate() 
    print('End of the audio file . . .')

def clear():
    remove('current.wav')
    remove('output.wav')

# call('Two roads diverged in a yellow wood, Robert Frost poetAnd sorry I could not travel both And be one traveler, long I stood And looked down one as far as I could To where it bent in the undergrowth;  Then took the other, as just as fair, And having perhaps the better claim, Because it was grassy and wanted wear; Though as for that the passing there Had worn them really about the same,  And both that morning equally lay In leaves no step had trodden black. Oh, I kept the first for another day! Yet knowing how way leads on to way, I doubted if I should ever come back.  I shall be telling this with a sigh Somewhere ages and ages hence: Two roads diverged in a wood, and I— I took the one less traveled by, And that has made all the difference.')
play()
clear()