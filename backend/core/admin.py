from django.contrib import admin
from .models import (
    CandidateProfile,
    Resume,
    InterviewSession,
    InterviewQuestion,
    InterviewResponse,
    ScreeningJob,
    CandidateScreening,
)

admin.site.register(CandidateProfile)
admin.site.register(Resume)
admin.site.register(InterviewSession)
admin.site.register(InterviewQuestion)
admin.site.register(InterviewResponse)
admin.site.register(ScreeningJob)
admin.site.register(CandidateScreening)
