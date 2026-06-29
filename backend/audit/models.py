from django.db import models

# Create your models here.

class AuditReport(models.Model):
    url = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)

    # Factual metrics
    word_count = models.IntegerField(default=0)
    h1_count = models.IntegerField(default=0)
    h2_count = models.IntegerField(default=0)
    h3_count = models.IntegerField(default=0)
    cta_count = models.IntegerField(default=0)
    internal_links = models.IntegerField(default=0)
    external_links = models.IntegerField(default=0)
    image_count = models.IntegerField(default=0)
    images_missing_alt = models.IntegerField(default=0)
    meta_title = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    # AI output 
    ai_insights = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)

    # Raw prompt log reference
    prompt_log_file = models.CharField(max_length=512, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.url} — {self.created_at:%Y-%m-%d %H:%M}"