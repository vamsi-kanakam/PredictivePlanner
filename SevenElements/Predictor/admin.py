from django.contrib import admin
from .models import UserProfile, Project, TeamComposition, ProductivityEfficiency, Risk, ProjectEnvironment, TechnicalPractices

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(TeamComposition)
admin.site.register(ProductivityEfficiency)
admin.site.register(Risk)
admin.site.register(ProjectEnvironment)
admin.site.register(TechnicalPractices)