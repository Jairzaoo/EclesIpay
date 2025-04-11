import logging
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
import requests
from decouple import config

User = get_user_model()
logger = logging.getLogger(__name__)

# Import here to avoid circular imports
from dizimo.models import EmailLog

def get_user_last_contribution(user_email):
    """
    Get the last contribution for a user from the API
    """
    try:
        url = "https://api.abacatepay.com/v1/billing/list"
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {config("ABACATE_PAY_API_KEY")}'
        }
        params = {
            'customer.metadata.email': user_email
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        contributions = response.json().get('data', [])

        # Filter for paid contributions and sort by date
        paid_contributions = [c for c in contributions if c.get('status') == 'PAID']
        if not paid_contributions:
            return None

        # Sort by createdAt date (newest first)
        sorted_contributions = sorted(
            paid_contributions,
            key=lambda x: x.get('createdAt', ''),
            reverse=True
        )

        if sorted_contributions:
            last_contrib = sorted_contributions[0]
            return {
                'amount': last_contrib.get('amount', 0) / 100,  # Convert cents to Reais
                'date': datetime.strptime(
                    last_contrib.get('createdAt', '').split('.')[0],
                    '%Y-%m-%dT%H:%M:%S'
                )
            }
        return None
    except Exception as e:
        logger.error(f"Error getting last contribution for {user_email}: {str(e)}")
        return None

def send_monthly_email_to_user(user, force=False):
    """
    Send a monthly email to a single user

    Args:
        user: The user to send the email to
        force: If True, send the email even if one has already been sent this month

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        # Check if the user has already received an email this month
        if not force and EmailLog.has_received_monthly_email_this_month(user):
            logger.info(f"Skipping monthly email to {user.email} - already sent this month")
            return True

        # Get the user's last contribution
        last_contribution = get_user_last_contribution(user.email)

        # Prepare email context
        context = {
            'user': user,
            'last_contribution': last_contribution,
            'site_url': settings.SITE_URL
        }

        # Render email templates
        html_content = render_to_string('emails/monthly_reminder.html', context)
        text_content = strip_tags(html_content)

        # Create email
        subject = 'Lembrete Mensal - EclesIPay'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        # Send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        # Log the email sending
        EmailLog.objects.create(
            user=user,
            email_type='monthly',
            subject=subject,
            successful=True
        )

        logger.info(f"Monthly email sent to {user.email}")
        return True
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error sending monthly email to {user.email}: {error_message}")

        # Log the failed attempt
        try:
            EmailLog.objects.create(
                user=user,
                email_type='monthly',
                subject='Lembrete Mensal - EclesIPay',
                successful=False,
                error_message=error_message
            )
        except Exception as log_error:
            logger.error(f"Error logging email failure: {str(log_error)}")

        return False

def send_monthly_emails_to_all_users(force=False):
    """
    Send monthly emails to all active users

    Args:
        force: If True, send emails even if they've already been sent this month

    Returns:
        dict: A dictionary with counts of successful and failed email sends
    """
    users = User.objects.filter(is_active=True)
    success_count = 0
    failure_count = 0
    skipped_count = 0

    for user in users:
        # If force is False, the function will check if an email has already been sent this month
        result = send_monthly_email_to_user(user, force=force)

        # If the result is True but the user was skipped (already received an email this month)
        if result and not force and EmailLog.has_received_monthly_email_this_month(user):
            skipped_count += 1
        elif result:
            success_count += 1
        else:
            failure_count += 1

    logger.info(f"Monthly email sending complete. Success: {success_count}, Failures: {failure_count}, Skipped: {skipped_count}")
    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'skipped_count': skipped_count,
        'total_count': success_count + failure_count + skipped_count
    }
