"""
Django management command to import candidates from CSV file.

Usage:
    python manage.py import_candidates candidates.csv

CSV Format:
    name,reg_no,description,position,photo_url
    John Doe,EE001,Experienced leader with vision,President,https://example.com/photo.jpg
    Jane Smith,EE002,Dedicated to student welfare,Secretary,
"""

import csv
import os
from urllib.parse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.base import ContentFile
from voting.models import Candidate, Position


class Command(BaseCommand):
    help = 'Import candidates from CSV file. Format: name,reg_no,description,position'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file containing candidate data')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing candidates if reg_no already exists',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        update_existing = options['update']

        # Check if file exists
        if not os.path.exists(csv_file):
            raise CommandError(f'File "{csv_file}" does not exist.')

        self.stdout.write(f'📄 Reading candidates from: {csv_file}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))

        candidates_data = []
        errors = []

        # Read CSV file
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate headers
                required_headers = ['name', 'reg_no', 'description', 'position']
                optional_headers = ['photo_url']
                if not all(header in reader.fieldnames for header in required_headers):
                    raise CommandError(
                        f'CSV file must have headers: {", ".join(required_headers)}\n'
                        f'Optional headers: {", ".join(optional_headers)}\n'
                        f'Found headers: {", ".join(reader.fieldnames or [])}'
                    )

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (accounting for header)
                    # Clean data
                    name = row['name'].strip()
                    reg_no = row['reg_no'].strip()
                    bio = row['description'].strip()  # CSV says 'description' but model uses 'bio'
                    position_name = row['position'].strip()
                    photo_url = row.get('photo_url', '').strip()  # Optional photo URL

                    # Validate required fields
                    if not all([name, reg_no, position_name]):
                        errors.append(f'Row {row_num}: Missing required fields (name, reg_no, or position)')
                        continue

                    # Check if position exists
                    try:
                        position = Position.objects.get(title__iexact=position_name)
                    except Position.DoesNotExist:
                        errors.append(f'Row {row_num}: Position "{position_name}" does not exist')
                        continue

                    candidates_data.append({
                        'name': name,
                        'reg_no': reg_no,
                        'bio': bio,
                        'position': position,
                        'photo_url': photo_url,
                        'row_num': row_num
                    })

        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

        # Display errors if any
        if errors:
            self.stdout.write(self.style.ERROR('❌ Errors found:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  • {error}'))
            
            if not candidates_data:
                raise CommandError('No valid candidate data found. Fix errors and try again.')

        # Show what will be imported
        self.stdout.write(f'\n📊 Found {len(candidates_data)} valid candidates:')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for candidate_data in candidates_data:
            name = candidate_data['name']
            reg_no = candidate_data['reg_no']
            bio = candidate_data['bio']
            position = candidate_data['position']
            photo_url = candidate_data['photo_url']
            row_num = candidate_data['row_num']

            # Handle photo download
            photo_file = None
            if photo_url and not dry_run:
                photo_file = self.download_photo(photo_url, name)

            # Check if candidate already exists
            existing_candidate = Candidate.objects.filter(reg_no=reg_no).first()

            if existing_candidate:
                if update_existing:
                    action = '🔄 UPDATE'
                    if not dry_run:
                        existing_candidate.name = name
                        existing_candidate.bio = bio
                        # Update photo if provided and successfully processed
                        if photo_file:
                            try:
                                existing_candidate.photo = photo_file
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(f'  📷 Error setting photo for {name}: {str(e)[:50]}...')
                                )
                        # Add position if not already assigned
                        if position not in existing_candidate.positions.all():
                            existing_candidate.positions.add(position)
                        try:
                            existing_candidate.save()
                            updated_count += 1
                        except Exception as e:
                            # If save fails with photo, try without photo
                            if existing_candidate.photo:
                                existing_candidate.photo = None
                                existing_candidate.save()
                                updated_count += 1
                                self.stdout.write(
                                    self.style.WARNING(f'  📷 Saved {name} without photo due to error: {str(e)[:50]}...')
                                )
                            else:
                                raise e
                else:
                    action = '⏭️  SKIP (exists)'
                    skipped_count += 1
            else:
                action = '✅ CREATE'
                if not dry_run:
                    try:
                        candidate = Candidate.objects.create(
                            name=name,
                            reg_no=reg_no,
                            bio=bio
                        )
                        # Set photo if provided and successfully processed
                        if photo_file:
                            try:
                                candidate.photo = photo_file
                                candidate.save()
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(f'  📷 Error setting photo for {name}: {str(e)[:50]}...')
                                )
                        candidate.positions.add(position)
                        created_count += 1
                    except Exception as e:
                        # If creation fails entirely, log and continue
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Failed to create candidate {name}: {str(e)[:50]}...')
                        )
                        errors.append(f'Row {row_num}: Failed to create candidate {name}: {str(e)[:50]}')
                        continue
                    # Set photo if provided
                    if photo_file:
                        candidate.photo = photo_file
                        candidate.save()
                    candidate.positions.add(position)
                    created_count += 1

            # Add photo status to output
            photo_status = ""
            if photo_url:
                if photo_file:
                    photo_status = " 📷✅"
                else:
                    photo_status = " 📷❌"
            
            self.stdout.write(f'  {action}: {name} ({reg_no}) -> {position.title}{photo_status}')

        # Summary
        self.stdout.write('\n📈 Summary:')
        
        if dry_run:
            self.stdout.write('  🔍 DRY RUN - No changes made')
            self.stdout.write(f'  📝 Would create: {len([c for c in candidates_data if not Candidate.objects.filter(reg_no=c["reg_no"]).exists()])}')
            if update_existing:
                self.stdout.write(f'  🔄 Would update: {len([c for c in candidates_data if Candidate.objects.filter(reg_no=c["reg_no"]).exists()])}')
            else:
                self.stdout.write(f'  ⏭️  Would skip: {len([c for c in candidates_data if Candidate.objects.filter(reg_no=c["reg_no"]).exists()])}')
        else:
            self.stdout.write(f'  ✅ Created: {created_count}')
            self.stdout.write(f'  🔄 Updated: {updated_count}')
            self.stdout.write(f'  ⏭️  Skipped: {skipped_count}')

        if errors:
            self.stdout.write(f'  ❌ Errors: {len(errors)}')

        self.stdout.write('\n🎉 Import completed!')
        
        if not dry_run and (created_count > 0 or updated_count > 0):
            self.stdout.write('\n💡 Next steps:')
            self.stdout.write('  1. Review candidates in Django admin')
            self.stdout.write('  2. Add candidate photos if needed')
            self.stdout.write('  3. Verify position assignments')

    def download_photo(self, photo_url, candidate_name):
        """Download photo from URL and return Django File object with better error handling."""
        if not photo_url:
            return None
            
        try:
            # For this implementation, we'll focus on local file paths
            # You can extend this to handle HTTP URLs with requests library
            if photo_url.startswith(('http://', 'https://')):
                self.stdout.write(
                    self.style.WARNING(f'  📷 HTTP URLs not supported yet for {candidate_name}. Please upload manually.')
                )
                return None
            
            # Handle local file paths
            if os.path.exists(photo_url):
                # Validate file size before processing
                file_size = os.path.getsize(photo_url)
                if file_size > 5 * 1024 * 1024:  # 5MB limit
                    self.stdout.write(
                        self.style.WARNING(f'  📷 Photo too large for {candidate_name}: {file_size / 1024 / 1024:.1f}MB (max 5MB)')
                    )
                    return None
                
                with open(photo_url, 'rb') as f:
                    # Get file extension and validate
                    _, ext = os.path.splitext(photo_url)
                    if not ext:
                        ext = '.jpg'
                    ext = ext.lower()
                    
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                    if ext not in valid_extensions:
                        self.stdout.write(
                            self.style.WARNING(f'  📷 Invalid file type for {candidate_name}: {ext}')
                        )
                        return None
                    
                    # Create shorter, cleaner filename to avoid path length issues
                    clean_name = candidate_name.replace(' ', '_').replace('-', '_').lower()[:20]  # Limit name length
                    filename = f"{clean_name}{ext}"
                    
                    # Read file content
                    content = f.read()
                    
                    # Create Django file object
                    from django.core.files.base import ContentFile
                    return ContentFile(content, name=filename)
            else:
                self.stdout.write(
                    self.style.WARNING(f'  📷 Photo file not found: {photo_url} for {candidate_name}')
                )
                return None
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  📷 Error processing photo for {candidate_name}: {str(e)[:100]}...')
            )
            return None
