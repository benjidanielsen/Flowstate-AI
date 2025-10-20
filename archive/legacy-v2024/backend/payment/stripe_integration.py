import stripe
from flask import Blueprint, request, jsonify

stripe.api_key = "sk_test_your_secret_key_here"

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount')  # in cents
        currency = data.get('currency', 'usd')

        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=['card']
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
