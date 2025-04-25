from flask import Flask, request
import os
import requests
import openai

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.json
        print("Webhook received:", data)

        try:
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            message_text = messaging_event['message']['text']

            ai_response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": message_text}]
            )
            reply = ai_response.choices[0].message["content"]

            send_message(sender_id, reply)
        except Exception as e:
            print("Error processing message:", e)

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("Facebook response:", response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
