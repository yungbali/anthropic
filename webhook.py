# webhook.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import os

app = Flask(__name__)

# Define the PAYSTACK_SECRET_KEY
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify Paystack signature
    paystack_signature = request.headers.get('x-paystack-signature')
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        request.data,
        hashlib.sha512
    ).hexdigest()

    if paystack_signature != computed_signature:
        return jsonify({'status': 'invalid signature'}), 400

    # Process the webhook
    event = request.json
    
    if event.get('event') == 'charge.success':
        # Update user's payment status in your database
        reference = event['data']['reference']
        # Store this reference and update user's access status
        
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=5000)