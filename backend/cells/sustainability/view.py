from ..base.cell import BaseCellView
from .services import CDPExtractorCell, CCFEstimatorCell, AnnualReportExtractorCell
from rest_framework.parsers import MultiPartParser


class CDPExtractorView(BaseCellView):
    parser_classes = [MultiPartParser]
    cell_class = CDPExtractorCell


class CCFEstimatorView(BaseCellView):
    cell_class = CCFEstimatorCell


class AnnualReportExtractorView(BaseCellView):
    parser_classes = [MultiPartParser]
    cell_class = AnnualReportExtractorCell
