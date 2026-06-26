"""
Firebase utilities for push notifications - UPDATED FOR V1 API
"""
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


# Initialize Firebase Admin SDK only if credentials file exists
def initialize_firebase():
    """Initialize Firebase Admin SDK with error handling"""
    if firebase_admin._apps:
        return True

    try:
        # Check if Firebase credentials file exists
        if not hasattr(settings, 'FIREBASE_SERVICE_ACCOUNT_KEY'):
            logger.warning("FIREBASE_SERVICE_ACCOUNT_KEY not set in settings")
            return False

        firebase_key_path = settings.FIREBASE_SERVICE_ACCOUNT_KEY

        if not os.path.exists(firebase_key_path):
            logger.warning(f"Firebase service account file not found: {firebase_key_path}")
            return False

        # Initialize with proper project configuration
        cred = credentials.Certificate(str(firebase_key_path))

        # Read project_id from the credentials file
        import json
        with open(firebase_key_path, 'r') as f:
            cred_data = json.load(f)
            project_id = cred_data.get('project_id')

        # Initialize with explicit project configuration
        firebase_admin.initialize_app(cred, {
            'projectId': project_id,
        })

        logger.info(f"Firebase Admin SDK initialized successfully for project: {project_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False


def send_push_notification(token, title, body, data=None):
    """Send a push notification to a single token"""
    if not initialize_firebase():
        logger.error("Firebase not initialized - cannot send notification")
        return False, "Firebase not initialized"

    try:
        # Use the new V1 API format
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    channel_id='default'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body
                        ),
                        badge=1,
                        sound='default'
                    )
                )
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon='/static/icon-192x192.png'
                )
            )
        )

        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return True, response

    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False, str(e)


def send_push_notification_multicast(tokens, title, body, data=None):
    """Send a push notification to multiple tokens using individual sends to avoid batch API"""
    if not initialize_firebase():
        logger.error("Firebase not initialized - cannot send notifications")
        return False, "Firebase not initialized"

    if not tokens:
        return False, "No tokens provided"

    try:
        success_count = 0
        failure_count = 0
        responses = []

        # Send to each token individually to avoid the batch API issue
        for i, token in enumerate(tokens):
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data or {},
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            title=title,
                            body=body,
                            channel_id='default'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=title,
                                    body=body
                                ),
                                badge=1,
                                sound='default'
                            )
                        )
                    ),
                    webpush=messaging.WebpushConfig(
                        notification=messaging.WebpushNotification(
                            title=title,
                            body=body,
                            icon='/static/icon-192x192.png'
                        )
                    )
                )

                response = messaging.send(message)
                success_count += 1
                responses.append({'success': True, 'response': response})
                logger.info(f"Successfully sent message to token {i + 1}/{len(tokens)}: {response}")

            except Exception as e:
                failure_count += 1
                responses.append({'success': False, 'error': str(e)})
                logger.error(f"Failed to send to token {i + 1}/{len(tokens)}: {e}")

        # Create a response object similar to multicast response
        class MockMulticastResponse:
            def __init__(self, success_count, failure_count, responses):
                self.success_count = success_count
                self.failure_count = failure_count
                self.responses = responses

        mock_response = MockMulticastResponse(success_count, failure_count, responses)

        logger.info(f"Completed sending to {len(tokens)} tokens: {success_count} successful, {failure_count} failed")

        return True, mock_response

    except Exception as e:
        logger.error(f"Error in multicast send: {e}")
        return False, str(e)
