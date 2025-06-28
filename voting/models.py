"""
Models for the Django Election Voting System.

This module contains all the database models for managing elections,
voters, candidates, and votes with proper relati    photo = models.ImageField(
        upload_to=candidate_photo_path, 
        blank=True, 
        null=True,
        validators=[validate_image_file],
        help_text="Profile photo of the candidate (Max 5MB, formats: JPG, PNG, GIF)"
    )s and constraints.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
import os


def validate_image_file(value):
    """Validate uploaded image file size and format."""
    if value:
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise ValidationError("Image file size cannot exceed 5MB.")
        
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if ext not in valid_extensions:
            raise ValidationError(f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}")


def candidate_photo_path(instance, filename):
    """Generate a shorter, cleaner path for candidate photos."""
    # Use candidate ID and clean filename to avoid path length issues
    ext = os.path.splitext(filename)[1].lower()
    clean_filename = f"candidate_{instance.reg_no}{ext}"
    return f"candidates/{clean_filename}"


class Voter(models.Model):
    """
    Model representing a voter in the election system.
    
    Each voter has a unique token for authentication and can vote only once.
    """
    name = models.CharField(max_length=100, help_text="Full name of the voter")
    reg_no = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Registration number (student ID)"
    )
    token = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        editable=False,
        help_text="Unique authentication token for voting"
    )
    has_voted = models.BooleanField(
        default=False,
        help_text="Whether this voter has already cast their vote"
    )
    voted_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when the voter cast their vote"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voting_voter'
        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.reg_no})"

    def mark_as_voted(self):
        """Mark this voter as having voted and set the timestamp."""
        self.has_voted = True
        self.voted_at = timezone.now()
        self.save()


class Position(models.Model):
    """
    Model representing an election position (e.g., President, Secretary).
    
    Each position has a specific voting time window.
    """
    title = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Title of the position (e.g., President, Secretary)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the position and responsibilities"
    )
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Legacy field - voting times are now set globally in Election Settings"
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Legacy field - voting times are now set globally in Election Settings"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this position is active in the election"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voting_position'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['title']

    def __str__(self):
        return self.title

    def clean(self):
        """Validate that end_time is after start_time (legacy fields)."""
        # Only validate if both times are set (legacy functionality)
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def is_voting_open(self):
        """Check if voting is currently open (uses global election timing)."""
        if not self.is_active:
            return False
        settings = ElectionSettings.get_settings()
        return settings.is_voting_open()

    def is_voting_ended(self):
        """Check if voting has ended (uses global election timing)."""
        settings = ElectionSettings.get_settings()
        return settings.is_voting_ended()

    def get_status(self):
        """Get the current status of voting (uses global election timing)."""
        if not self.is_active:
            return "Inactive"
        settings = ElectionSettings.get_settings()
        return settings.get_voting_status()


class Candidate(models.Model):
    """
    Model representing a candidate who can contest for one or more positions.
    """
    name = models.CharField(max_length=100, help_text="Full name of the candidate")
    reg_no = models.CharField(
        max_length=20,
        help_text="Registration number of the candidate"
    )
    bio = models.TextField(
        blank=True,
        help_text="Brief biography or manifesto of the candidate"
    )
    positions = models.ManyToManyField(
        Position,
        related_name='candidates',
        help_text="Positions this candidate is contesting for"
    )
    photo = models.ImageField(
        upload_to=candidate_photo_path, 
        blank=True, 
        null=True,
        validators=[validate_image_file],
        help_text="Profile photo of the candidate (Max 5MB, formats: JPG, PNG, GIF)"
    )
    photo_url = models.URLField(
        blank=True,
        null=True,
        help_text="Cloud storage URL for the candidate photo (automatically set)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this candidate is active in the election"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voting_candidate'
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.reg_no})"

    def get_positions_list(self):
        """Get a comma-separated list of positions this candidate is contesting."""
        return ", ".join([pos.title for pos in self.positions.all()])

    def get_photo_url(self):
        """Get the photo URL with proper error handling, prioritizing cloud storage."""
        from django.conf import settings
        
        # First, check if we have a cloud URL
        if self.photo_url:
            return self.photo_url
            
        # Fallback to local photo file
        try:
            if self.photo and hasattr(self.photo, 'url'):
                return self.photo.url
        except (ValueError, AttributeError):
            pass
        return None

    def has_photo(self):
        """Check if candidate has a valid photo (cloud or local)."""
        return bool(self.photo_url or (self.photo and self.get_photo_url()))

    def upload_to_github(self):
        """Upload local photo to GitHub storage and update photo_url."""
        from django.conf import settings
        from .github_storage import github_storage
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not self.photo:
            logger.warning(f"No photo to upload for candidate {self.name}")
            return False
            
        if not github_storage.is_configured():
            logger.warning(f"GitHub storage not configured for candidate {self.name}")
            return False
            
        try:
            logger.info(f"Attempting to upload photo to GitHub for {self.name} ({self.reg_no})")
            
            # Upload to GitHub
            github_url = github_storage.upload_image(self.photo, self.reg_no, self.name)
            if github_url:
                logger.info(f"Successfully uploaded {self.name}'s photo to GitHub: {github_url}")
                self.photo_url = github_url
                
                # Optionally remove local file to save space
                if getattr(settings, 'REMOVE_LOCAL_AFTER_UPLOAD', False):
                    logger.info(f"Removing local photo file for {self.name}")
                    self.delete_photo()
                    
                self.save(update_fields=['photo_url'])
                return True
            else:
                logger.error(f"Failed to upload photo to GitHub for {self.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading to GitHub for {self.name}: {e}")
            return False

    def delete_photo(self):
        """Safely delete the candidate's photo file and GitHub image."""
        from .github_storage import github_storage
        
        # Delete from GitHub if we have a URL
        if self.photo_url and github_storage.is_configured():
            try:
                # Extract file path from GitHub URL
                if 'raw.githubusercontent.com' in self.photo_url:
                    parts = self.photo_url.split('/')
                    if len(parts) >= 2:
                        file_path = '/'.join(parts[-2:])  # Get last two parts (folder/filename)
                        github_storage.delete_image(file_path)
            except Exception:
                pass  # Fail silently
        
        # Delete local file
        if self.photo:
            try:
                if default_storage.exists(self.photo.name):
                    default_storage.delete(self.photo.name)
            except Exception:
                pass  # Fail silently to avoid breaking the model
            self.photo = None
        
        # Clear cloud URL
        self.photo_url = None

    def save(self, *args, **kwargs):
        """Override save to handle photo operations safely and validate."""
        from django.conf import settings
        from .github_storage import github_storage
        
        # Validate photo if it exists
        if self.photo:
            try:
                validate_image_file(self.photo)
            except ValidationError as e:
                # Log the validation error and remove the photo
                print(f"Photo validation failed for {self.name}: {e}")
                self.photo = None
        
        try:
            super().save(*args, **kwargs)
            
            # After successful save, try to upload to GitHub if configured and we have a local photo
            if (self.photo and not self.photo_url and 
                getattr(settings, 'USE_GITHUB_STORAGE', False) and 
                github_storage.is_configured()):
                self.upload_to_github()
                
        except Exception as e:
            # If there's an error with the photo, try saving without it
            if self.photo:
                self.delete_photo()
                super().save(*args, **kwargs)
            else:
                raise e


class Vote(models.Model):
    """
    Model representing a vote cast by a voter for a candidate in a specific position.
    
    This maintains the audit trail while keeping votes anonymous on the frontend.
    """
    voter = models.ForeignKey(
        Voter,
        on_delete=models.CASCADE,
        help_text="The voter who cast this vote"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        help_text="The position this vote is for"
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        help_text="The candidate this vote is for"
    )
    voted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this vote was cast"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address from which the vote was cast"
    )

    class Meta:
        db_table = 'voting_vote'
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        unique_together = ['voter', 'position']  # One vote per voter per position
        ordering = ['-voted_at']

    def __str__(self):
        return f"Vote by {self.voter.name} for {self.candidate.name} ({self.position.title})"

    def clean(self):
        """Validate that the candidate is contesting for the position."""
        if self.candidate and self.position:
            if not self.candidate.positions.filter(id=self.position.id).exists():
                raise ValidationError(
                    f"{self.candidate.name} is not contesting for {self.position.title}"
                )


class ElectionSettings(models.Model):
    """
    Model for storing global election settings and configurations.
    """
    election_title = models.CharField(
        max_length=200,
        default="Class Election 2025",
        help_text="Title of the election"
    )
    election_description = models.TextField(
        blank=True,
        help_text="Description of the election"
    )
    is_election_active = models.BooleanField(
        default=True,
        help_text="Whether the election system is active"
    )
    show_live_results = models.BooleanField(
        default=True,
        help_text="Whether to show live results during voting"
    )
    results_refresh_interval = models.PositiveIntegerField(
        default=30,
        help_text="Auto-refresh interval for live results (in seconds)"
    )
    technical_head_email = models.EmailField(
        blank=True,
        help_text="Email of the technical head who can access audit trails"
    )
    audit_password = models.CharField(
        max_length=100,
        default="audit2025",
        help_text="Password for audit trail access"
    )
    audit_access_code = models.CharField(
        max_length=50,
        default="AUDIT-EESA-2025",
        help_text="Special access code for audit trail"
    )
    voting_start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Global voting start time for all positions"
    )
    voting_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Global voting end time for all positions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voting_election_settings'
        verbose_name = 'Election Settings'
        verbose_name_plural = 'Election Settings'

    def __str__(self):
        return self.election_title

    def save(self, *args, **kwargs):
        """Ensure only one instance of election settings exists."""
        if not self.pk and ElectionSettings.objects.exists():
            # If this is a new instance and one already exists, update the existing one
            existing = ElectionSettings.objects.first()
            existing.election_title = self.election_title
            existing.election_description = self.election_description
            existing.is_election_active = self.is_election_active
            existing.show_live_results = self.show_live_results
            existing.results_refresh_interval = self.results_refresh_interval
            existing.technical_head_email = self.technical_head_email
            existing.audit_password = self.audit_password
            existing.audit_access_code = self.audit_access_code
            existing.voting_start_time = self.voting_start_time
            existing.voting_end_time = self.voting_end_time
            existing.save()
            return existing
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the current election settings, creating default if none exist."""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'election_title': 'Class Election 2025',
                'is_election_active': True,
                'show_live_results': True,
                'results_refresh_interval': 30,
            }
        )
        return settings

    def is_voting_open(self):
        """Check if voting is currently open globally."""
        if not self.voting_start_time or not self.voting_end_time:
            return False
        now = timezone.now()
        return self.voting_start_time <= now <= self.voting_end_time

    def is_voting_ended(self):
        """Check if voting has ended globally."""
        if not self.voting_end_time:
            return False
        return timezone.now() > self.voting_end_time

    def get_voting_status(self):
        """Get the current global voting status."""
        if not self.voting_start_time or not self.voting_end_time:
            return "Not Configured"
        now = timezone.now()
        if now < self.voting_start_time:
            return "Not Started"
        elif self.voting_start_time <= now <= self.voting_end_time:
            return "Active"
        else:
            return "Ended"

    def clean(self):
        """Validate that voting end time is after start time."""
        if self.voting_start_time and self.voting_end_time:
            if self.voting_end_time <= self.voting_start_time:
                raise ValidationError("Voting end time must be after start time.")
