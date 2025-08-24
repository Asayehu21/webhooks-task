
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from .models import WebhookEvent

@csrf_exempt
def webhook(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    # Raw request body
    payload = request.body
    # Webhook signature sent by YaYa Wallet (suppose it's in headers)
    signature = request.headers.get('X-Yaya-Signature')

    if not signature:
        return HttpResponseForbidden('Missing signature')

    # Shared secret for webhook verification (set in Django settings)
    secret = settings.YAYA_WEBHOOK_SECRET.encode()

    # Verify the webhook signature using HMAC SHA256
    computed_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        return HttpResponseForbidden('Invalid signature')

    # Parse JSON payload
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
        return JsonResponse({'message': 'Event already processed'}, status=200)


    # Timestamp validation: reject requests older than 5 minutes
    timestamp_str = data.get('timestamp')
    if not timestamp_str:
        return HttpResponseBadRequest('Missing timestamp')

    try:
        # Parse ISO 8601 timestamp; assume UTC if timezone not provided
        request_time = datetime.fromisoformat(timestamp_str)
        if request_time.tzinfo is None:
            request_time = request_time.replace(tzinfo=timezone.utc)
    except ValueError:
        return HttpResponseBadRequest('Invalid timestamp format')

    now = datetime.now(timezone.utc)
    if now - request_time > timedelta(minutes=5):
        return HttpResponseForbidden('Request timeout: older than 5 minutes')



    # Save event to prevent replay
    WebhookEvent.objects.create(event_id=event_id, payload=data)

    # Process the transaction data (replace with your actual logic)
    transaction = data.get('transaction')
    if transaction:
        # Example: extract transaction details and handle them
        # account_id = transaction.get('account_id')
        # amount = transaction.get('amount')
        # created_at_time = transaction.get('created_at_time')
        # currency = transaction.get('currency')
        # cause = transaction.get('cause')
        # timestamp = transaction.get('timestamp')
        # full_name = transaction.get('full_name')
        # account_number = transaction.get('account_number')
        # status = transaction.get('status')
        # TODO: Implement your processing logic here

        pass

    return JsonResponse({'message': 'Webhook processed successfully'}, status=200)
