import logging
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            # Log request details
            logger.info(f"Request Method: {request.method}")
            logger.info(f"Request Path: {request.path}")
            logger.info(f"Request Headers: {dict(request.headers)}")
            
            if request.body:
                try:
                    body = json.loads(request.body)
                    logger.info(f"Request Body: {body}")
                except json.JSONDecodeError:
                    logger.info("Request Body: <non-JSON data>")
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
        return None

    def process_response(self, request, response):
        try:
            # Log response details
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            if hasattr(response, 'content'):
                try:
                    content = json.loads(response.content)
                    logger.info(f"Response Content: {content}")
                except json.JSONDecodeError:
                    logger.info("Response Content: <non-JSON data>")
        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")
        return response
