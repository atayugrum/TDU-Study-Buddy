import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
from collections import deque
import requests
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config

# --- Einstellungen und Konstanten ---
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID

# GPIO-Pins
SES_PIN = 17
ISIK_PIN = 27
LED_YESIL = 5
LED_SARI = 6
LED_KIRMIZI = 13

# Einstellungen für die Datenfilterung
MOVING_AVERAGE_SIZE = 5
temp_readings = deque(maxlen=MOVING_AVERAGE_SIZE)

# --- Globale Variablen (für die Kommunikation zwischen Threads) ---
global_current_states = {}
previous_alerts = {"ses": False, "isik": False, "sicaklik": False}
is_running = True

# --- Hardware- und Sensorfunktionen ---
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SES_PIN, GPIO.IN)
    GPIO.setup(ISIK_PIN, GPIO.IN)
    GPIO.setup(LED_YESIL, GPIO.OUT)
    GPIO.setup(LED_SARI, GPIO.OUT)
    GPIO.setup(LED_KIRMIZI, GPIO.OUT)
    print("GPIO pinleri ayarlandı.")

dht_sensor = adafruit_dht.DHT11(board.D14)

def get_sensor_states():
    global global_current_states
    states = {}
    
    states['ses_var'] = GPIO.input(SES_PIN) == GPIO.HIGH
    states['isik_var'] = GPIO.input(ISIK_PIN) == GPIO.HIGH
    states['ses_durum'] = "Yüksek" if states['ses_var'] else "İdeal"
    states['isik_durum'] = "İdeal" if states['isik_var'] else "Yetersiz"

    try:
        current_temp = dht_sensor.temperature
        if current_temp is not None:
            temp_readings.append(current_temp)
    except RuntimeError:
        pass
    
    if len(temp_readings) > 0:
        filtered_temp = sum(temp_readings) / len(temp_readings)
        states['sicaklik'] = filtered_temp
        states['sicaklik_durum'] = "İdeal" if 19 <= filtered_temp <= 25 else "Uygun Değil"
    else:
        states['sicaklik'] = None
        states['sicaklik_durum'] = "Okunamadı"
        
    global_current_states = states
    return states

def update_leds(states):
    ideal_olmayan_sayisi = 0
    if states.get('ses_var'): ideal_olmayan_sayisi += 1
    if not states.get('isik_var'): ideal_olmayan_sayisi += 1
    sicaklik = states.get('sicaklik')
    if sicaklik is None or not (19 <= sicaklik <= 25): ideal_olmayan_sayisi += 1
    
    GPIO.output(LED_YESIL, ideal_olmayan_sayisi == 0)
    GPIO.output(LED_SARI, ideal_olmayan_sayisi == 1)
    GPIO.output(LED_KIRMIZI, ideal_olmayan_sayisi >= 2)

# --- Telegram-Funktionen ---
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.get(url, params=params, timeout=5)
        print(f"Telegram'a uyarı gönderildi: {message}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def check_and_send_alerts(states):
    global previous_alerts
    
    if states['ses_var'] and not previous_alerts['ses']:
        send_telegram_alert("⚠️ UYARI: Ortamdaki ses seviyesi yükseldi!")
        previous_alerts['ses'] = True
    elif not states['ses_var']:
        previous_alerts['ses'] = False

    if not states['isik_var'] and not previous_alerts['isik']:
        send_telegram_alert("⚠️ UYARI: Işık seviyesi yetersiz!")
        previous_alerts['isik'] = True
    elif states['isik_var']:
        previous_alerts['isik'] = False

    sicaklik = states.get('sicaklik')
    is_temp_bad = sicaklik is not None and not (19 <= sicaklik <= 25)
    if is_temp_bad and not previous_alerts['sicaklik']:
        send_telegram_alert(f"⚠️ UYARI: Sıcaklık ideal aralıkta değil! ({sicaklik:.1f}°C)")
        previous_alerts['sicaklik'] = True
    elif not is_temp_bad:
        previous_alerts['sicaklik'] = False
        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Ben Akıllı Ders Asistanı Bot'u. Ortamdaki bir durum bozulduğunda sana haber vereceğim. Anlık durumu öğrenmek için /status yazabilirsin.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not global_current_states:
        await update.message.reply_text("Henüz sensör verisi okunmadı. Lütfen bir kaç saniye bekleyin.")
        return
    
    states = global_current_states
    sicaklik_str = f"{states['sicaklik']:.1f}°C" if states['sicaklik'] is not None else "Okunamadı"
    
    message = (
        f"📊 **Anlık Ortam Durumu** 📊\n\n"
        f"💡 Işık Durumu: *{states['isik_durum']}*\n"
        f"🔊 Ses Durumu: *{states['ses_durum']}*\n"
        f"🌡️ Sıcaklık: *{sicaklik_str} ({states['sicaklik_durum']})*"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

# --- Hauptschleife (wird in einem separaten Thread ausgeführt) ---
def sensor_loop():
    while is_running:
        states = get_sensor_states()
        update_leds(states)
        check_and_send_alerts(states)
        time.sleep(5)

# --- Hauptprogrammstart ---
if __name__ == "__main__":
    setup_gpio()
    
# 1. Starte die Sensorschleife in einem separaten Thread
    sensor_thread = threading.Thread(target=sensor_loop)
    sensor_thread.start()
    
# 2. Starte den Telegram-Bot im Haupt-Thread
    print("Sensör döngüsü başlatıldı. Telegram botu başlatılıyor...")
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))

# Stellt sicher, dass die Sensorschleife stoppt
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")

# Wartet, bis der Thread beendet ist
    finally:
        is_running = False
        sensor_thread.join()
        dht_sensor.exit()
        GPIO.cleanup()
        print("GPIO pinleri temizlendi. Hoşça kalın!")