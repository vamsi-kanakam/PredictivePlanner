from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Project, TeamComposition, ProductivityEfficiency, Risk, ProjectEnvironment, TechnicalPractices

# Existing forms (unchanged)
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    user_role = forms.CharField(max_length=50, required=False, label="User Role (e.g., Project Manager, Developer)")
    organization_name = forms.CharField(max_length=100, required=False, label="Organization Name")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'user_role', 'organization_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone_number=self.cleaned_data['phone_number'],
                user_role=self.cleaned_data['user_role'],
                organization_name=self.cleaned_data['organization_name']
            )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# Updated forms for the wizard
class ProjectInfoForm(forms.ModelForm):
    project_title = forms.CharField(max_length=200, required=True)
    project_description = forms.CharField(widget=forms.Textarea, required=True)
    project_type = forms.ChoiceField(
        choices=[
            ('Business System', 'Business System'),
            ('Web Application', 'Web Application'),
            ('Mobile Application', 'Mobile Application'),
            ('Data Analytics', 'Data Analytics'),
            ('AI & Machine Learning', 'AI & Machine Learning'),
            ('Embedded Systems', 'Embedded Systems'),
            ('Cloud Computing', 'Cloud Computing'),
        ],
        required=True
    )
    planned_budget = forms.DecimalField(max_digits=15, decimal_places=2, required=True, min_value=0)
    planned_schedule = forms.IntegerField(required=True, min_value=1, max_value=52)  # Weeks
    planned_scope = forms.CharField(widget=forms.Textarea, required=True)
    project_manager_title = forms.ChoiceField(
        choices=[
            ('Project Manager', 'Project Manager'),
            ('Scrum Master', 'Scrum Master'),
            ('Product Owner', 'Product Owner'),
            ('Technical Lead', 'Technical Lead')
        ],
        required=True
    )
    project_manager_skill_level = forms.IntegerField(required=True, min_value=1, max_value=5)

    class Meta:
        model = Project
        fields = ['project_title', 'project_description', 'project_type', 'planned_budget', 'planned_schedule', 'planned_scope', 'project_manager_title', 'project_manager_skill_level']

class TeamCompositionForm(forms.ModelForm):
    team_size = forms.IntegerField(required=True, min_value=1, max_value=50)
    avg_experience_level = forms.ChoiceField(
        choices=[
            ('Junior', 'Junior'),
            ('Mid-Level', 'Mid-Level'),
            ('Senior', 'Senior')
        ],
        required=True
    )
    senior_to_junior_ratio = forms.FloatField(required=True, min_value=0, max_value=5)

    class Meta:
        model = TeamComposition
        fields = ['team_size', 'avg_experience_level', 'senior_to_junior_ratio']

class ProductivityEfficiencyForm(forms.ModelForm):
    expected_sprint_completion_rate = forms.FloatField(required=True, min_value=0, max_value=100)
    task_completion_rate = forms.FloatField(required=True, min_value=0, max_value=100)
    expected_velocity = forms.FloatField(required=True, min_value=1)
    estimated_cycle_time = forms.IntegerField(required=True, min_value=1, max_value=30)
    defect_rate = forms.FloatField(required=True, min_value=0, max_value=100)
    dependencies_blocked = forms.IntegerField(required=True, min_value=0, max_value=50)

    class Meta:
        model = ProductivityEfficiency
        fields = ['expected_sprint_completion_rate', 'task_completion_rate', 'expected_velocity', 'estimated_cycle_time', 'defect_rate', 'dependencies_blocked']

class ProjectEnvironmentForm(forms.ModelForm):
    leadership_support = forms.ChoiceField(
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High')
        ],
        required=True
    )
    team_collaboration_level = forms.FloatField(required=True, min_value=1, max_value=10)
    stakeholder_engagement = forms.ChoiceField(
        choices=[
            ('Weak', 'Weak'),
            ('Moderate', 'Moderate'),
            ('Strong', 'Strong')
        ],
        required=True
    )
    work_life_balance = forms.ChoiceField(
        choices=[
            ('50', '50'),
            ('45', '45'),
            ('40', '40')
        ],
        required=True
    )
    psychological_safety_score = forms.FloatField(required=True, min_value=1, max_value=10)
    resource_availability = forms.ChoiceField(
        choices=[
            ('Adequate', 'Adequate'),
            ('Limited', 'Limited'),
            ('Insufficient', 'Insufficient')
        ],
        required=True
    )
    turnover_rate = forms.FloatField(required=True, min_value=0, max_value=100)

    class Meta:
        model = ProjectEnvironment
        fields = ['leadership_support', 'team_collaboration_level', 'stakeholder_engagement', 'work_life_balance', 'psychological_safety_score', 'resource_availability', 'turnover_rate']

class TechnicalPracticesForm(forms.ModelForm):
    development_methodology = forms.ChoiceField(
        choices=[
            ('Agile', 'Agile'),
            ('Waterfall', 'Waterfall'),
            ('Kanban', 'Kanban')
        ],
        required=True
    )
    devops_adoption = forms.BooleanField(required=False)
    automated_testing_coverage = forms.FloatField(required=True, min_value=0, max_value=100)
    cicd_pipeline_usage = forms.BooleanField(required=False)
    code_review_process = forms.ChoiceField(
        choices=[
            ('none', 'none'),
            ('Ad Hoc', 'Ad Hoc'),
            ('Formal', 'Formal')
        ],
        required=True
    )
    technical_debt_level = forms.ChoiceField(
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High')
        ],
        required=True
    )
    cloud_based_development = forms.BooleanField(required=False)
    security_practices = forms.ChoiceField(
        choices=[
            ('Basic', 'Basic'),
            ('Moderate', 'Moderate'),
            ('Advanced', 'Advanced')
        ],
        required=True
    )

    class Meta:
        model = TechnicalPractices
        fields = ['development_methodology', 'devops_adoption', 'automated_testing_coverage', 'cicd_pipeline_usage', 'code_review_process', 'technical_debt_level', 'cloud_based_development', 'security_practices']