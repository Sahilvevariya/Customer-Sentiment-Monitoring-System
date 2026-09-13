import requests

BOT_TOKEN = "AAGezrO_rJVkhe7Cf0CPdCOnY7R3DVaUj-k"
CHAT_ID = "8219260623"

def send_telegram_alert(message: str) -> bool:
    """
    Sends a message to the specified Telegram chat ID using the bot token.
    Returns True if successful, False otherwise.
    """ 
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
        return False 