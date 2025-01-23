import os
import tempfile
import pandas as pd
import logging
import shutil
from datetime import datetime

from cells.base.helpers import clear_directory
from ..base.cell import BaseCell
from ..base.serializers import FileUploadSerializer
from .data_extraction import process_cdp_report
# from get_ccf_data import get_ongil_ccf_estimates, generate_explainability_text

from config.settings import MEDIA_ROOT
UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'app_files')


class CDPExtractorCell(BaseCell):

    def validate_input(self, data):
        serializer = FileUploadSerializer(data=data)
        if serializer.is_valid():
            return True
        else:
            return False

    def process(self, data):

        logger = logging.getLogger(__name__)

        serializer = FileUploadSerializer(data=data)
        if serializer.is_valid():
            pass
        session_id = serializer.validated_data.get('session_id')
        files = serializer.validated_data.get('files')

        logger.info("Deleting folder if exists for processing...")
        clear_directory(f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}")

        logger.info("Creating folder for processing...")
        input_folder_path = f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}/input"
        output_folder_path = f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}/output"
        config_path = f"{MEDIA_ROOT}/required/beverage_config.xlsx"
        os.makedirs(input_folder_path, exist_ok=True)
        os.makedirs(output_folder_path, exist_ok=True)

        try:
            logger.info("Writing files to the inputs folder...")
            # Write files to the inputs folder

            for file in files:
                if "config" in file.name:
                    with open(config_path, "wb") as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                else:
                    with open(f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}/input/{file.name}", "wb") as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

            logger.info("Processing files...")

            try:
                df = process_cdp_report(input_folder_path, output_folder_path, config_path)
            except Exception as e:
                logger.error(f"Error processing CDP report: {str(e)}")
                return {
                    'data': {
                        'output_path': None,
                        'error': f"Error processing CDP report: {str(e)}"
                    }
                }

            # Write the dataframe to the output folder
            output_file_path = os.path.join(output_folder_path, 'cdp-report.xlsx')
            try:
                logger.info("Writing output DataFrame to Excel file...")
                df.to_excel(output_file_path, index=False)
            except Exception as e:
                logger.error(f"Error writing output file: {str(e)}")
                return {
                    'data': {
                        'output_path': None,
                        'error': f"Error writing output file: {str(e)}"
                    }
                }

            logger.info("Process completed successfully.")
            return {
                'data': {
                    'output_path': output_file_path,
                    'metadata': {
                        'file_count': len(files),
                        'output_folder': output_folder_path,
                        'extraction_timestamp': datetime.now().isoformat()
                    },
                    'error': None
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'data': {
                    'output_path': None,
                    'error': f"Unexpected error: {str(e)}"
                }
            }


class AnnualReportExtractorCell(BaseCell):
    def validate_input(self, data):
        return 'files' in data and isinstance(data['files'], list) and all(hasattr(file, 'read') for file in data['files'])

    def process(self, data):

        logger = logging.getLogger(__name__)

        files = data['files']

        try:
            logger.info("Creating temporary folder for processing...")
            with tempfile.TemporaryDirectory(delete = False) as temp_folder:
                inputs_folder = os.path.join(temp_folder, 'inputs')
                output_folder = os.path.join(temp_folder, 'output')

                os.makedirs(inputs_folder, exist_ok=True)
                os.makedirs(output_folder, exist_ok=True)

                # Write files to the inputs folder
                logger.info("Writing files to the inputs folder...")
                for file in files:
                    file_path = os.path.join(inputs_folder, file.name)
                    with open(file_path, 'wb') as f:
                        shutil.copyfileobj(file, f)

                logger.info("Processing files...")
                try:
                    df = process_annual_report(inputs_folder, output_folder, config_path)
                except Exception as e:
                    logger.error(f"Error processing Annual report: {str(e)}")
                    return {
                        'data': {
                            'output_path': None,
                            'error': f"Error processing Annual report: {str(e)}"
                        }
                    }

                # Write the dataframe to the output folder
                output_file_path = os.path.join(output_folder, 'annual-report.xlsx')
                try:
                    logger.info("Writing output DataFrame to Excel file...")
                    df.to_excel(output_file_path, index=False)
                except Exception as e:
                    logger.error(f"Error writing output file: {str(e)}")
                    return {
                        'data': {
                            'output_path': None,
                            'error': f"Error writing output file: {str(e)}"
                        }
                    }

                logger.info("Process completed successfully.")
                return {
                    'data': {
                        'output_path': output_file_path,
                        'metadata': {
                            'file_count': len(files),
                            'output_folder': output_folder,
                            'extraction_timestamp': datetime.now().isoformat()
                        },
                        'error': None
                    }
                }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'data': {
                    'output_path': None,
                    'error': f"Unexpected error: {str(e)}"
                }
            }


class CCFEstimatorCell(BaseCell):
    def validate_input(self, data):
        return all(key in data for key in ['cdp_report_path', 'annual_report_path'])

    def process(self, data):
        logger = logging.getLogger(__name__)

        cdp_report_path = data['cdp_report_path']
        annual_report_path = data['annual_report_path']

        try:
            logger.info("Reading CDP report and annual report files...")

            # Read the CDP report
            df = pd.read_excel(cdp_report_path).rename(columns={"Unit": 'Units'})
            if 'Activity' not in df.columns:
                df['Activity'] = 'Total'
            df['Year'] = df['Year'].astype(int)

            # Read the annual report
            predictors_long = pd.read_excel(annual_report_path).rename(columns={"Unit": 'Units'})
            predictors = predictors_long.set_index(['Year', 'Parameter'])['Value'].unstack('Parameter').reset_index()

            # Load configuration data
            config_dict = pd.read_excel(config_path, sheet_name=None)
            parameter_matrix = config_dict['Dependency Matrix']
            predictor_config = config_dict['annual_reports']
            param_config = config_dict['climate_reports']

            # Prepare the dependency matrix
            pred_mat = (
                df[['Scope', 'Parameter', 'Activity']]
                .drop_duplicates()
                .merge(parameter_matrix, on=['Scope', 'Parameter'])
                .set_index(['Scope', 'Parameter', 'Activity'])
                .astype(bool)
            )

            logger.info("Generating estimates...")
            estimates = get_ongil_ccf_estimates(df, predictors, pred_mat)

            logger.info("Generating explainability text...")
            # graph_dicts = get_graph_links(df=estimates, inputs=predictors_long, matrix=pred_mat)
            chk = generate_explainability_text(pred_mat, predictor_config, param_config, company='The Coca Cola Company')
            dependencies = pred_mat.join(chk)

            # Write outputs to Excel file
            output_folder = data.get('output_folder', os.getcwd())
            output_file_path = os.path.join(output_folder, 'final_output.xlsx')
            with pd.ExcelWriter(output_file_path) as writer:
                estimates.to_excel(writer, sheet_name='Data', index=False)
                dependencies.to_excel(writer, sheet_name='Dependencies')
            
            # Convert estimates and dependencies to JSON format
            estimates_json = estimates.to_dict(orient='records')
            explainability_json = chk.reset_index().to_dict(orient='records')

            logger.info("Process completed successfully.")
            return {
                'data': {
                    'output_path': output_file_path,
                    'metadata': {
                        'cdp_report_path': cdp_report_path,
                        'annual_report_path': annual_report_path,
                        'extraction_timestamp': datetime.now().isoformat()
                    },
                    'estimates': estimates_json,
                    'explanation': dependencies_json,
                    'error': None
                }
            }

        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            return {
                'data': {
                    'output_path': None,
                    'error': f"Error during processing: {str(e)}"
                }
            }
