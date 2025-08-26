##  Webhook Endpoint Manual

  **I did the task by django because, I so passionate the django.**

## Overview

This Task implements a webhook endpoint that receives and processes transaction notifications from YaYa Wallet and generate the signature. The endpoint verifies webhook requests using HMAC SHA256 signatures, prevents replay attacks via event ID tracking, and rejects requests older than 5 minutes to ensure security and freshness of data.

## Assumptions

- YaYa Wallet sends webhook POST requests with a JSON payload containing:
  - A unique `event_id` to identify each transaction event.
  - A `timestamp` in ISO 8601 format indicating when the event occurred.
  - A `transaction` object with details such as account ID, amount, currency, and status.
  - Each webhook request includes an `X-Yaya-Signature` HTTP header containing an HMAC SHA256 hex digest   signature of the raw JSON payload, generated with a shared secret (`YAYA_WEBHOOK_SECRET`).
  - The webhook payload timestamp is in ISO 8601 format and may or may not include timezone information. If timezone info is missing, UTC is assumed.
  - The webhook secret (`YAYA_WEBHOOK_SECRET`) is stored securely as an environment variable and never hardcoded.
  - Replay attacks are prevented by saving processed event IDs to a database and rejecting duplicates.
  - Requests older than 5 minutes from their `timestamp` are rejected to avoid processing stale events.


## How to Run

1. **Clone the repository**

2. **Set up your Python environment** 

3. **Install dependencies**
    - pip install -r requirements.txt


4. **Create a `.env` file** in the project root (same level as `manage.py`):
     **Set your webhook secret key in '.env'**
      - YAYA_WEBHOOK_SECRET = your_shared_secret_here

##  Apply migrations:

   - python manage.py makemigrations
   - python manage.py migrate
   
##  Run the server:
 - python manage.py runserver
    
    
##  The webhook endpoint available at:
 - https://localhost:8000/webhook/yaya/ 
  
##  Generating Signature for Testing
 - https://localhost:8000/webhook/yaya/generate-signature/


## How to Test
- Use a tool like Postman or Thunder Client.

- Prepare a JSON payload including a unique event_id and transaction data.

- Generate the HMAC SHA256 signature of the raw JSON payload using your webhook secret.

- Send a POST request to /webhook/yaya/ with:  Header X-Yaya-Signature set to the generated signature.

- Body as raw JSON payload.

- Successful requests will return {"message": "Webhook processed successfully"}.

- Sending the same event_id twice will return {"message": "Event already processed"} to prevent replays.

- Requests with invalid or missing signature, missing `event_id`, malformed JSON, or timestamps older than 5 minutes are rejected with appropriate HTTP status codes (400 or 403).



## Approach and Problem-Solving

**Security & Verification**  
- The webhook verifies authenticity by comparing the HMAC SHA256 signature sent from YaYa Wallet (`X-Yaya-Signature`) against a signature generated using the payload and a shared secret (`YAYA_WEBHOOK_SECRET`). - This prevents forged requests.

**Replay Protection**  
- To prevent replay attacks, all processed webhook event IDs are stored in the database. Any subsequent request with a duplicate `event_id` is recognized and rejected, ensuring each event is processed only once.

**Request Freshness**  
 - The webhook rejects requests older than 5 minutes (based on the `timestamp` in the payload) to avoid processing outdated notifications. This is checked by parsing the ISO 8601 timestamp and comparing it to the current UTC time.

**Maintainability & Simplicity**  
 - The code is modular, with clear separation between settings, models, and views.  
 - Proper error handling returns clear HTTP status codes and messages for each failure case.  
 - The use of environment variables keeps secrets out of the codebase.  
 - Code comments improve readability and maintenance.

**Extensibility**  
 - The transaction processing logic is designed as a placeholder for integrating custom business rules or data handling as needed by the partner system.




