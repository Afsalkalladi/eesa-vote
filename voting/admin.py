"""
Django Admin configuration for the Election Voting System.

This module configures the admin interface for managing elections,
voters, candidates, and viewing results.
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Voter, Position, Candidate, Vote, ElectionSettings


@admin.register(ElectionSettings)
class ElectionSettingsAdmin(admin.ModelAdmin):
    """Admin interface for election settings."""
    
    list_display = [
        'election_title', 
        'is_election_active', 
        'show_live_results',
        'results_refresh_interval'
    ]
    fieldsets = (
        ('Election Information', {
            'fields': ('election_title', 'election_description')
        }),
        ('Global Voting Schedule', {
            'fields': ('voting_start_time', 'voting_end_time'),
            'description': 'Set the global voting times for all positions. Individual position times are no longer used.'
        }),
        ('Election Control', {
            'fields': ('is_election_active', 'show_live_results', 'results_refresh_interval')
        }),
        ('Technical Settings', {
            'fields': ('technical_head_email',)
        }),
    )

    def has_add_permission(self, request):
        """Only allow one election settings instance."""
        return not ElectionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of election settings."""
        return False


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    """Admin interface for managing voters."""
    
    list_display = ['name', 'reg_no', 'has_voted', 'voted_at', 'token_display']
    list_filter = ['has_voted', 'voted_at']
    search_fields = ['name', 'reg_no']
    readonly_fields = ['token', 'voted_at', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Voter Information', {
            'fields': ('name', 'reg_no')
        }),
        ('Voting Status', {
            'fields': ('has_voted', 'voted_at')
        }),
        ('Authentication', {
            'fields': ('token',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def token_display(self, obj):
        """Display token with copy functionality."""
        return format_html(
            '<span title="Click to copy" style="font-family: monospace; cursor: pointer;" '
            'onclick="navigator.clipboard.writeText(\'{}\'); '
            'this.style.backgroundColor=\'lightgreen\'; '
            'setTimeout(() => this.style.backgroundColor=\'\', 1000);">{}</span>',
            str(obj.token),
            str(obj.token)[:8] + '...'
        )
    token_display.short_description = 'Token'

    actions = ['reset_voting_status', 'export_tokens']

    def reset_voting_status(self, request, queryset):
        """Reset voting status for selected voters."""
        count = queryset.update(has_voted=False, voted_at=None)
        self.message_user(request, f'Reset voting status for {count} voters.')
    reset_voting_status.short_description = 'Reset voting status'

    def export_tokens(self, request, queryset):
        """Export tokens for selected voters."""
        # This would typically generate a CSV download
        self.message_user(request, 'Token export functionality would be implemented here.')
    export_tokens.short_description = 'Export tokens'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin interface for managing election positions."""
    
    list_display = [
        'title', 
        'get_status', 
        'candidate_count', 
        'vote_count',
        'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['title']
    
    fieldsets = (
        ('Position Information', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Note', {
            'fields': (),
            'description': 'Voting times are set globally in Election Settings. Individual position timing is no longer used.'
        }),
        ('Individual Timing (Legacy - Not Used)', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',),
            'description': 'These fields are kept for backward compatibility but are not used. Use Election Settings for global timing.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def candidate_count(self, obj):
        """Display number of candidates for this position."""
        return obj.candidates.count()
    candidate_count.short_description = 'Candidates'

    def vote_count(self, obj):
        """Display number of votes for this position."""
        return Vote.objects.filter(position=obj).count()
    vote_count.short_description = 'Total Votes'

    def get_status(self, obj):
        """Display voting status with color coding."""
        status = obj.get_status()
        colors = {
            'Not Started': '#ffc107',  # Warning yellow
            'Active': '#28a745',       # Success green
            'Ended': '#6c757d'         # Secondary gray
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, '#000'),
            status
        )
    get_status.short_description = 'Status'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Admin interface for managing candidates."""
    
    list_display = [
        'name', 
        'reg_no', 
        'get_positions_list', 
        'vote_count',
        'is_active'
    ]
    list_filter = ['is_active', 'positions']
    search_fields = ['name', 'reg_no', 'bio']
    filter_horizontal = ['positions']
    ordering = ['name']
    
    fieldsets = (
        ('Candidate Information', {
            'fields': ('name', 'reg_no', 'bio', 'photo', 'is_active')
        }),
        ('Positions', {
            'fields': ('positions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def vote_count(self, obj):
        """Display total votes received by this candidate."""
        return Vote.objects.filter(candidate=obj).count()
    vote_count.short_description = 'Total Votes'

    def get_positions_list(self, obj):
        """Display positions as a formatted list."""
        positions = obj.positions.all()
        if not positions:
            return "No positions"
        return format_html(
            '<br>'.join([pos.title for pos in positions])
        )
    get_positions_list.short_description = 'Positions'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for viewing votes (audit purposes)."""
    
    list_display = [
        'voter_name',
        'voter_reg_no', 
        'position', 
        'candidate', 
        'voted_at',
        'ip_address'
    ]
    list_filter = ['position', 'voted_at', 'candidate']
    search_fields = [
        'voter__name', 
        'voter__reg_no', 
        'candidate__name',
        'position__title'
    ]
    readonly_fields = [
        'voter', 
        'position', 
        'candidate', 
        'voted_at', 
        'ip_address'
    ]
    ordering = ['-voted_at']

    def voter_name(self, obj):
        """Display voter name."""
        return obj.voter.name
    voter_name.short_description = 'Voter Name'

    def voter_reg_no(self, obj):
        """Display voter registration number."""
        return obj.voter.reg_no
    voter_reg_no.short_description = 'Voter Reg No'

    def has_add_permission(self, request):
        """Prevent manual vote creation through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent vote modification through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent vote deletion through admin."""
        return False


# Customize admin site headers
admin.site.site_header = "Election Voting System Admin"
admin.site.site_title = "Election Admin"
admin.site.index_title = "Welcome to Election Administration"
