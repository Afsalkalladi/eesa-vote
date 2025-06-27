"""
Django management command to export voters with their tokens to a CSV file.

Usage:
    python manage.py export_voters [output_file]

If no output file is specified, it will create 'voters_tokens.csv'
"""

import csv
from django.core.management.base import BaseCommand
from voting.models import Voter


class Command(BaseCommand):
    help = 'Export voters with their tokens to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'output_file',
            nargs='?',
            default='voters_tokens.csv',
            help='Output CSV file path (default: voters_tokens.csv)'
        )
        parser.add_argument(
            '--include-voted',
            action='store_true',
            help='Include voters who have already voted'
        )
        parser.add_argument(
            '--tokens-only',
            action='store_true',
            help='Export only tokens (for distribution)'
        )

    def handle(self, *args, **options):
        output_file = options['output_file']
        include_voted = options['include_voted']
        tokens_only = options['tokens_only']
        
        # Filter voters
        voters = Voter.objects.all().order_by('name')
        if not include_voted:
            voters = voters.filter(has_voted=False)
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                if tokens_only:
                    # Export only tokens for distribution
                    fieldnames = ['token']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for voter in voters:
                        writer.writerow({
                            'token': str(voter.token)
                        })
                else:
                    # Export full voter information
                    fieldnames = [
                        'name', 'reg_no', 'token', 'has_voted', 'voted_at'
                    ]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for voter in voters:
                        writer.writerow({
                            'name': voter.name,
                            'reg_no': voter.reg_no,
                            'token': str(voter.token),
                            'has_voted': 'Yes' if voter.has_voted else 'No',
                            'voted_at': voter.voted_at.strftime('%Y-%m-%d %H:%M:%S') if voter.voted_at else ''
                        })
                
                count = voters.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully exported {count} voters to {output_file}'
                    )
                )
                
                if tokens_only:
                    self.stdout.write(
                        self.style.WARNING(
                            'Tokens exported for distribution. Keep this file secure!'
                        )
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error writing to file: {str(e)}')
            )
