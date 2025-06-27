"""
Django management command to import voters from a CSV file.

Usage:
    python manage.py import_voters <csv_file_path>

CSV format:
    name,reg_no
    John Doe,2021001
    Jane Smith,2021002
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from voting.models import Voter


class Command(BaseCommand):
    help = 'Import voters from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing voter data'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing voters instead of skipping them'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options['update']
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        name = row.get('name', '').strip()
                        reg_no = row.get('reg_no', '').strip()
                        
                        if not name or not reg_no:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Row {row_num}: Missing name or reg_no - {row}'
                                )
                            )
                            error_count += 1
                            continue
                        
                        voter, created = Voter.objects.get_or_create(
                            reg_no=reg_no,
                            defaults={'name': name}
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created voter: {name} ({reg_no}) - Token: {voter.token}'
                                )
                            )
                        elif update_existing and voter.name != name:
                            voter.name = name
                            voter.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Updated voter: {name} ({reg_no})'
                                )
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Skipped existing voter: {name} ({reg_no})'
                                )
                            )
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Row {row_num}: Error processing {row} - {str(e)}'
                            )
                        )
                
                # Summary
                self.stdout.write('\n' + '='*50)
                self.stdout.write(
                    self.style.SUCCESS(f'Import completed!')
                )
                self.stdout.write(f'Created: {created_count}')
                self.stdout.write(f'Updated: {updated_count}')
                self.stdout.write(f'Skipped: {skipped_count}')
                if error_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f'Errors: {error_count}')
                    )
                
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')
