from django.core.management.base import BaseCommand
from django.utils import timezone
from dizimo.email_utils import send_monthly_emails_to_all_users
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send monthly reminder emails to all active users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force sending emails even if they have already been sent this month',
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            self.stdout.write(self.style.WARNING('Forcing email send to all users, even if already sent this month.'))

        self.stdout.write(self.style.SUCCESS('Starting to send monthly emails...'))

        # Log the start time
        start_time = timezone.now()
        logger.info(f"Monthly email sending started at {start_time}")

        # Send emails
        result = send_monthly_emails_to_all_users(force=force)

        # Log the end time
        end_time = timezone.now()
        duration = end_time - start_time

        # Output results
        self.stdout.write(self.style.SUCCESS(
            f"Monthly emails sent successfully!\n"
            f"Total users: {result['total_count']}\n"
            f"Success: {result['success_count']}\n"
            f"Failures: {result['failure_count']}\n"
            f"Skipped: {result['skipped_count']}\n"
            f"Duration: {duration.total_seconds():.2f} seconds"
        ))

        logger.info(
            f"Monthly email sending completed at {end_time}. "
            f"Duration: {duration.total_seconds():.2f} seconds. "
            f"Success: {result['success_count']}, Failures: {result['failure_count']}, "
            f"Skipped: {result['skipped_count']}"
        )
