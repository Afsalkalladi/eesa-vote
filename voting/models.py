"""
Models for the Django Election Voting System.

This module contains all the database models for managing elections,
voters, candidates, and votes with proper relationships and constraints.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


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
        help_text="When voting opens for this position"
    )
    end_time = models.DateTimeField(
        help_text="When voting closes for this position"
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
        """Validate that end_time is after start_time."""
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def is_voting_open(self):
        """Check if voting is currently open for this position."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def is_voting_ended(self):
        """Check if voting has ended for this position."""
        return timezone.now() > self.end_time

    def get_status(self):
        """Get the current status of voting for this position."""
        now = timezone.now()
        if now < self.start_time:
            return "Not Started"
        elif self.start_time <= now <= self.end_time:
            return "Active"
        else:
            return "Ended"


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
        upload_to='candidate_photos/', 
        blank=True, 
        null=True,
        help_text="Profile photo of the candidate"
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
