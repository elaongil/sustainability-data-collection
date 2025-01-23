from ..base.cell import BaseCellView
from .services import WikipediaExtractorCell


class WikipediaExtractorView(BaseCellView):
    cell_class = WikipediaExtractorCell
