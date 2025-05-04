"""
URL configuration for SevenElements project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Predictor import views
from Predictor.views import ProjectWizard

# Define the form list for the wizard
project_wizard = ProjectWizard.as_view()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('project/', views.project, name='project'),
    path('add-project/', project_wizard, name='add_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/api/', views.analytics_api, name='analytics_api'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('report/<int:project_id>/', views.generate_report, name='generate_report'),
    path('report/<int:project_id>/download/', views.download_report, name='download_report'),
    path('project-detail-final/<int:project_id>/', views.project_detail_final, name='project_detail_final'),
]