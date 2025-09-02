from flask import Flask, request, jsonify
from pyngrok import ngrok

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📨 Webhook recebido:", data)
    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    port = 5000
    public_url = ngrok.connect(port)
    print(f"🌍 URL pública do webhook: {public_url}/webhook")
    app.run(host="0.0.0.0", port=port)

