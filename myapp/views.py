
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from django.conf import settings
from .models import WebhookEvent

#   Generate X-Yaya-Signature by concatenating payload values, encoding to UTF-8, then hashing with HMAC SHA256 using the secret key.  
def generate_yaya_signature(payload_dict, secret_key):

    # Concatenate all values from the payload dictionary, converted to string
    data_for_seal = ''.join(str(value) for value in payload_dict.values())
    
    # Encode the concatenated string to bytes
    signed_payload = data_for_seal.encode('utf-8')
    
    # Create HMAC SHA256 signature and get hexadecimal digest
    signature = hmac.new(secret_key.encode(), signed_payload, hashlib.sha256).hexdigest()
    return signature

    
# Endpoint to generate X-Yaya-Signature for a given JSON payload for testing.
# Expects JSON data or payload in POST request body.
@csrf_exempt
def generate_signature_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST Method Allowed')
    
    # Parse JSON payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')
    
    # Retrieve secret key from .env variables
    secret_key = settings.YAYA_WEBHOOK_SECRET
    
    # Generate signature
    signature = generate_yaya_signature(payload, secret_key)
    return JsonResponse({'X-Yaya-Signature': signature})


def process_webhook_async(data):
    # Placeholder: Process the transaction data (Replace with actual async task logic)
    transaction = data.get('transaction')
    if transaction:
        # Extract transaction details and handle them

        # id = transaction.get('account_id')
        # amount = transaction.get('amount')
        # currency = transaction.get('currency')
        # created_at_time = transaction.get('created_at_time')
        # timestamp = transaction.get('timestamp')
        # cause = transaction.get('cause')
        # full_name = transaction.get('full_name')
        # account_name = transaction.get('account_name')
        # status = transaction.get('status')
        pass




@csrf_exempt
def webhook(request):
    # Reject Non-HTTPS Requests
    if not request.is_secure():
        return HttpResponseForbidden("HTTPS is Required for Security")
    
    # Reject Non-POST Requests
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST Method Allowed')

    # Raw Request Body
    payload = request.body
    
    # Webhook Signature sent by YaYa Wallet (suppose it's in headers)
    signature = request.headers.get('X-Yaya-Signature')

    if not signature:
        return HttpResponseForbidden('Missing Signature')

    # Shared secret key for webhook verification (set in .env variable)
    secret = settings.YAYA_WEBHOOK_SECRET.encode()

    # Verify the webhook signature using HMAC SHA256
    computed_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        return HttpResponseForbidden('Invalid Signature')

    # Parse JSON Payload
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Malformed JSON')

    # Check for replay attacks by storing event ID
    event_id = data.get('event_id')
    if not event_id:
        return HttpResponseBadRequest('Missing event_id')
    

    if WebhookEvent.objects.filter(event_id=event_id).exists():
        # Event already processed (replay attack)
        return JsonResponse({'message': 'Event Already Processed'}, status=200)


    # Timestamp Validation: reject requests older than 5 minutes
    timestamp_str = data.get('timestamp')
    if not timestamp_str:
        return HttpResponseBadRequest('Missing Timestamp')

    try:
        # Parse ISO 8601 timestamp; assume UTC if timezone not provided
        request_time = datetime.fromisoformat(timestamp_str)
        if request_time.tzinfo is None:
            request_time = request_time.replace(tzinfo=timezone.utc)
    except ValueError:
        return HttpResponseBadRequest('Invalid Timestamp Format')

    now = datetime.now(timezone.utc)
    if now - request_time > timedelta(minutes=5):
        return HttpResponseForbidden('Request Timeout: Older Than 5 Minutes')
    
    # Immediately acknowledge receipt - quick 200 response
    response = JsonResponse({'message': 'Webhook Received'})

    # Save event to prevent replay
    WebhookEvent.objects.create(event_id=event_id, payload=data)

    # Start background task for complex processing (pseudo-code)
    process_webhook_async(data)

    return response


