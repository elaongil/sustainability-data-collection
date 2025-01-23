import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ..base.cell import BaseCell


class WikipediaExtractorCell(BaseCell):
    def validate_input(self, data):
        return 'source' in data and isinstance(data['source'], str)

    def process(self, data):
        import logging
        logger = logging.getLogger(__name__)
        
        url = data['source']
        table_index = data.get('table_index')
        
        try:
            logger.info(f"Attempting to extract tables from: {url}")
            
            try:
                # Fetch the page content
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html5lib')
                
                # Find all table elements
                all_tables = soup.find_all('table', class_='wikitable')
                logger.info(f"Found {len(all_tables)} wikitable tables")
                
                # Convert valid tables using pandas
                tables = []
                for table in all_tables:
                    try:
                        # Convert the table HTML to string and parse with pandas
                        df = pd.read_html(str(table), flavor='html5lib')[0]
                        tables.append(df)
                        logger.info("Successfully parsed table")
                    except Exception as e:
                        logger.warning(f"Failed to parse table: {str(e)}")
                        continue
                        
                logger.info(f"Successfully processed {len(tables)} tables")
            except ValueError as e:
                logger.error(f"Failed to extract tables: {str(e)}")
                return {
                    'data': {
                        'tables': [],
                        'error': "No tables found on this Wikipedia page"
                    }
                }
            except Exception as e:
                logger.error(f"Error reading HTML: {str(e)}")
                return {
                    'data': {
                        'tables': [],
                        'error': f"Failed to read tables: {str(e)}"
                    }
                }
            
            if not tables:
                logger.warning("No tables found")
                return {
                    'data': {
                        'tables': [],
                        'error': "No tables found on this Wikipedia page"
                    }
                }
                
            logger.info("Processing tables...")
            processed_tables = []
            
            for idx, table in enumerate(tables):
                if table_index is not None and idx != table_index:
                    continue
                
                try:
                    # Convert any non-string values to strings
                    table = table.astype(str)
                    
                    # Handle potential NaN values
                    table = table.fillna('')
                    
                    # Convert DataFrame to dict
                    table_dict = {
                        'index': idx,
                        'title': f'Table {idx + 1}',
                        'headers': table.columns.tolist(),
                        'data': table.values.tolist()
                    }
                    
                    processed_tables.append(table_dict)
                    logger.info(f"Processed table {idx + 1}")
                except Exception as e:
                    logger.error(f"Error processing table {idx}: {str(e)}")
                    continue
            
            if not processed_tables:
                return {
                    'data': {
                        'tables': [],
                        'error': "Failed to process any tables from the page"
                    }
                }
            
            logger.info("Preparing response...")
            response = {
                'data': {
                    'tables': processed_tables,
                    'metadata': {
                        'article_title': url.split('/')[-1],
                        'table_count': len(processed_tables),
                        'extraction_timestamp': datetime.now().isoformat()
                    },
                    'error': None
                }
            }
            
            # Verify response is JSON serializable
            try:
                import json
                json.dumps(response)
                logger.info("Response prepared successfully")
                return response
            except Exception as e:
                logger.error(f"Response serialization error: {str(e)}")
                return {
                    'data': {
                        'tables': [],
                        'error': "Failed to serialize response data"
                    }
                }
        except ValueError as e:
            return {
                'data': {
                    'tables': [],
                    'error': str(e)
                }
            }
        except Exception as e:
            return {
                'data': {
                    'tables': [],
                    'error': f"Failed to extract tables: {str(e)}"
                }
            }
