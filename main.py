from flask import Flask, request, jsonify
import openai
import os
import requests

app = Flask(__name__)

# Ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == os.environ.get("VERIFY_TOKEN"):
            return str(challenge), 200
        else:
            return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.json
        message_text = data.get('entry', [{}])[0].get('messaging', [{}])[0].get('message', {}).get('text', '')
        if message_text:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": message_text}
                ]
            )
            print("Ответ OpenAI:", response.choices[0].message["content"])
        return "EVENT_RECEIVED", 200

    return "Invalid method", 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
