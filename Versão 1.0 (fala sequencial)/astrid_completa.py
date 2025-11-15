import ollama
import speech_recognition as sr
import pyttsx3
import time

# --- Configuração 1: A Boca (TTS) ---
print("Carregando a 'Boca' (TTS)...")
engine = pyttsx3.init()
# Tenta encontrar vozes em Português (pode não funcionar no Linux, mas tentamos)
try:
    voices = engine.getProperty('voices')
    for voice in voices:
        if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    print("Aviso: Não foi possível carregar vozes em PT-BR. Usando padrão.")


def falar(texto):
    """Função para fazer a Astrid falar"""
    print(f"🤖 Astrid: {texto}")
    engine.say(texto)
    engine.runAndWait()

# --- Configuração 2: O Ouvido (STT) ---
print("Carregando o 'Ouvido' (STT)...")
r = sr.Recognizer()
mic = sr.Microphone()

# Ajuste inicial de ruído (importante!)
with mic as source:
    print("Calibrando... por favor, fique em silêncio por 2 segundos.")
    r.adjust_for_ambient_noise(source, duration=2)
    print("Calibração concluída.")


# --- O Loop Principal ---
falar("Sistema online. Aguardando comandos, Mestre.")

while True:
    try:
        print("\nOuvindo...")
        with mic as source:
            # Escuta o áudio do microfone
            audio = r.listen(source, timeout=10, phrase_time_limit=180)
        
        # --- Parte 1: Transcrever (Voz -> Texto) ---
        print("Processando sua voz (Whisper)...")
        
        # Usa o Whisper local para transcrever.
        # 'model="base"' é o modelo pequeno (rápido).
        # Na primeira vez, ele vai baixar ~140MB.
        texto_usuario = r.recognize_whisper(
            audio, 
            model="base",  # (opções: tiny, base, small, medium)
            language="pt"
        )
        print(f"👤 Mestre: {texto_usuario}")

        # --- Parte 2: Pensar (Texto -> IA) ---
        # Envia o texto para a Astrid (seu bot do Ollama)
        response = ollama.chat(
            model='artrisdv3',  # <--- Use o nome do seu bot aqui!
            messages=[
                {'role': 'user', 'content': texto_usuario}
            ]
        )
        resposta_ia = response['message']['content']

        # --- Parte 3: Falar (IA -> Voz) ---
        falar(resposta_ia)
        
        # Se você falar "dormir", o programa para
        if "dormir" in texto_usuario.lower():
            falar("Entendido, Mestre. Desligando.")
            break

    except sr.UnknownValueError:
        # Erro se o Whisper não entendeu nada
        print("Desculpe, não entendi o que você disse.")
    except sr.WaitTimeoutError:
        # Erro se você não falou nada
        print("Tempo esgotado. Você não disse nada.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        falar("Mestre, ocorreu um erro. Reiniciando meu ciclo.")
        time.sleep(2)