"""
Views for the Django Election Voting System.

This module contains all the views for handling voter authentication,
voting process, results display, and admin functionality.
"""

import csv
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Voter, Position, Candidate, Vote, ElectionSettings


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    """
    Home page showing election information and login form.
    """
    settings = ElectionSettings.get_settings()
    
    # Check if voter is already authenticated
    voter_token = request.session.get('voter_token')
    if voter_token:
        try:
            voter = Voter.objects.get(token=voter_token)
            if voter.has_voted:
                return redirect('voting_complete')
            else:
                return redirect('vote')
        except Voter.DoesNotExist:
            # Invalid token in session, clear it
            request.session.pop('voter_token', None)
    
    # Get active positions for display
    now = timezone.now()
    settings = ElectionSettings.get_settings()
    active_positions = Position.objects.filter(is_active=True)
    
    # Check if voting is globally open
    is_voting_open = settings.is_voting_open()
    
    # Get voter statistics
    total_voters = Voter.objects.count()
    total_voted = Voter.objects.filter(has_voted=True).count()
    turnout_percentage = 0
    if total_voters > 0:
        turnout_percentage = round((total_voted / total_voters) * 100, 1)
    
    context = {
        'settings': settings,
        'active_positions': active_positions,
        'current_time': now,
        'is_voting_open': is_voting_open,
        'total_voters': total_voters,
        'total_voted': total_voted,
        'turnout_percentage': turnout_percentage,
    }
    
    return render(request, 'voting/index.html', context)


@csrf_protect
def login_voter(request):
    """
    Handle voter login using authentication token.
    """
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if not token:
            messages.error(request, 'Please enter a valid token.')
            return redirect('index')
        
        try:
            voter = Voter.objects.get(token=token)
            
            if voter.has_voted:
                messages.info(request, 'You have already cast your vote. Thank you!')
                request.session['voter_token'] = str(voter.token)
                return redirect('voting_complete')
            
            # Store voter token in session
            request.session['voter_token'] = str(voter.token)
            messages.success(request, f'Welcome, {voter.name}!')
            return redirect('vote')
            
        except Voter.DoesNotExist:
            messages.error(request, 'Invalid token. Please check and try again.')
            return redirect('index')
    
    return redirect('index')


def logout_voter(request):
    """
    Handle voter logout.
    """
    request.session.pop('voter_token', None)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


@never_cache
def vote(request):
    """
    Main voting interface showing all active positions and candidates.
    """
    # Check if voter is authenticated
    voter_token = request.session.get('voter_token')
    if not voter_token:
        messages.error(request, 'Please log in with your token to vote.')
        return redirect('index')
    
    try:
        voter = get_object_or_404(Voter, token=voter_token)
    except:
        messages.error(request, 'Invalid session. Please log in again.')
        request.session.pop('voter_token', None)
        return redirect('index')
    
    if voter.has_voted:
        return redirect('voting_complete')
    
    # Get active positions with their candidates
    now = timezone.now()
    settings = ElectionSettings.get_settings()
    
    # Check if voting is globally open
    if not settings.is_voting_open():
        voting_status = settings.get_voting_status()
        if voting_status == "Not Started":
            messages.warning(request, f'Voting has not started yet. Voting begins at {settings.voting_start_time.strftime("%B %d, %Y at %I:%M %p")}.')
        elif voting_status == "Ended":
            messages.warning(request, 'Voting has ended.')
        else:
            messages.warning(request, 'Voting is not available at this time.')
        return render(request, 'voting/voting_closed.html', {'settings': settings})
    
    positions = Position.objects.filter(is_active=True).prefetch_related('candidates')
    
    if not positions.exists():
        messages.warning(request, 'No active voting positions at this time.')
        return render(request, 'voting/no_active_voting.html')
    
    # Prepare positions data for template
    positions_data = []
    for position in positions:
        candidates = position.candidates.filter(is_active=True)
        if candidates.exists():
            positions_data.append({
                'position': position,
                'candidates': candidates
            })
    
    if not positions_data:
        messages.warning(request, 'No candidates available for voting at this time.')
        return render(request, 'voting/no_candidates.html')
    
    context = {
        'voter': voter,
        'positions_data': positions_data,
        'current_time': now,
    }
    
    return render(request, 'voting/vote.html', context)


@csrf_protect
@require_POST
@never_cache
def submit_vote(request):
    """
    Handle vote submission with validation and fraud prevention.
    """
    # Check authentication
    voter_token = request.session.get('voter_token')
    if not voter_token:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        voter = get_object_or_404(Voter, token=voter_token)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid session'})
    
    if voter.has_voted:
        return JsonResponse({'success': False, 'error': 'You have already voted'})
    
    # Check if voting is still globally open
    settings = ElectionSettings.get_settings()
    if not settings.is_voting_open():
        return JsonResponse({
            'success': False, 
            'error': 'Voting has ended. Your vote cannot be processed.',
            'voting_ended': True
        })
    
    # Get current time and client IP
    now = timezone.now()
    client_ip = get_client_ip(request)
    
    # Parse vote selections
    vote_data = {}
    errors = []
    
    for key, value in request.POST.items():
        if key.startswith('position_') and value:
            try:
                position_id = int(key.split('_')[1])
                candidate_id = int(value)
                vote_data[position_id] = candidate_id
            except (ValueError, IndexError):
                errors.append(f"Invalid vote data: {key}")
    
    if not vote_data:
        return JsonResponse({'success': False, 'error': 'No votes selected'})
    
    if errors:
        return JsonResponse({'success': False, 'error': '; '.join(errors)})
    
    # Validate votes and create vote objects
    votes_to_create = []
    
    with transaction.atomic():
        for position_id, candidate_id in vote_data.items():
            try:
                position = Position.objects.get(id=position_id, is_active=True)
                candidate = Candidate.objects.get(id=candidate_id, is_active=True)
                
                # Check if voting is still open for this position
                if not position.is_voting_open():
                    return JsonResponse({
                        'success': False, 
                        'error': f'Voting for {position.title} is not open'
                    })
                
                # Check if candidate is contesting for this position
                if not candidate.positions.filter(id=position_id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'{candidate.name} is not contesting for {position.title}'
                    })
                
                # Check if voter has already voted for this position
                if Vote.objects.filter(voter=voter, position=position).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'You have already voted for {position.title}'
                    })
                
                # Create vote object
                vote = Vote(
                    voter=voter,
                    position=position,
                    candidate=candidate,
                    ip_address=client_ip
                )
                votes_to_create.append(vote)
                
            except (Position.DoesNotExist, Candidate.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid position or candidate'
                })
        
        # Save all votes
        Vote.objects.bulk_create(votes_to_create)
        
        # Mark voter as voted
        voter.mark_as_voted()
    
    return JsonResponse({
        'success': True,
        'message': 'Your votes have been successfully recorded!'
    })


def voting_complete(request):
    """
    Page shown after successful voting.
    """
    voter_token = request.session.get('voter_token')
    if not voter_token:
        return redirect('index')
    
    try:
        voter = get_object_or_404(Voter, token=voter_token)
    except:
        return redirect('index')
    
    if not voter.has_voted:
        return redirect('vote')
    
    context = {
        'voter': voter,
        'settings': ElectionSettings.get_settings()
    }
    
    return render(request, 'voting/voting_complete.html', context)


@never_cache
def live_results(request):
    """
    Display live voting results with auto-refresh.
    """
    settings = ElectionSettings.get_settings()
    
    if not settings.show_live_results:
        return render(request, 'voting/results_disabled.html')
    
    # Get all positions with vote counts
    positions = Position.objects.filter(is_active=True).prefetch_related(
        'candidates', 'candidates__vote_set'
    )
    
    results_data = []
    total_voters = Voter.objects.count()
    total_voted = Voter.objects.filter(has_voted=True).count()
    pending_voters = total_voters - total_voted
    
    # Check if election has ended
    now = timezone.now()
    voting_ended_by_time = settings.is_voting_ended()
    all_voters_voted = total_voters > 0 and total_voted == total_voters
    election_ended = voting_ended_by_time or all_voters_voted
    
    # Determine end reason
    end_reason = None
    if election_ended:
        if all_voters_voted:
            end_reason = "All eligible voters have cast their votes"
        elif voting_ended_by_time:
            end_reason = "Voting time period has ended"
    
    for position in positions:
        candidates_data = []
        total_votes_for_position = Vote.objects.filter(position=position).count()
        
        for candidate in position.candidates.filter(is_active=True):
            vote_count = Vote.objects.filter(
                position=position, 
                candidate=candidate
            ).count()
            
            percentage = 0
            if total_votes_for_position > 0:
                percentage = (vote_count / total_votes_for_position) * 100
            
            candidates_data.append({
                'candidate': candidate,
                'votes': vote_count,
                'percentage': round(percentage, 1)
            })
        
        # Sort by vote count (descending)
        candidates_data.sort(key=lambda x: x['votes'], reverse=True)
        
        results_data.append({
            'position': position,
            'candidates': candidates_data,
            'total_votes': total_votes_for_position,
            'status': position.get_status()
        })
    
    context = {
        'results_data': results_data,
        'total_voters': total_voters,
        'total_voted': total_voted,
        'pending_voters': pending_voters,
        'election_ended': election_ended,
        'end_reason': end_reason,
        'voting_ended_by_time': voting_ended_by_time,
        'all_voters_voted': all_voters_voted,
        'settings': settings,
        'current_time': timezone.now()
    }
    
    return render(request, 'voting/live_results.html', context)


@never_cache
def live_results_api(request):
    """
    API endpoint for live results data (JSON).
    """
    settings = ElectionSettings.get_settings()
    
    if not settings.show_live_results:
        return JsonResponse({'error': 'Live results are disabled'})
    
    # Get results data
    positions = Position.objects.filter(is_active=True)
    results = []
    
    total_voters = Voter.objects.count()
    total_voted = Voter.objects.filter(has_voted=True).count()
    
    # Check if election has ended
    now = timezone.now()
    voting_ended_by_time = settings.is_voting_ended()
    all_voters_voted = total_voters > 0 and total_voted == total_voters
    election_ended = voting_ended_by_time or all_voters_voted
    
    # Determine end reason
    end_reason = None
    if election_ended:
        if all_voters_voted:
            end_reason = "All eligible voters have cast their votes"
        elif voting_ended_by_time:
            end_reason = "Voting time period has ended"
    
    for position in positions:
        candidates_data = []
        total_votes = Vote.objects.filter(position=position).count()
        
        for candidate in position.candidates.filter(is_active=True):
            vote_count = Vote.objects.filter(
                position=position, 
                candidate=candidate
            ).count()
            
            percentage = 0
            if total_votes > 0:
                percentage = (vote_count / total_votes) * 100
            
            candidates_data.append({
                'name': candidate.name,
                'votes': vote_count,
                'percentage': round(percentage, 1)
            })
        
        candidates_data.sort(key=lambda x: x['votes'], reverse=True)
        
        results.append({
            'position': position.title,
            'candidates': candidates_data,
            'total_votes': total_votes,
            'status': position.get_status()
        })
    
    return JsonResponse({
        'results': results,
        'total_voters': total_voters,
        'total_voted': total_voted,
        'election_ended': election_ended,
        'end_reason': end_reason,
        'voting_ended_by_time': voting_ended_by_time,
        'all_voters_voted': all_voters_voted,
        'timestamp': timezone.now().isoformat()
    })


def final_results(request):
    """
    Display final election results (winners only).
    Only show results if voting has ended or all voters have voted.
    """
    # Check if final results should be visible
    total_voters = Voter.objects.count()
    total_voted = Voter.objects.filter(has_voted=True).count()
    
    # Get global voting status
    settings = ElectionSettings.get_settings()
    now = timezone.now()
    
    # Check if voting has ended globally
    voting_ended = settings.is_voting_ended()
    
    # Check if all voters have voted
    all_voters_voted = total_voters > 0 and total_voted == total_voters
    
    # Show results only if voting has ended OR all voters have voted
    can_show_results = voting_ended or all_voters_voted
    
    if not can_show_results:
        context = {
            'can_show_results': False,
            'voting_ended': voting_ended,
            'all_voters_voted': all_voters_voted,
            'total_voters': total_voters,
            'total_voted': total_voted,
            'voting_end_time': settings.voting_end_time,
            'current_time': now,
            'settings': settings
        }
        return render(request, 'voting/final_results_restricted.html', context)
    
    # Generate results data
    positions = Position.objects.filter(is_active=True)
    winners_data = []
    
    for position in positions:
        # Get candidate with most votes for this position
        votes_by_candidate = Vote.objects.filter(position=position).values(
            'candidate__name', 'candidate__reg_no'
        ).annotate(vote_count=Count('id')).order_by('-vote_count')
        
        if votes_by_candidate:
            winner = votes_by_candidate[0]
            total_votes = Vote.objects.filter(position=position).count()
            
            winners_data.append({
                'position': position,
                'winner_name': winner['candidate__name'],
                'winner_reg_no': winner['candidate__reg_no'],
                'votes': winner['vote_count'],
                'total_votes': total_votes,
                'all_candidates': list(votes_by_candidate)
            })
    
    context = {
        'can_show_results': True,
        'winners_data': winners_data,
        'total_voters': total_voters,
        'total_voted': total_voted,
        'voting_ended': voting_ended,
        'all_voters_voted': all_voters_voted,
        'settings': settings
    }
    
    return render(request, 'voting/final_results.html', context)


def is_technical_head(user):
    """
    Check if user is technical head (for audit access).
    """
    if not user.is_authenticated:
        return False
    
    settings = ElectionSettings.get_settings()
    return (
        user.is_superuser or 
        user.is_staff or
        (settings.technical_head_email and user.email == settings.technical_head_email)
    )


@staff_member_required
def audit_trail(request):
    """
    Audit trail view - restricted to staff users only.
    Shows detailed voting information for fraud detection and election oversight.
    """
    votes = Vote.objects.select_related(
        'voter', 'position', 'candidate'
    ).order_by('-voted_at')
    
    # Apply filters if provided
    position_filter = request.GET.get('position')
    if position_filter:
        votes = votes.filter(position_id=position_filter)
    
    voter_filter = request.GET.get('voter')
    if voter_filter:
        votes = votes.filter(
            Q(voter__name__icontains=voter_filter) |
            Q(voter__reg_no__icontains=voter_filter)
        )
    
    # Pagination could be added here for large datasets
    
    context = {
        'votes': votes,
        'positions': Position.objects.filter(is_active=True),
        'position_filter': position_filter,
        'voter_filter': voter_filter,
        'total_votes': votes.count(),
    }
    
    return render(request, 'voting/audit_trail.html', context)


@staff_member_required
def export_voters_csv(request):
    """
    Export voters list with tokens as CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voters_tokens.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Registration Number', 'Token', 'Has Voted', 'Voted At'])
    
    for voter in Voter.objects.all().order_by('name'):
        writer.writerow([
            voter.name,
            voter.reg_no,
            str(voter.token),
            'Yes' if voter.has_voted else 'No',
            voter.voted_at.strftime('%Y-%m-%d %H:%M:%S') if voter.voted_at else ''
        ])
    
    return response


@staff_member_required
def import_voters_csv(request):
    """
    Import voters from CSV file.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row in reader:
                name = row.get('name', '').strip()
                reg_no = row.get('reg_no', '').strip()
                
                if not name or not reg_no:
                    errors.append(f"Missing name or reg_no in row: {row}")
                    continue
                
                voter, created = Voter.objects.get_or_create(
                    reg_no=reg_no,
                    defaults={'name': name}
                )
                
                if created:
                    created_count += 1
                else:
                    voter.name = name
                    voter.save()
                    updated_count += 1
            
            messages.success(
                request, 
                f'Import completed. Created: {created_count}, Updated: {updated_count}'
            )
            
            if errors:
                for error in errors[:5]:  # Show only first 5 errors
                    messages.warning(request, error)
                if len(errors) > 5:
                    messages.warning(request, f'... and {len(errors) - 5} more errors')
                    
        except Exception as e:
            messages.error(request, f'Error importing CSV: {str(e)}')
    
    # Get current voter statistics
    total_voters = Voter.objects.count()
    voted_count = Voter.objects.filter(has_voted=True).count()
    remaining_count = total_voters - voted_count
    
    context = {
        'total_voters': total_voters,
        'voted_count': voted_count,
        'remaining_count': remaining_count,
    }
    
    return render(request, 'voting/import_voters.html', context)


def audit_required(view_func):
    """
    Decorator to check if user is authenticated for audit access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('audit_authenticated'):
            messages.warning(request, 'Audit authentication required.')
            return redirect('audit_login')
        
        # Check session timeout (2 hours)
        login_time_str = request.session.get('audit_login_time')
        if login_time_str:
            from django.utils.dateparse import parse_datetime
            login_time = parse_datetime(login_time_str)
            if login_time and (timezone.now() - login_time).total_seconds() > 7200:  # 2 hours
                # Session expired
                request.session.flush()
                messages.warning(request, 'Audit session expired. Please login again.')
                return redirect('audit_login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
