from pyfcm import FCMNotification


# Function to send Firebase Push Notification
def send_firebase_notification(token, alert):
    push_service = FCMNotification(api_key="AIzaSyCRbaiIswHpZJJqh4OfEauRgeZLLHLQR1M")  # Replace with your actual server key

    # Send notification
    result = push_service.notify_single_device(
        registration_id=token,
        message_body=alert.message,
        title=alert.title
    )

    return result
