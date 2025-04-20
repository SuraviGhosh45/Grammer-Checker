from gtts import gTTS
import pygame
import os
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from g4f import Client
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

def record_audio(duration=10, samplerate=16000):
    try:
        print("🎙️ Listening....")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        return np.squeeze(audio_data)
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return None

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        audio = record_audio()
        if audio is None:
            return None
        print("🧠 Processing your voice...")
        audio_data = sr.AudioData(audio.tobytes(), 16000, 2)
        query = recognizer.recognize_google(audio_data)
        print(f"✅ You said: {query}")
        return query
    except Exception as e:
        print(f"❌ Error during speech recognition: {e}")
        return None

def speak(text):
    try:
        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception as e:
        print(f"❌ Error during speech synthesis: {e}")

def grammar_check(sentence):
    prompt = (
        f"Check the grammar of this sentence and give only a score from 0 to 100 and a brief explanation. "
        f"Do not include any correction or feedback.\n\n"
        f"Sentence: \"{sentence}\"\n\n"
        f"Format:\nScore: ...\nExplanation: ..."
    )
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        print(f"❌ Error with online grammar check: {e}")
        return "An error occurred. Please try again."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_grammar', methods=['POST'])
def check_grammar():
    sentence = request.form['sentence']
    result = grammar_check(sentence)
    return jsonify(result=result)

@app.route('/check_speech', methods=['POST'])
def check_speech():
    speech_text = request.form['speech_text']
    result = grammar_check(speech_text)
    return jsonify(result=result)

if __name__ == "__main__":
    app.run(debug=True)
