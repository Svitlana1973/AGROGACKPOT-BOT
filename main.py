from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("Ответ от Facebook:", response.text)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        else:
            return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.json
        print("Входящее сообщение:", data)

        messaging_event = data.get('entry', [{}])[0].get('messaging', [{}])[0]
        sender_id = messaging_event.get('sender', {}).get('id')
        message_text = messaging_event.get('message', {}).get('text')

        if sender_id and message_text:
            ai_response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": message_text}]
            )
            reply = ai_response.choices[0].message["content"]
            send_message(sender_id, reply)

        return "EVENT_RECEIVED", 200

    return "Invalid method", 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

