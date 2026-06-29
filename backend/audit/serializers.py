from rest_framework import serializers
from .models import AuditReport


class AuditReportSerializer(serializers.ModelSerializer):
    images_missing_alt_pct = serializers.SerializerMethodField()

    class Meta:
        model = AuditReport
        fields = [
            "id",
            "url",
            "created_at",
            "word_count",
            "h1_count",
            "h2_count",
            "h3_count",
            "cta_count",
            "internal_links",
            "external_links",
            "image_count",
            "images_missing_alt",
            "images_missing_alt_pct",
            "meta_title",
            "meta_description",
            "ai_insights",
            "recommendations",
            "prompt_log_file",
        ]

    def get_images_missing_alt_pct(self, obj):
        if obj.image_count == 0:
            return 0
        return round((obj.images_missing_alt / obj.image_count) * 100, 1)