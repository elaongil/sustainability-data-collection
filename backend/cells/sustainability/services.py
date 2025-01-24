import os
import tempfile
from urllib.parse import urljoin

import pandas as pd
import logging
import shutil
from datetime import datetime

from cells.base.helpers import clear_directory
from cells.sustainability.get_ccf_data import generate_explainability_text, get_ongil_ccf_estimates
from ..base.cell import BaseCell
from ..base.serializers import FileUploadSerializer, SessionIdSerializer
from .data_extraction import process_cdp_report, process_annual_report

from config.settings import MEDIA_ROOT
UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'app_files')


class CDPExtractorCell(BaseCell):

    def validate_input(self, data):
        serializer = FileUploadSerializer(data=data)
        if serializer.is_valid():
            return True
        else:
            return False

    def process(self, data, *args, **kwargs):

        request = kwargs["request"]

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
            output_file_path = os.path.join(output_folder_path, f'{self.__class__.__name__}.xlsx')
            output_file_url = urljoin(request.build_absolute_uri('/'), os.path.relpath(output_file_path))

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
                    'output_path': output_file_url,
                    'metadata': {
                        'file_count': len(files),
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
        serializer = FileUploadSerializer(data=data)
        if serializer.is_valid():
            return True
        else:
            return False

    def process(self, data, *args, **kwargs):

        request = kwargs["request"]

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
                with open(f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}/input/{file.name}", "wb") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            logger.info("Processing files...")

            try:
                df = process_annual_report(input_folder_path, config_path)
            except Exception as e:
                logger.error(f"Error processing {self.__class__.__name__} report: {str(e)}")
                return {
                    'data': {
                        'output_path': None,
                        'error': f"Error processing {self.__class__.__name__} report: {str(e)}"
                    }
                }

            # Write the dataframe to the output folder
            output_file_path = os.path.join(output_folder_path, f'{self.__class__.__name__}.xlsx')
            output_file_url = urljoin(request.build_absolute_uri('/'), os.path.relpath(output_file_path))

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
                    'output_path': output_file_url,
                    'metadata': {
                        'file_count': len(files),
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
        serializer = SessionIdSerializer(data=data)
        if serializer.is_valid():
            return True
        else:
            return False

    def process(self, data, *args, **kwargs):

        request = kwargs["request"]

        logger = logging.getLogger(__name__)

        serializer = SessionIdSerializer(data=data)
        if serializer.is_valid():
            pass

        session_id = serializer.validated_data.get('session_id')

        cdp_report_path = f"{UPLOAD_DIR}/{session_id}/CDPExtractorCell/output/CDPExtractorCell.xlsx"
        annual_report_path = f"{UPLOAD_DIR}/{session_id}/AnnualReportExtractorCell/output/AnnualReportExtractorCell.xlsx"
        config_path = f"{MEDIA_ROOT}/required/beverage_config.xlsx"

        output_folder_path = f"{UPLOAD_DIR}/{session_id}/{self.__class__.__name__}/output"
        os.makedirs(output_folder_path, exist_ok=True)

        try:
            logger.info("Reading CDP report and annual report files...")

            # Read the CDP report
            df = pd.read_excel(cdp_report_path).rename(columns={"Unit": 'Units'})
            if 'Activity' not in df.columns:
                df['Activity'] = 'Total'
            df['Year'] = df['Year'].astype(int)
            df.loc[df['Units'] != 'MWh','Units'] = 'metric tonnes CO2e'
            
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
            estimates['Ongil Estimated'] = estimates['Ongil Estimated'].fillna(0)

            logger.info("Generating explainability text...")
            # graph_dicts = get_graph_links(df=estimates, inputs=predictors_long, matrix=pred_mat)
            chk = generate_explainability_text(pred_mat, predictor_config, param_config, company='The Coca Cola Company')
            dependencies = pred_mat.join(chk)

            # Write outputs to Excel file
            output_file_path = os.path.join(output_folder_path, f'{self.__class__.__name__}.xlsx')
            with pd.ExcelWriter(output_file_path) as writer:
                estimates.to_excel(writer, sheet_name='Data', index=False)
                dependencies.to_excel(writer, sheet_name='Dependencies')

            output_file_url = urljoin(request.build_absolute_uri('/'), os.path.relpath(output_file_path))

            # Convert estimates and dependencies to JSON format
            estimates_json = estimates.fillna('').to_dict(orient='records')
            explainability_json = chk.reset_index().to_dict(orient='records')

            logger.info("Process completed successfully.")
            return {
                'data': {
                    'output_path': output_file_url,
                    'metadata': {
                        'cdp_report_path': urljoin(request.build_absolute_uri('/'), os.path.relpath(cdp_report_path)),
                        'annual_report_path': urljoin(request.build_absolute_uri('/'), os.path.relpath(annual_report_path)),
                        'extraction_timestamp': datetime.now().isoformat()
                    },
                    'estimates': estimates_json,
                    'explanation': explainability_json,
                    'error': None
                }
            }

        except Exception as e:
            logger.exception(f"Error during processing: {str(e)}")
            return {
                'data': {
                    'output_path': None,
                    'error': f"Error during processing: {str(e)}"
                }
            }
