from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            message_text = messaging_event['message'].get('text')

            if message_text:
                reply_text = generate_reply(message_text)
                send_instagram_message(sender_id, reply_text)
        except Exception as e:
            print("Ошибка обработки запроса:", e)

        return "EVENT_RECEIVED", 200

def generate_reply(user_text):
    prompt = f"Відповідай українською мовою як консультант магазину агрохімії. Клієнт написав: '{user_text}'. Відповідай лише в рамках товарів компанії, пропонуй супутні товари, запитуй ім’я, спосіб доставки і куди виставити рахунок. Запропонуй оплату, канал у Telegram та перехід на сайт."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ти продавець-консультант українського магазину агротематики."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

def send_instagram_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    print("Відповідь Facebook:", response.status_code, response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
