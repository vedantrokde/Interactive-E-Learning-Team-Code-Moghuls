import argparse
import base64
import configparser
import json
import threading
import time

import pyaudio
import websocket
from websocket._abnf import ABNF

CHUNK = 1024
FORMAT = pyaudio.paInt16

CHANNELS = 1

RATE = 44100
RECORD_SECONDS = 10000000
FINALS = []

REGION_MAP = {
    'us-east': 'gateway-wdc.watsonplatform.net',
    'us-south': 'stream.watsonplatform.net',
    'eu-gb': 'stream.watsonplatform.net',
    'eu-de': 'stream-fra.watsonplatform.net',
    'au-syd': 'gateway-syd.watsonplatform.net',
    'jp-tok': 'gateway-syd.watsonplatform.net',
}


def read_audio(ws, timeout):

    global RATE
    p = pyaudio.PyAudio()

    RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    rec = timeout or RECORD_SECONDS

    for i in range(0, int(RATE )):  # / CHUNKik* rec
        data = stream.read(CHUNK)
        ws.send(data, ABNF.OPCODE_BINARY)

    stream.stop_stream()
    stream.close()
    print("* done recording")

    data = {"action": "stop"}
    ws.send(json.dumps(data).encode('utf8'))
    time.sleep(1)
    ws.close()
    p.terminate()


def on_message(self, msg):

    data = json.loads(msg)
    if "results" in data:
        if data["results"][0]["final"]:
            FINALS.append(data)
        print(data['results'][0]['alternatives'][0]['transcript'])


def on_error(self, error):
    print(error)


def on_close(ws):
    transcript = "".join([x['results'][0]['alternatives'][0]['transcript']
                          for x in FINALS])
    print(transcript)


def on_open(ws):
    args = ws.args
    data = {
        "action": "start",
        "content-type": "audio/l16;rate=%d" % RATE,
        "continuous": True,
        "interim_results": True,
        "inactivity_timeout": 50,
        "word_confidence": True,
        "timestamps": True,
        "max_alternatives": 3
    }

    ws.send(json.dumps(data).encode('utf8'))

    threading.Thread(target=read_audio, args=(ws, args.timeout)).start()

def get_url():
    return ("wss://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/10f79b79-dbba-4294-8f76-985b9406bd70/v1/recognize")


def get_auth():
    return ("apikey", 'd795hJnr0EFrzafYChaL1IzlfmSBG_g9-dVAHIIBVd_d')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Transcribe Watson text in real time')
    parser.add_argument('-t', '--timeout', type=int, default=5)
    # parser.add_argument('-d', '--device')
    # parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    headers = {}
    userpass = ":".join(get_auth())
    headers["Authorization"] = "Basic " + base64.b64encode(
        userpass.encode()).decode()
    url = get_url()

    ws = websocket.WebSocketApp(url,
                                header=headers,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.args = parse_args()
    ws.run_forever()


if __name__ == "__main__":
    main()
