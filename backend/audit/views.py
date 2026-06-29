from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import AuditReport
from .serializers import AuditReportSerializer
from .scraper import scrape_metrics
from .ai import run_ai_analysis


class AuditCreateView(APIView):
    """
    POST /api/audit/
    Body: { "url": "https://example.com" }
    Scrapes metrics, runs AI analysis, saves to DB, returns full report.
    """

    def post(self, request):
        url = request.data.get("url", "").strip()
        if not url:
            return Response({"error": "url is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            metrics = scrape_metrics(url)
        except Exception as e:
            return Response({"error": f"Scraping failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            ai_result = run_ai_analysis(url, metrics)
        except Exception as e:
            return Response({"error": f"AI analysis failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        report = AuditReport.objects.create(
            url=url,
            word_count=metrics["word_count"],
            h1_count=metrics["h1_count"],
            h2_count=metrics["h2_count"],
            h3_count=metrics["h3_count"],
            cta_count=metrics["cta_count"],
            internal_links=metrics["internal_links"],
            external_links=metrics["external_links"],
            image_count=metrics["image_count"],
            images_missing_alt=metrics["images_missing_alt"],
            meta_title=metrics["meta_title"],
            meta_description=metrics["meta_description"],
            ai_insights=ai_result["insights"],
            recommendations=ai_result["recommendations"],
            prompt_log_file=ai_result["prompt_log_file"],
        )

        serializer = AuditReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuditHistoryView(APIView):
    """
    GET /api/audits/
    Returns all past audit reports, newest first.
    """

    def get(self, request):
        reports = AuditReport.objects.all()
        serializer = AuditReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditDetailView(APIView):
    """
    GET /api/audits/<id>/
    Returns a single audit report by ID.
    """

    def get(self, request, pk):
        try:
            report = AuditReport.objects.get(pk=pk)
        except AuditReport.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuditReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)