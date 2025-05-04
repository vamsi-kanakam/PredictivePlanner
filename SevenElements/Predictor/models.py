from django.db import models
from django.contrib.auth.models import User

# UserProfile model to extend the built-in User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    user_role = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Project Manager", "Developer"
    organization_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"

# Project model
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    project_title = models.CharField(max_length=200)
    project_description = models.TextField()
    project_type = models.CharField(max_length=100)
    planned_budget = models.DecimalField(max_digits=15, decimal_places=2)
    actual_budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    planned_schedule = models.IntegerField()  # In days
    planned_scope = models.TextField()
    actual_schedule = models.IntegerField(blank=True, null=True)  # In days
    actual_scope = models.TextField(blank=True, null=True)
    project_manager_title = models.CharField(max_length=100)
    project_manager_skill_level = models.CharField(max_length=50)  # e.g., "Beginner", "Intermediate", "Expert"
    project_info_score = models.FloatField(blank=True, null=True)
    resource_utilization_score = models.FloatField(blank=True, null=True)
    total_score = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_title

# TeamComposition model (One-to-One with Project)
class TeamComposition(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='team_composition')
    team_size = models.IntegerField()
    avg_experience_level = models.CharField(max_length=100)
    senior_to_junior_ratio = models.FloatField()  # e.g., 2.5 (2.5 seniors per junior)
    stability_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Team Composition for {self.project.project_title}"

# ProductivityEfficiency model (One-to-One with Project)
class ProductivityEfficiency(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='productivity_efficiency')
    expected_sprint_completion_rate = models.FloatField()  # Percentage
    task_completion_rate = models.FloatField()  # Percentage
    expected_velocity = models.FloatField()  # Story points per sprint
    estimated_cycle_time = models.IntegerField()  # In days
    defect_rate = models.FloatField()  # Defects per 1000 lines of code
    dependencies_blocked = models.IntegerField()  # Number of blocked dependencies
    productivity_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Productivity Efficiency for {self.project.project_title}"

# Risk model (One-to-One with Project)
class Risk(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='risk')
    final_risk_score = models.FloatField(blank=True, null=True)
    risk_factors = models.TextField()  # Description of risk factors

    def __str__(self):
        return f"Risk for {self.project.project_title}"

# ProjectEnvironment model (One-to-One with Project)
class ProjectEnvironment(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='project_environment')
    leadership_support = models.CharField(max_length=100)
    team_collaboration_level = models.FloatField()  # Score out of 10
    stakeholder_engagement = models.CharField(max_length=100)
    work_life_balance = models.CharField(max_length=100)
    psychological_safety_score = models.FloatField()  # Score out of 10
    resource_availability = models.CharField(max_length=100)
    turnover_rate = models.FloatField()  # Percentage
    environment_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Project Environment for {self.project.project_title}"

# TechnicalPractices model (One-to-One with Project)
class TechnicalPractices(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='technical_practices')
    development_methodology = models.CharField(max_length=100)  # e.g., "Agile", "Waterfall"
    devops_adoption = models.BooleanField(default=False)
    automated_testing_coverage = models.FloatField()  # Percentage
    cicd_pipeline_usage = models.BooleanField(default=False)
    code_review_process = models.CharField(max_length=100)
    technical_debt_level = models.CharField(max_length=100)
    cloud_based_development = models.BooleanField(default=False)
    security_practices = models.CharField(max_length=100)
    technical_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Technical Practices for {self.project.project_title}"

class ProjectReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.project.project_title}"