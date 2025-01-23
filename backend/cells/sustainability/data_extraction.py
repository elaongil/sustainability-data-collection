import re
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import json
from openai import OpenAI, AzureOpenAI
import numpy as np
import pdfplumber
from tenacity import retry
from tenacity import wait_exponential, stop_after_attempt
from decouple import config

open_api_key = config("OPEN_API_KEY")
api_version = config("API_VERSION")
azure_endpoint = config("AZURE_ENDPOINT")
deployment = config("DEPLOYMENT")


def get_reporting_year(text):
    try:
        year = int(text.split("<h1")[1].split("</h1")[0][-4:]) - 1
        return year
    except:
        return "0000"


@retry(wait=wait_exponential(multiplier=60, min=20, max=320),stop=stop_after_attempt(3))
def extract_values(context, relevant, previous = None):
    key = open_api_key
    client = AzureOpenAI(
        api_key=key,
        api_version=api_version,
        azure_endpoint=azure_endpoint
    )

    bin_str = '20596f752061726520612068656c7066756c206461746120656e74727920617373697374616e742e0a54686520757365722077696c6c206769766520796f752073656374696f6e73206f66206120646f63756d656e742074686174206d617920626520612068746d6c206f722074657874206578747261637465642066726f6d2061207064662e0a45787472616374207468652076616c75657320616e6420636f72726573706f6e64696e6720756e69747320666f722074686520706172616d6574657273206c69737465642062656c6f772066726f6d20746865206461746120616e642073686172652069742061732061204a534f4e20696e2074686520666f726d6174207368617265642062656c6f772e0a5468652075736572206d617920616c736f20736861726520646174612070726576696f75736c792065787472616374656420666f726d207468652066696c652e20496e207468617420636173652c2075706461746520746865204a534f4e2070726f766964656420696620616e79206d697373696e672076616c756573206172652070726573656e7420696e2069742e0a5765206f6e6c792077616e7420746865206461746120666f72207468652063757272656e74207265706f7274696e6720796561722e2049676e6f726520616c6c206f746865722076616c7565732074686174206d61792062652070726573656e740a4d616b65207375726520746f2075736520746865206578616374207370656c6c696e672c206361736520616e642073706163696e6720666f722074686520706172616d65746572206e616d6520617320696e20746865206465736372697074696f6e2062656c6f770a0a4f757470757420666f726d61743a0a7b0a202020207265706f7274696e675f796561723a0a20202020706172616d657465725f6c6973743a5b0a2020202020202020202020207b0a2020202020202020202020202020202022506172616d65746572223a737472202f2f506172616d65746572206e616d652061732073706563696669656420696e20746865206465736372697074696f6e732062656c6f770a202020202020202020202020202020202256616c7565223a6e756d657269637c4e554c4c202f2f206e756d657269632076616c7565206f662074686520676976656e20706172616d657465722c20656d707479206966206e6f2076616c756520697320676976656e0a2020202020202020202020202020202022556e697473223a7374727c4e554c4c202f2f20756e69747320666f7220746865206e756d6265722c20656d707479206966206e6f2076616c756520697320676976656e0a2020202020202020202020207d2c0a2020202020202020202020207b0a2020202020202020202020202020202022506172616d65746572223a737472202f2f506172616d65746572206e616d652061732073706563696669656420696e20746865206465736372697074696f6e732062656c6f770a202020202020202020202020202020202256616c7565223a6e756d657269637c4e554c4c202f2f206e756d657269632076616c7565206f662074686520676976656e20706172616d657465722c20656d707479206966206e6f2076616c756520697320676976656e0a2020202020202020202020202020202022556e697473223a7374727c4e554c4c202f2f20756e69747320666f7220746865206e756d6265722c20656d707479206966206e6f2076616c756520697320676976656e0a2020202020202020202020207d2c0a2020202020202020202020200a2020202020202020202020202e2e2e0a202020205d0a202020200a7d0a0a506172616d65746572206465736372697074696f6e733a0a'

    prompt = (
        str(bytes.fromhex(bin_str).decode()) + context
    )
    output = {}
    messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": relevant},
        ]
    if previous:
        messages.append(
            {"role": "user", "content": f'Update the JSON with the values from the above document:{previous}'}
        )
    else:
        messages.append(
            {"role": "user", "content": f'Extract the parameter values from the above document in the requested format'}
        )
    completion = client.chat.completions.create(
        model=deployment,
        response_format={"type": "json_object"},
        messages=messages
    )
    try:
        output = json.loads(completion.choices[0].message.content)
    except:
        pass
    if len(output)>0:
        if 'parameter_list' in output:
            if not isinstance(output['parameter_list'],list):
                print(output)
                raise ValueError
    return output


def scope1(full_text, reporting_year, config):
    relevant = full_text.split("(C6.1)")[1].split("<h2")[0]
    
    initial = {
        'reporting_year':reporting_year,
        'parameter_list':pd.DataFrame({'Parameter':config['Parameter'], 'Value':None, 'Units':'metric tonnes CO2e'}).to_dict('records')
    }
    context = config.to_string()
    extracted = extract_values(context, relevant, initial)
    temp = pd.DataFrame(extracted['parameter_list'])
    temp.insert(0,'Year',reporting_year)
    temp['Scope'] = 'Scope 1'
    temp = temp.rename(columns = {'Units':'Unit'})
    return temp


def scope2(full_text, reporting_year, config):
    relevant = full_text.split("C6. Emissions")[1].split("C8.")[0]
    energy_params = [
            "Electricity Produced",
            "Electricity Purchased",
            "Energy Produced Direct",
            "Energy Purchased Direct",
            "Energy Use Total",
            "Indirect Energy Use",
            "Renewable Energy Produced",
            "Renewable Energy Purchased",
            "Total Renewable Energy",
        ]
    config = config.query('~Parameter.isin(@energy_params)')
    initial = {
        'reporting_year':reporting_year,
        'parameter_list':pd.DataFrame({'Parameter':config['Parameter'], 'Value':None, 'Units':'metric tonnes CO2e'}).to_dict('records')
    }
    context = config.to_string()
    extracted = extract_values(context, relevant, initial)
    temp = pd.DataFrame(extracted['parameter_list'])
    temp.insert(0,'Year',reporting_year)
    temp['Scope'] = 'Scope 2'
    temp = temp.rename(columns = {'Units':'Unit'})
    return temp


def scope3(full_text, reporting_year, config):
    
    config = config.query('Parameter != "Total scope 3 emission"')    
    
    relevant = full_text.split("(C6.5)")[1].split("<h2")[0]

    
    initial = {
        'reporting_year':reporting_year,
        'parameter_list':pd.DataFrame({'Parameter':config['Parameter'], 'Value':None, 'Units':'metric tonnes CO2e'}).to_dict('records')
    }
    context = config.to_string()
    extracted = extract_values(context, relevant, initial)
    temp = pd.DataFrame(extracted['parameter_list'])
    temp.insert(0,'Year',reporting_year)
    temp['Value'] = pd.to_numeric(temp['Value'], errors = 'coerce')
    tot_row = pd.DataFrame(
        {
            'Year':reporting_year,
            'Parameter':'Total scope 3 emission',
            'Value': temp['Value'].sum(),
            'Units': 'metric tonnes CO2e'
        },
        index = [0]
    )
    temp = pd.concat((temp, tot_row), ignore_index = True)
    temp['Scope'] = 'Scope 3'
    temp = temp.rename(columns = {'Units':'Unit'})
    return temp


def get_cdp_table_data(f, reporting_year):
    dfs = pd.read_html(f, header=0)
    dlist = []
    energy_df = None
    for df in dfs:
        if df.columns.str.contains("metric tons CO2e", case=False).any() and (
            "Scope" in df.columns[1]
        ):
            df_long = df.set_index(df.columns[0])
            dlist.append(df_long)
        if df.columns.str.contains("mwh", case=False).any():
            dlist.append(df)
            if df.iloc[:, 0].str.contains("consumption of purchased", case=False).any():
                energy_df = df.copy()
                energy_df["Total MWh"] = energy_df[energy_df.columns[-1]]

    if energy_df is not None:
        energy_df["type"] = "Produced"
        purchased_idx = energy_df.iloc[:, 0].str.contains(
            "consumption of purchased", case=False
        )
        energy_df.loc[purchased_idx, "type"] = "Purchased"
        tot_idx = energy_df.iloc[:, 0].str.startswith("Total")
        energy_df.loc[tot_idx, "type"] = "Total"
        value_cols = ["MWh from renewable sources", "Total MWh"]
        energy_df[value_cols] = energy_df[value_cols].applymap(
            lambda x: (
                float(x)
                if (
                    isinstance(x, float)
                    or isinstance(x, int)
                    or (isinstance(x, str) and x.isnumeric())
                )
                else np.nan
            )
        )
        energy_agg = energy_df.groupby("type")[value_cols].sum()

        elec_idx = energy_df.iloc[:, 0].str.contains("electricity", case=False)
        electricity_agg = energy_df.loc[elec_idx, :].groupby("type")[value_cols].sum()
        energy_params = [
            "Electricity Produced",
            "Electricity Purchased",
            "Energy Produced Direct",
            "Energy Purchased Direct",
            "Energy Use Total",
            "Indirect Energy Use",
            "Renewable Energy Produced",
            "Renewable Energy Purchased",
            "Total Renewable Energy",
        ]
        energy_dict = {x: None for x in energy_params}
        electricity_agg.index = 'Electricity ' + electricity_agg.index
        elec_dict = electricity_agg[
            "Total MWh"
        ].to_dict()
        energy_dict.update(elec_dict)
        dir_energy_dict = (
            energy_agg["Total MWh"]
            .rename(
                lambda x: "Energy Use Total" if x == "Total" else f"Energy {x} Direct"
            )
            .to_dict()
        )
        energy_dict.update(dir_energy_dict)
        ren_energy_dict = (
            energy_agg["MWh from renewable sources"]
            .rename(
                lambda x: (
                    "Total Renewable Energy"
                    if x == "Total"
                    else f"Renewable Energy {x}"
                )
            )
            .to_dict()
        )
        energy_dict.update(ren_energy_dict)
    else:
        energy_dict = None
    # return dlist, energy_dict

    temp = pd.DataFrame()
    temp["Year"] = [reporting_year for i in range(len(energy_dict))]
    temp["Scope"] = ["Scope 2" for i in range(len(energy_dict))]
    temp["Parameter"] = energy_dict.keys()
    temp["Value"] = energy_dict.values()
    temp["Unit"] = ["MWh" for i in range(len(energy_dict))]

    return dlist, temp


def remove_header(plist, merge_pages=True):
    page_lines = [[l for l in p.split("\n")] for p in plist]
    header_lines = 0
    for lines in zip(*page_lines):
        all_lines_same = len(set(lines)) == 1
        all_lines_page = all(
            [re.match("^\s*\d+\s*$", chk) is not None for chk in lines]
        )
        if all_lines_same or all_lines_page:
            header_lines += 1
        else:
            break
    modified_pages = ["\n".join(p[header_lines:]) for p in page_lines]
    if merge_pages:
        all_text = "\n".join(modified_pages)
        return all_text
    else:
        return modified_pages


def remove_footer(plist, merge_pages=True):
    page_lines = [[l for l in p.split("\n")] for p in plist]
    modified_pages = []
    for i, p in enumerate(page_lines):
        footer_start = len(p)
        for l in p[::-1]:
            m = re.match("^\s*\d+\s*$", l)
            is_page_no = (m is not None) and (int(l) == (i + 1))
            is_blank = re.match("^\s*$", l) is not None
            if is_page_no or is_blank:
                footer_start -= 1
            else:
                break
        modified_pages.append("\n".join(p[:footer_start]))
    if merge_pages:
        all_text = "\n".join(modified_pages)
        return all_text
    else:
        return modified_pages


def process_annual_report(folder, config_file):
    config_annual = pd.read_excel(config_file, sheet_name="annual_reports")
    context = config_annual.to_string(index = False)
    files = os.listdir(folder)

    dlist = []
    for file in tqdm(files):
        
        with pdfplumber.open(os.path.join(folder, file)) as pdf:
            # Read pages
            pdf_text = [p.extract_text(layout=True) for p in pdf.pages]
            
        # Batch pages
        batches= []
        txt = ''
        tcount = 0
        tlimit = 50_000
        for p in pdf_text:
            #Preprocess page
            lines = p.split('\n')
            lines = [x.rstrip() for x in lines]
            # if len(lines) <1:
            #     continue
            margins = [len(x)-len(x.strip()) for x in lines if x!='']
            if len(margins)>0:
                margin = min(margins)
                patt ='^'+ ' '*margin
                lines = [re.sub(patt,'', x) for x in lines]
            p = '\n\n'.join(lines).strip()
            
            if (tcount+len(p)//4) >=tlimit:
                batches.append(txt)
                txt = ''
                tcount = 0
            txt += p
            tcount += len(p)//4
        if len(txt) > 0:
            batches.append(txt)
    
        #  Extract data
        p = None
        for b in batches:
            data_dict =  extract_values(b, context, p)
            if len(data_dict) >0:
                p = json.dumps(data_dict, indent = 1)
            else:
                p = None

        if 'parameter_list' in data_dict:
            frame = pd.DataFrame(data_dict['parameter_list'])
            frame.insert(0, 'Year',data_dict['reporting_year'])
            dlist.append(frame)

        else:
            print(f'Warning: No data extracted from {file}')
    
    report = pd.concat(dlist, ignore_index = True)
    return report


def process_cdp_report(folder, output, config_file):
    files = os.listdir(folder)
    config = pd.read_excel(config_file, sheet_name='climate_reports')
    config3 = config[config["Scope"] == "Scope 3"]
    config2 = config[config["Scope"] == "Scope 2"]
    config1 = config[config["Scope"] == "Scope 1"]
    report = pd.DataFrame()
    print("processing cdp reports")
    for file in tqdm(files):
        config = pd.read_excel(config_file)
        file_path = os.path.join(folder, file)
        if file_path.endswith('html'):
            with open(file_path, "r") as f:
                full_text = f.read()
                reporting_year = get_reporting_year(full_text)
                temp1 = scope1(full_text, reporting_year, config1)
                temp2 = scope2(full_text, reporting_year, config2)
                dfs, temp3 = get_cdp_table_data(file_path, reporting_year)
                temp4 = scope3(full_text, reporting_year, config3)
            with pd.ExcelWriter(os.path.join(output, file + ".xlsx"), mode="w") as excel:
                for i in range(len(dfs)):
                    dfs[i].to_excel(excel, sheet_name=str(i))
            report = pd.concat([report, temp1, temp2, temp3, temp4], ignore_index = True)
        
        elif file_path.endswith('pdf'):
            context = config.to_string()
            scope_map = pd.Series(config['Scope'], index = config['Parameter'])
            with pdfplumber.open(os.path.join(folder, file)) as pdf:
                # Read pages
                pdf_text = [p.extract_text(layout=True) for p in pdf.pages]
                
                # Batch pages
                batches= []
                txt = ''
                tcount = 0
                tlimit = 50_000
                for p in pdf_text:
                    #Preprocess page
                    lines = p.split('\n')
                    lines = [x.rstrip() for x in lines]
                    # if len(lines) <1:
                    #     continue
                    margins = [len(x)-len(x.strip()) for x in lines if x!='']
                    if len(margins)>0:
                        margin = min(margins)
                        patt ='^'+ ' '*margin
                        lines = [re.sub(patt,'', x) for x in lines]
                    p = '\n'.join(lines).strip() +'\n'
                    
                    if (tcount+len(p)//4) >=tlimit:
                        batches.append(txt)
                        txt = ''
                        tcount = 0
                    txt += p
                    tcount += len(p)//4
                if len(txt) > 0:
                    batches.append(txt)
            
                #  Extract data
                p = None
                for b in batches:
                    data_dict =  extract_values(b, context, p)
                    if len(data_dict) >0:
                        p = json.dumps(data_dict, indent = 1)
                    else:
                        p = None

                if 'parameter_list' in data_dict:
                    frame = pd.DataFrame(data_dict['parameter_list']).rename(columns = {'Units':'Unit'})
                    frame['Value'] = pd.to_numeric(frame['Value'], errors = 'coerce')
                    frame = config[['Scope','Parameter']].merge(frame, on = 'Parameter', how = 'left')
                    frame.insert(0, 'Year',data_dict['reporting_year'])
                    tot_idx = frame['Parameter'] == 'Total scope 3 emission'
                    frame = frame.drop(tot_idx[tot_idx].index)
                    scope_3_idx = (frame['Scope'] == 'Scope 3')
                    tot_scope_3 = frame.loc[scope_3_idx,'Value'].sum()
                    tot_row = pd.DataFrame(
                        {
                            'Year':data_dict['reporting_year'],
                            'Scope': 'Scope 3',
                            'Parameter':'Total scope 3 emission',
                            'Value': tot_scope_3,
                            'Units': 'metric tonnes CO2e'
                        },
                        index = [0]
                    )
                    
                    report = pd.concat([report, frame, tot_row], ignore_index = True)
                else:
                    print(f'Warning: No data extracted from {file}')

        else:
            print('File Format not recognised')
        
    report["Activity"] = ["Total" for i in range(len(report))]
    report = report[["Year", "Scope", "Parameter", "Activity", "Value", "Unit"]]

    return report

# if __name__ == '__main__':
#     annual_report_folder = BASE_DIR + "/ccf_data_flow_files/1_input_data/annual_reports"
#     cdp_report_folder = BASE_DIR + "/ccf_data_flow_files/1_input_data/climate_reports"
#     config_file = BASE_DIR + "/ccf_data_flow_files/0_config/beverage_config.xlsx"
#     output_folder = BASE_DIR + "/ccf_data_flow_files/2_extraction_output"
#
#     cdp_report = process_cdp_report(cdp_report_folder, output_folder, config_file)
#     cdp_report['Value'] = cdp_report['Value'].fillna(0)
#     annual_report = process_annual_report(annual_report_folder, config_file)
#
#     out_path = os.path.join(output_folder, "ccf_output_data.xlsx")
#     with pd.ExcelWriter(out_path, mode="w") as excel:
#         cdp_report.to_excel(excel, index=False, sheet_name="cdp-report")
#         annual_report.to_excel(excel, index=False, sheet_name="annual-report")
