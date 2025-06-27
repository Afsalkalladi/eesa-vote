"""
URL configuration for the voting app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main voting pages
    path('', views.index, name='index'),
    path('login/', views.login_voter, name='login_voter'),
    path('logout/', views.logout_voter, name='logout_voter'),
    path('vote/', views.vote, name='vote'),
    path('submit-vote/', views.submit_vote, name='submit_vote'),
    path('voting-complete/', views.voting_complete, name='voting_complete'),
    
    # Results pages
    path('live-results/', views.live_results, name='live_results'),
    path('api/live-results/', views.live_results_api, name='live_results_api'),
    path('final-results/', views.final_results, name='final_results'),
    
    # Admin and audit
    path('audit/', views.audit_trail, name='audit_trail'),
    path('export-voters/', views.export_voters_csv, name='export_voters_csv'),
    path('import-voters/', views.import_voters_csv, name='import_voters_csv'),
]
