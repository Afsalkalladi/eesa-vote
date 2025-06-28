"""
Management command to migrate existing candidate photos to GitHub storage.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from voting.models import Candidate
from voting.github_storage import github_storage


class Command(BaseCommand):
    help = 'Migrate existing candidate photos to GitHub storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-upload photos even if they already have GitHub URLs',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))
        
        # Check if GitHub storage is configured
        if not github_storage.is_configured():
            self.stdout.write(
                self.style.ERROR(
                    'GitHub storage is not configured. Please set GITHUB_TOKEN and GITHUB_IMAGES_REPO environment variables.'
                )
            )
            return
        
        self.stdout.write('🚀 Starting photo migration to GitHub...\n')
        
        # Get candidates with local photos
        if force:
            candidates = Candidate.objects.filter(photo__isnull=False)
            self.stdout.write(f'Found {candidates.count()} candidates with photos (force mode)')
        else:
            candidates = Candidate.objects.filter(photo__isnull=False, photo_url__isnull=True)
            self.stdout.write(f'Found {candidates.count()} candidates with photos but no GitHub URL')
        
        if not candidates.exists():
            self.stdout.write(self.style.SUCCESS('✅ No photos need to be migrated'))
            return
        
        success_count = 0
        error_count = 0
        
        for candidate in candidates:
            self.stdout.write(f'📤 Processing {candidate.name} ({candidate.reg_no})...')
            
            if dry_run:
                if candidate.photo:
                    self.stdout.write(f'  Would upload: {candidate.photo.name}')
                else:
                    self.stdout.write(f'  No photo file found')
                continue
            
            try:
                if candidate.upload_to_github():
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Successfully uploaded to: {candidate.photo_url}')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Failed to upload photo')
                    )
                    error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error: {str(e)}')
                )
                error_count += 1
        
        if not dry_run:
            self.stdout.write('\n📊 Migration Summary:')
            self.stdout.write(f'  ✅ Successful uploads: {success_count}')
            self.stdout.write(f'  ❌ Failed uploads: {error_count}')
            
            if success_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\n🎉 Successfully migrated {success_count} photos to GitHub!')
                )
            
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  {error_count} photos failed to migrate. Check the logs above.')
                )
        else:
            self.stdout.write('\n🔍 Dry run complete. Use --dry-run=false to actually migrate the photos.')
