from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView
from .forms import RegistrationForm, LoginForm, ProjectInfoForm, TeamCompositionForm, ProductivityEfficiencyForm, ProjectEnvironmentForm, TechnicalPracticesForm
from .models import Project, TeamComposition, ProductivityEfficiency, Risk, ProjectEnvironment, TechnicalPractices, ProjectReport
from django.contrib import messages
import csv
from ML__Model import ML_Model
from openai import OpenAI
import csv
import json
import tempfile
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from django.conf import settings
import markdown

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 != password2:
                messages.error(request, 'Confirmation password does not match.')
                return render(request, 'register.html', {'form': form})
            form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def project(request):
    projects_list = Project.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(projects_list, 5)  # Show 5 projects per page

    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    return render(request, 'project.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    return render(request, 'project_detail.html', {'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == "POST":
        project_title = project.project_title
        project.delete()
        messages.success(request, f"Project '{project_title}' has been deleted successfully.")
        return redirect('project')
    return redirect('project')

@login_required
def analytics(request):
    # Fetch all projects for the logged-in user
    projects = Project.objects.filter(user=request.user).order_by('-created_at')

    
    # Calculate success and failure counts
    success_projects = 0
    failed_projects = 0

    for project in projects:
        if project.total_score>=6:
            success_projects += 1
        else:
            failed_projects += 1

    # Calculate overall analytics
    total_projects = projects.count()
    if total_projects > 0:
        avg_total_score = sum(project.total_score for project in projects if project.total_score is not None) / total_projects
        avg_project_info_score = sum(project.project_info_score for project in projects if project.project_info_score is not None) / total_projects
        avg_resource_utilization_score = sum(project.resource_utilization_score for project in projects if project.resource_utilization_score is not None) / total_projects
        avg_stability_score = sum(project.team_composition.stability_score for project in projects if hasattr(project, 'team_composition') and project.team_composition.stability_score is not None) / total_projects
        avg_productivity_score = sum(project.productivity_efficiency.productivity_score for project in projects if hasattr(project, 'productivity_efficiency') and project.productivity_efficiency.productivity_score is not None) / total_projects
        avg_risk_score = sum(project.risk.final_risk_score for project in projects if hasattr(project, 'risk') and project.risk.final_risk_score is not None) / total_projects
        avg_environment_score = sum(project.project_environment.environment_score for project in projects if hasattr(project, 'project_environment') and project.project_environment.environment_score is not None) / total_projects
        avg_technical_score = sum(project.technical_practices.technical_score for project in projects if hasattr(project, 'technical_practices') and project.technical_practices.technical_score is not None) / total_projects
    else:
        avg_total_score = 0
        avg_project_info_score = 0
        avg_resource_utilization_score = 0
        avg_stability_score = 0
        avg_productivity_score = 0
        avg_risk_score = 0
        avg_environment_score = 0
        avg_technical_score = 0

    context = {
        'projects': projects,
        'total_projects': total_projects,
        'avg_total_score': round(avg_total_score, 2),
        'avg_project_info_score': round(avg_project_info_score, 2),
        'avg_resource_utilization_score': round(avg_resource_utilization_score, 2),
        'avg_stability_score': round(avg_stability_score, 2),
        'avg_productivity_score': round(avg_productivity_score, 2),
        'avg_risk_score': round(avg_risk_score, 2),
        'avg_environment_score': round(avg_environment_score, 2),
        'avg_technical_score': round(avg_technical_score, 2),
        'success_projects': success_projects,
        'failed_projects': failed_projects,
    }
    return render(request, 'analytics.html', context)

@login_required
def analytics_api(request):
    # Fetch all projects for the logged-in user
    projects = Project.objects.filter(user=request.user).order_by('-created_at')

    # Calculate overall analytics
    total_projects = projects.count()

     # Calculate success and failure counts
    success_projects = 0
    failed_projects = 0

    for project in projects:
        if project.total_score>=6:
            success_projects += 1
        else:
            failed_projects += 1

    if total_projects > 0:
        avg_total_score = sum(project.total_score for project in projects if project.total_score is not None) / total_projects
        avg_project_info_score = sum(project.project_info_score for project in projects if project.project_info_score is not None) / total_projects
        avg_resource_utilization_score = sum(project.resource_utilization_score for project in projects if project.resource_utilization_score is not None) / total_projects
        avg_stability_score = sum(project.team_composition.stability_score for project in projects if hasattr(project, 'team_composition') and project.team_composition.stability_score is not None) / total_projects
        avg_productivity_score = sum(project.productivity_efficiency.productivity_score for project in projects if hasattr(project, 'productivity_efficiency') and project.productivity_efficiency.productivity_score is not None) / total_projects
        avg_risk_score = sum(project.risk.final_risk_score for project in projects if hasattr(project, 'risk') and project.risk.final_risk_score is not None) / total_projects
        avg_environment_score = sum(project.project_environment.environment_score for project in projects if hasattr(project, 'project_environment') and project.project_environment.environment_score is not None) / total_projects
        avg_technical_score = sum(project.technical_practices.technical_score for project in projects if hasattr(project, 'technical_practices') and project.technical_practices.technical_score is not None) / total_projects
    else:
        avg_total_score = 0
        avg_project_info_score = 0
        avg_resource_utilization_score = 0
        avg_stability_score = 0
        avg_productivity_score = 0
        avg_risk_score = 0
        avg_environment_score = 0
        avg_technical_score = 0

    # Prepare project details
    project_data = []
    for project in projects:
        project_data.append({
            'id': project.id,
            'project_title': project.project_title,
            'total_score': project.total_score if project.total_score is not None else "N/A",
            'project_info_score': project.project_info_score if project.project_info_score is not None else "N/A",
            'resource_utilization_score': project.resource_utilization_score if project.resource_utilization_score is not None else "N/A",
            'stability_score': project.team_composition.stability_score if hasattr(project, 'team_composition') and project.team_composition.stability_score is not None else "N/A",
            'productivity_score': project.productivity_efficiency.productivity_score if hasattr(project, 'productivity_efficiency') and project.productivity_efficiency.productivity_score is not None else "N/A",
            'risk_score': project.risk.final_risk_score if hasattr(project, 'risk') and project.risk.final_risk_score is not None else "N/A",
            'environment_score': project.project_environment.environment_score if hasattr(project, 'project_environment') and project.project_environment.environment_score is not None else "N/A",
            'technical_score': project.technical_practices.technical_score if hasattr(project, 'technical_practices') and project.technical_practices.technical_score is not None else "N/A",
            'created_at': project.created_at.isoformat(),  # Include created_at for trends
        
        })

    data = {
        'total_projects': total_projects,
        'avg_total_score': round(avg_total_score, 2),
        'avg_project_info_score': round(avg_project_info_score, 2),
        'avg_resource_utilization_score': round(avg_resource_utilization_score, 2),
        'avg_stability_score': round(avg_stability_score, 2),
        'avg_productivity_score': round(avg_productivity_score, 2),
        'avg_risk_score': round(avg_risk_score, 2),
        'avg_environment_score': round(avg_environment_score, 2),
        'avg_technical_score': round(avg_technical_score, 2),
        'projects': project_data,
        'success_projects': success_projects,
        'failed_projects': failed_projects,
    }
    return JsonResponse(data)

# Form Wizard for adding a project
class ProjectWizard(SessionWizardView):
    form_list = [
        ('project_info', ProjectInfoForm),
        ('team_composition', TeamCompositionForm),
        ('productivity_efficiency', ProductivityEfficiencyForm),
        ('project_environment', ProjectEnvironmentForm),
        ('technical_practices', TechnicalPracticesForm),
    ]
    template_name = 'add_project_wizard.html'

    def get_form_initial(self, step):
        # Optionally, you can pre-fill form fields here if needed
        return {}
    
    def insertProjectDataToCSV(project_info,team_composition,productivity_efficiency,project_environment,technical_practices):
        CSV_FILE_PATH = "test_dataset.csv"

        # Define the column order exactly as it should be in the CSV

        features = ['project_title', 'Project Type', 'Planned Budget ($)', 'Planned Schedule (Weeks)', 'Planned Scope (Story Points)',
                'Project Manager Title', 'Project Manager Skill Level', 'Leadership Support', 'Team Collaboration Level',
                'Stakeholder Engagement', 'Work-Life Balance (hrs/week)', 'Psychological Safety Score',
                'Resource Availability', 'Turnover Rate (%)', 'Development Methodology', 'DevOps Adoption',
                'Automated Testing Coverage (%)', 'CI/CD Pipeline Usage', 'Code Review Process', 'Technical Debt Level',
                'Cloud-Based Development', 'Security Practices', 'Team Size', 'Average Experience Level',
                'Senior to Junior Ratio', 'Expected Sprint Completion Rate (%)', 'Task Completion Rate (%)',
                'Expected Velocity (Story Points per Sprint)', 'Estimated Cycle Time (Days per Task)',
                'Defect Rate (Bugs per KLOC)', 'Number of Dependencies Blocked'
        ]
        
        project_data = {
                    "project_title": project_info["project_title"],
                    "Project Type": project_info['project_type'],
                    "Planned Budget ($)": project_info['planned_budget'],
                    "Planned Schedule (Weeks)": project_info['planned_schedule'],
                    "Planned Scope (Story Points)": project_info['planned_scope'],
                    "Project Manager Title": project_info['project_manager_title'],
                    "Project Manager Skill Level": project_info['project_manager_skill_level'],

                    "Leadership Support": project_environment['leadership_support'],
                    "Team Collaboration Level": project_environment['team_collaboration_level'],
                    "Stakeholder Engagement": project_environment['stakeholder_engagement'],
                    "Work-Life Balance (hrs/week)": project_environment['work_life_balance'],
                    "Psychological Safety Score": project_environment['psychological_safety_score'],
                    "Resource Availability": project_environment['resource_availability'],
                    "Turnover Rate (%)": project_environment['turnover_rate'],

                    "Development Methodology": technical_practices['development_methodology'],
                    "DevOps Adoption": "Yes" if technical_practices['devops_adoption'] else "No",
                    #"DevOps Adoption": technical_practices['devops_adoption'],
                    "Automated Testing Coverage (%)": technical_practices['automated_testing_coverage'],
                    "CI/CD Pipeline Usage": "Yes" if technical_practices['cicd_pipeline_usage'] else "No",
                    #"CI/CD Pipeline Usage": technical_practices['cicd_pipeline_usage'],
                    "Code Review Process": technical_practices['code_review_process'],
                    "Technical Debt Level": technical_practices['technical_debt_level'],
                    "Cloud-Based Development": "Yes" if technical_practices['cloud_based_development'] else "No",
                    #"Cloud-Based Development": technical_practices['cloud_based_development'],
                    "Security Practices": technical_practices['security_practices'],

                    "Team Size": team_composition['team_size'],
                    "Average Experience Level": team_composition['avg_experience_level'],
                    "Senior to Junior Ratio": team_composition['senior_to_junior_ratio'],

                    "Expected Sprint Completion Rate (%)": productivity_efficiency['expected_sprint_completion_rate'],
                    "Task Completion Rate (%)": productivity_efficiency['task_completion_rate'],
                    "Expected Velocity (Story Points per Sprint)": productivity_efficiency['expected_velocity'],
                    "Estimated Cycle Time (Days per Task)": productivity_efficiency['estimated_cycle_time'],
                    "Defect Rate (Bugs per KLOC)": productivity_efficiency['defect_rate'],
                    "Number of Dependencies Blocked": productivity_efficiency['dependencies_blocked']
        }
        
        # Append data to InputData CSV
        with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=features)
            writer.writerow(project_data)  # Append new row


    def done(self, form_list, **kwargs):
        # Extract data from all forms
        project_info = self.get_cleaned_data_for_step('project_info')
        team_composition = self.get_cleaned_data_for_step('team_composition')
        productivity_efficiency = self.get_cleaned_data_for_step('productivity_efficiency')
        project_environment = self.get_cleaned_data_for_step('project_environment')
        technical_practices = self.get_cleaned_data_for_step('technical_practices')

        # inserting data into csv
        ProjectWizard.insertProjectDataToCSV(project_info,team_composition,productivity_efficiency,project_environment,technical_practices)

        scores_from_ml_model = ML_Model()
        
        # Save the Project
        project = Project.objects.create(
            user=self.request.user,
            project_title=project_info['project_title'],
            project_description=project_info['project_description'],
            project_type=project_info['project_type'],
            planned_budget=project_info['planned_budget'],
            planned_schedule=project_info['planned_schedule'],
            planned_scope=project_info['planned_scope'],
            project_manager_title=project_info['project_manager_title'],
            project_manager_skill_level=project_info['project_manager_skill_level'],
            project_info_score=scores_from_ml_model[0],
            resource_utilization_score=scores_from_ml_model[5],
            total_score=scores_from_ml_model[7]
        )

        # Save TeamComposition
        TeamComposition.objects.create(
            project=project,
            team_size=team_composition['team_size'],
            avg_experience_level=team_composition['avg_experience_level'],
            senior_to_junior_ratio=team_composition['senior_to_junior_ratio'],
            stability_score=scores_from_ml_model[3]
        )

        # Save ProductivityEfficiency
        ProductivityEfficiency.objects.create(
            project=project,
            expected_sprint_completion_rate=productivity_efficiency['expected_sprint_completion_rate'],
            task_completion_rate=productivity_efficiency['task_completion_rate'],
            expected_velocity=productivity_efficiency['expected_velocity'],
            estimated_cycle_time=productivity_efficiency['estimated_cycle_time'],
            defect_rate=productivity_efficiency['defect_rate'],
            dependencies_blocked=productivity_efficiency['dependencies_blocked'],
            productivity_score=scores_from_ml_model[4]
        )

        # Save Risk (with default value since Risk Factors is not in the form)
        Risk.objects.create(
            project=project,
            risk_factors="Not specified",
            final_risk_score=scores_from_ml_model[6]
        )

        # Save ProjectEnvironment
        ProjectEnvironment.objects.create(
            project=project,
            leadership_support=project_environment['leadership_support'],
            team_collaboration_level=project_environment['team_collaboration_level'],
            stakeholder_engagement=project_environment['stakeholder_engagement'],
            work_life_balance=project_environment['work_life_balance'],
            psychological_safety_score=project_environment['psychological_safety_score'],
            resource_availability=project_environment['resource_availability'],
            turnover_rate=project_environment['turnover_rate'],
            environment_score=scores_from_ml_model[2]
        )

        # Save TechnicalPractices
        TechnicalPractices.objects.create(
            project=project,
            development_methodology=technical_practices['development_methodology'],
            devops_adoption=technical_practices['devops_adoption'],
            automated_testing_coverage=technical_practices['automated_testing_coverage'],
            cicd_pipeline_usage=technical_practices['cicd_pipeline_usage'],
            code_review_process=technical_practices['code_review_process'],
            technical_debt_level=technical_practices['technical_debt_level'],
            cloud_based_development=technical_practices['cloud_based_development'],
            security_practices=technical_practices['security_practices'],
            technical_score=scores_from_ml_model[2]
        )

        messages.success(self.request, 'Project added successfully!')

        return redirect('project')
    


def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def contact_us(request):
    return render(request, 'contact_us.html')

@login_required
def generate_report(request, project_id):
    # Fetch project data
    project = Project.objects.get(id=project_id, user=request.user)
    team_composition = project.team_composition
    project_environment = project.project_environment
    technical_practices = project.technical_practices
    productivity_efficiency = project.productivity_efficiency
    productivity = project.productivity_efficiency
    risk = project.risk
    environment = project.project_environment
    technical = project.technical_practices

    total_score = project.total_score

    # Prepare data for ChatGPT
    # project_data = {
    #     "project_description": project.project_description,
    #     "project_title": project.project_title,
    #     "planned_budget": float(project.planned_budget),
    #     "planned_schedule": project.planned_schedule,
    #     "total_score": project.total_score or "N/A",
    #     "risk_score": risk.final_risk_score or "N/A",
    #     "risk_factors": risk.risk_factors,
    #     "team_size": team_composition.team_size,
    #     "stability_score": team_composition.stability_score or "N/A",
    #     "productivity_score": productivity.productivity_score or "N/A",
    #     "sprint_completion_rate": productivity.expected_sprint_completion_rate,
    #     "environment_score": environment.environment_score or "N/A",
    #     "technical_score": technical.technical_score or "N/A",
    #     "development_methodology": technical.development_methodology,
    # }
    project_data = {
        "project_title": project.project_title,
        "project_description": project.project_description,
        "planned_budget": float(project.planned_budget),
        "planned_schedule": project.planned_schedule,

        "risk_factors": risk.risk_factors,

        "team_size": team_composition.team_size,
        "avg_experience_level": team_composition.avg_experience_level,
        "senior_to_junior_ratio": team_composition.senior_to_junior_ratio,

        "sprint_completion_rate": productivity_efficiency.expected_sprint_completion_rate,
        "task_completion_rate": productivity_efficiency.task_completion_rate,
        "expected_velocity": productivity_efficiency.expected_velocity,
        "estimated_cycle_time": productivity_efficiency.estimated_cycle_time,
        "defect_rate": productivity_efficiency.defect_rate,
        "dependencies_blocked": productivity_efficiency.dependencies_blocked,

        "leadership_support": project_environment.leadership_support,
        "team_collaboration_level": project_environment.team_collaboration_level,
        "stakeholder_engagement": project_environment.stakeholder_engagement,
        "work_life_balance": project_environment.work_life_balance,
        "resource_availability": project_environment.resource_availability,
        "turnover_rate": project_environment.turnover_rate,

        "development_methodology": technical_practices.development_methodology,
        "devops_adoption": "Yes" if technical_practices.devops_adoption else "No",
        "automated_testing_coverage": technical_practices.automated_testing_coverage,
        "cicd_pipeline_usage": "Yes" if technical_practices.cicd_pipeline_usage else "No",
        "code_review_process": technical_practices.code_review_process,
        "technical_debt_level": technical_practices.technical_debt_level,
        "cloud_based_development": "Yes" if technical_practices.cloud_based_development else "No",
        "security_practices": technical_practices.security_practices
    }




    try:
        score = float(total_score)
        if score > 6:
            outcome_message = "**🎉 Project Evaluation Summary:**\n\n🎊 **Congratulations!** The project is progressing well with a strong total score of {:.1f}.\nKeep up the great work and celebrate this success! 🚀".format(
                score)
            score_status = "success"
        else:
            outcome_message = "**⚠️ Project Evaluation Summary:**\n\n❗ The project has a lower score of {:.1f}. Focus on improving key areas like risk management, productivity, and team dynamics for better outcomes.".format(
                score)
            score_status = "failure"
    except ValueError:
        outcome_message = "**ℹ️ Project Evaluation Summary:**\n\n⚠️ Total score not available. Unable to determine overall success level."
        score_status = "unknown"

    # Initialize OpenAI client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # # Create prompt for ChatGPT
    # # prompt = f"""
    # #         {outcome_message}

    # #         You are a project management expert. Generate a detailed report for the following project based on the provided data. The report should include:
    # #         1. Project Overview: Summarize the project title, budget, and schedule.
    # #         2. Risk Analysis: Highlight key risks and their scores, with mitigation recommendations.
    # #         3. Team and Productivity: Assess team composition and productivity metrics.
    # #         4. Environment and Technical Practices: Evaluate the project environment and technical practices.
    # #         5. Recommendations: Provide actionable suggestions to improve project success.

    # #         Ensure the report is professional, concise, well-structured, and formatted using Markdown (use ** for bold, - for bullet points, and line breaks between paragraphs).

    # #         Project Data:
    # #         {json.dumps(project_data, indent=2)}
    # #         """

    prompt = f"""
            I want you to generate a professional Project Estimation Report using the following project input details. Structure the report with clear sections:

            Project Overview

            Scope Summary

            Estimation Method

            Effort & Time Estimation

            Cost Estimation

            Schedule (Timeline)

            Risks & Mitigation

            Resources Required

            Project Inputs: {json.dumps(project_data, indent=2)}
            
            Generate effort, time, and cost estimations based on these inputs using historical patterns and expert logic. Include assumptions and identify risks with mitigation strategies.

            Display any formulaes used as text and not use any styling decorators.
            """

    # Call ChatGPT API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional report generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        raw_report = response.choices[0].message.content
        report_content = markdown.markdown(raw_report)
    except Exception as e:
        report_content = f"Error generating report: {str(e)}"

    # Save or return the report
    context = {
        "project": project,
        "report": report_content,
        "score_status": score_status
    }

    ProjectReport.objects.create(project=project, content=report_content)
    return render(request, "report.html", context)

@login_required
def download_report(request, project_id):
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return HttpResponseNotFound("Project not found.")

    try:
        report = ProjectReport.objects.filter(project=project).latest('created_at')
    except ProjectReport.DoesNotExist:
        return HttpResponseNotFound("No report available for this project.")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()

    # Customize styles to match the reference document
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Title'], fontSize=24, spaceAfter=30, leading=26))
    styles.add(ParagraphStyle(name='CustomHeading1', parent=styles['Heading1'], fontSize=16, spaceBefore=20, spaceAfter=15, leading=18))
    styles.add(ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, leading=16))
    styles.add(ParagraphStyle(name='CustomNormal', parent=styles['Normal'], fontSize=12, spaceAfter=10, leading=14))
    styles.add(ParagraphStyle(name='CustomBullet', parent=styles['Normal'], fontSize=12, leftIndent=20, spaceAfter=8, bulletIndent=10))
    styles.add(ParagraphStyle(name='CustomCode', parent=styles['Code'], fontSize=12, spaceAfter=10))

    elements = []

    # Main Title: "Project Report: SmartTasker"
    title = f"Project Report: {project.project_title}"
    elements.append(Paragraph(title, styles['CustomTitle']))
    elements.append(Spacer(1, 30))  # Space after the main title

    # Process report content to match the reference formatting
    content_lines = report.content.split('\n')
    for i, line in enumerate(content_lines):
        line = line.strip()
        if not line:  # Skip empty lines but add a small spacer
            elements.append(Spacer(1, 10))
            continue
        if line.startswith("##"):  # Main section headings (e.g., "1. PROJECT OVERVIEW")
            heading_text = line.replace("##", "").strip().upper()  # Ensure uppercase
            elements.append(Paragraph(heading_text, styles['CustomHeading1']))
            elements.append(Spacer(1, 15))
        elif line.startswith("-"):  # Bullet points
            bullet_text = line[1:].strip()  # Remove the "-"
            elements.append(Paragraph(f"• {bullet_text}", styles['CustomBullet']))
        elif line.startswith("PROJECT TITLE:") or line.startswith("BUDGET:") or line.startswith("SCHEDULE:") or line.startswith("TEAM SIZE:") or line.startswith("ENVIRONMENT SCORE:") or line.startswith("TECHNICAL SCORE:"):
            # Bold labels like "TEAM SIZE:", "ENVIRONMENT SCORE:", etc.
            label, value = line.split(":", 1)
            elements.append(Paragraph(f"<b>{label}:</b>{value}", styles['CustomNormal']))
            elements.append(Spacer(1, 10))
        elif line.isupper() and line.endswith(":"):  # Subheadings like "PRODUCTIVITY METRICS:", "KEY RISKS:"
            elements.append(Paragraph(line, styles['CustomHeading2']))
            elements.append(Spacer(1, 8))
        elif "|" in line:  # Table-like lines
            elements.append(Paragraph(line.replace("|", " | "), styles['CustomCode']))
            elements.append(Spacer(1, 10))
        else:  # Regular paragraph text
            elements.append(Paragraph(line, styles['CustomNormal']))
            elements.append(Spacer(1, 10))

    # Build the PDF
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{project.project_title}.pdf"'
    return response
@login_required
def project_detail_final(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    return render(request, 'project_detail_final.html', {'project': project})