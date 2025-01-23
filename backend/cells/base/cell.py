from abc import ABC, abstractmethod
from rest_framework.views import APIView
from rest_framework.response import Response


class BaseCell(ABC):
    @abstractmethod
    def process(self, data):
        """Process the input data according to cell's functionality"""
        pass

    @abstractmethod
    def validate_input(self, data):
        """Validate the input data"""
        pass


class BaseCellView(APIView):
    cell_class = None  # To be set by implementing cells

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log request data for debugging
            logger.info(f"Received request data: {request.data}")
            
            if not request.data:
                return Response({
                    'data': {
                        'tables': [],
                        'error': 'No data provided in request'
                    }
                }, status=400)

            cell = self.cell_class()
            
            # Validate input
            if not cell.validate_input(request.data):
                return Response({
                    'data': {
                        'tables': [],
                        'error': 'Invalid input data format'
                    }
                }, status=400)
            
            try:
                # Process the request
                result = cell.process(request.data)
                
                # Validate response data
                if not isinstance(result, dict):
                    logger.error(f"Invalid response format: {result}")
                    return Response({
                        'data': {
                            'tables': [],
                            'error': 'Invalid response format from cell'
                        }
                    }, status=500)
                
                # Ensure response has the expected structure
                if not isinstance(result, dict) or 'data' not in result:
                    logger.error(f"Invalid response format: {result}")
                    return Response({
                        'data': {
                            'tables': [],
                            'error': 'Invalid response format from cell'
                        }
                    }, status=500)

                # Log successful response
                logger.info("Successfully processed request")
                logger.info(f"Response data: {result}")
                
                # Return the result directly since it already has the correct structure
                return Response(result, status=200)
                
            except ValueError as e:
                logger.error(f"Value error in cell processing: {str(e)}")
                return Response({
                    'data': {
                        'tables': [],
                        'error': str(e)
                    }
                }, status=400)
            except Exception as e:
                logger.error(f"Unexpected error in cell processing: {str(e)}", exc_info=True)
                return Response({
                    'data': {
                        'tables': [],
                        'error': 'Internal server error while processing request'
                    }
                }, status=500)
                
        except Exception as e:
            logger.error(f"Base cell error: {str(e)}", exc_info=True)
            return Response({
                'data': {
                    'tables': [],
                    'error': 'Internal server error'
                }
            }, status=500)
