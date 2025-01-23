from django.urls import path
from .view import CDPExtractorView, AnnualReportExtractorView, CCFEstimatorView

urlpatterns = [
    path('cdp_extractor/', CDPExtractorView.as_view(), name='cdp_extractor'),
    path('ccf_estimator/', CCFEstimatorView.as_view(), name='ccf_estimator'),
    path('annual_report_extractor/', AnnualReportExtractorView.as_view(), name='annual_report_extractor'),
]
