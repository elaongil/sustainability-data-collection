from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import re


def get_ongil_ccf_estimates(df, predictors, pred_mat):
    print(df)
    predictors = predictors.set_index('Year')
    wide_df = df.pivot(index = 'Year', columns = ['Scope','Parameter','Activity','Units'],values='Value')
    energy_pred1 = df.query('(Scope == "Scope 2") & (Activity == "Total") & (Parameter == "Energy Use Total")').set_index('Year')['Value'].rename('energy_use')
    ren_energy_pred1 = df.query('(Scope == "Scope 2") & (Activity == "Total") & (Parameter == "Total Renewable Energy")').set_index('Year')['Value'].rename('energy_use')
    energy_pred = energy_pred1 - ren_energy_pred1
    predictors = predictors.join(energy_pred)
    predictors = predictors.loc[wide_df.index]
    param_predictors = pred_mat.apply(lambda x: x[x].index.tolist(), axis = 1).to_dict()
    s2_params = [x for x,y in param_predictors.items() if 'based' in x[1].lower() ]
    for p in s2_params:
        param_predictors[p].append('energy_use')
    n = len(predictors.index)
    weights = pd.Series([1.2**j for j in range(n)],index = predictors.index, name = 'weights')
    lmod = LinearRegression(fit_intercept = False)
    pred_df = pd.DataFrame(index = wide_df.index, columns = wide_df.columns)
    k = 0
    for scope, param, act, units in wide_df.columns:
        k = k+1
        pred_cols = param_predictors[(scope, param, act)]
        if (pred_cols is None) or (isinstance(pred_cols, list) and (len(pred_cols) == 0)):
            continue
        y = f'{scope}_{param}_{act}'
        col = (scope, param, act, units)
        ydata = wide_df[col].rename(y).copy().replace({0:np.nan})
        max_score = - np.inf
        for i,x in enumerate(pred_cols):

            plot_data = predictors[[x]].join(ydata).join(weights)

            if all(ydata.isnull()):
                continue

            tridx = plot_data[x].notnull() & plot_data[y].notnull()
            if tridx.sum()<3:
                continue
            X = plot_data.loc[tridx,[x]]
            Y = plot_data.loc[tridx,y]
            w = plot_data.loc[tridx,'weights']
            lmod.fit(X,Y, sample_weight = w)

            pred_idx = plot_data[x].notnull()

            y_pred = lmod.predict(plot_data.loc[pred_idx,[x]])
            plot_data.loc[pred_idx,'ypred'] = y_pred
            score = r2_score(Y, plot_data.loc[tridx,'ypred'])
            if score >= max_score:
                x_best = x
                max_score = score
                num_idx= pred_idx[pred_idx].index
                pred_df.loc[num_idx,col] = y_pred

            for j in range(len(plot_data)):
                xj, yj = plot_data.iloc[j,:][[x,y]]
                if any(np.isnan([xj,yj])):
                    continue
    ongil_score = wide_df.transpose()
    ongil_score.columns  = pd.MultiIndex.from_product([ongil_score.columns, ['Company Reported']])
    ongil_pred = pred_df.transpose().astype(float).round()
    ongil_pred.columns  = pd.MultiIndex.from_product([ongil_pred.columns, ['Ongil Estimated']])
    ongil_pred = ongil_pred.fillna(ongil_score.round())
    ongil_pred = ongil_pred.reindex(ongil_score.index)
    # Correct Activity totals
    idx = pd.IndexSlice
    activities = set(df['Activity']).difference(['Total'])
    activities = list(activities)
    act_sum = ongil_pred.loc[idx[:,:,activities,:],:].groupby(level = ['Scope','Parameter','Units']).sum()
    act_sum1 = pd.concat([act_sum], keys=['Total'], names=['Activity']).reorder_levels(['Scope','Parameter','Activity','Units'])
    ongil_pred.loc[act_sum1.index] = act_sum1

    # Correct parameter subtotals
    parent_map = {
        ('Scope 1', 'Total scope 1 emission'): [
            'Fugitive emissions',
            'Mobile combustion',
            'Process emissions',
            'Stationary combustion'
        ],
        ('Scope 2','Energy Use Total'): [
            'Energy Produced Direct',
            'Energy Purchased Direct',
            'Indirect Energy Use'
        ],
        ('Scope 2', 'Total Renewable Energy'): [
            'Renewable Energy Produced',
            'Renewable Energy Purchased'
        ],
        ('Scope 3', 'Total scope 3 emission'): [
            'Category  1- Purchased goods and services',
            'Category  2-Capital goods',
            'Category  3- Fuel-and-energy-related activities (not included in Scope 1 or 2)',
            'Category  4- Upstream transportation and distribution',
            'Category  5- Waste generated in operations',
            'Category  6- Business travel',
            'Category  7- Employee commuting',
            'Category  8- Upstream leased assets',
            'Category  9- Downstream transportation and distribution',
            'Category 1- Purchased goods and services',
            'Category 2-Capital goods',
            'Category 3- Fuel-and-energy-related activities (not included in Scope 1 or 2)',
            'Category 4- Upstream transportation and distribution',
            'Category 5- Waste generated in operations',
            'Category 6- Business travel',
            'Category 7- Employee commuting',
            'Category 8- Upstream leased assets',
            'Category 9- Downstream transportation and distribution',
            'Category 10- Processing of sold products',
            'Category 11- Use of sold products',
            'Category 12- End of life treatment of sold products',
            'Category 13- Downstream leased assets',
            'Category 14- Franchises',
            'Category 15- Investments [row hidden for FS sector companies, data point requested in C-FS14.1a]',
            'Other downstream emissions',
            'Other upstream emissions'
        ]
    }
    for p, c in parent_map.items():

        idx = ongil_pred.index.isin(c, level = 1)
        subtot = pd.concat({(*p,'Total'): ongil_pred.loc[idx,:].fillna(ongil_score.rename(columns = {'Company Reported': 'Ongil Estimated'})).groupby('Units').sum()},names = ('Scope','Parameter','Activity'))
        if subtot.sum().sum() > 0:
            ongil_pred.loc[subtot.index] = subtot
    er_df = pred_df - wide_df
    rel_er_df = (er_df.abs())/ (wide_df.abs()+1000)
    conf_wide = pd.cut(rel_er_df.stack(['Scope','Parameter','Activity','Units']), [0,0.2,0.4,np.inf], labels = ['High','Medium','Low']).unstack(['Scope','Parameter','Activity','Units'])
    conf = conf_wide.transpose().astype(str).replace({'nan':'Not Applicable'})
    conf.columns = pd.MultiIndex.from_product([conf.columns, ['Confidence']])
    combined = ongil_score.round().join(ongil_pred).fillna(0).join(conf).sort_index().sort_index(axis = 1, level = 0)
    combined.columns.names = ['Year','Value']
    final_df = combined.stack('Year').reset_index().sort_values(['Year','Scope','Units','Parameter','Activity']).reset_index(drop = True)
    final_df['Parameter'] = final_df['Parameter'].str.replace(r'Category (\d)\-',r'Category  \1-', regex = True)
    final_df = final_df.sort_values(['Year','Scope','Units','Parameter','Activity']).reset_index(drop = True)
    idx = final_df['Confidence'].isnull()
    final_df.loc[idx,'Ongil Estimated'] = final_df.loc[idx,'Company Reported']
    return final_df


def get_graph_links(df, inputs, matrix):

    input_units = inputs[['Parameter','Units']].dropna().drop_duplicates().set_index('Parameter')['Units']
    inputs = inputs.set_index(['Year','Parameter'])['Value'].unstack('Parameter')
    matrix = matrix.reset_index()
    matrix['Parameter'] =  matrix['Parameter'].str.replace(r'Category (\d)\-',r'Category  \1-', regex = True)
    matrix = matrix.set_index(['Scope', 'Parameter', 'Activity'])
    emission_nodes = df[['Scope','Parameter','Activity']].drop_duplicates().copy()
    emission_nodes['id'] = emission_nodes.apply(lambda x: x['Parameter'] if x['Activity'] == 'Total' else x['Parameter'] + '> ' + x['Activity'], axis = 1)
    emission_nodes['node_type'] = 'parameter'
    emission_nodes['file'] = emission_nodes['Scope']
    emission_nodes.loc[emission_nodes['Parameter'].str.contains('Energy|Electricity', regex = True),'file'] = 'Energy'
    param_node_values = emission_nodes.merge(df.rename(columns = {'Ongil Estimated': 'value'}), on = ['Scope','Parameter','Activity'])[['Year','id','value','Units','node_type']]
    param_node_values.columns = param_node_values.columns.str.lower()
    input_nodes = pd.DataFrame({'name':matrix.columns})
    input_nodes['id'] = input_nodes['name']
    input_nodes['units'] = input_nodes['name'].map(input_units)
    input_nodes['node_type'] = 'factor'
    input_node_values = input_nodes.join(inputs.T, on = 'name').melt(id_vars = ['id','units','node_type'],value_vars = inputs.index, var_name = 'year')
    all_node_values = pd.concat((param_node_values, input_node_values)).sort_values(['year', 'node_type'], ascending = [True, False]).reset_index(drop = True)
    root_nodes = {'Scope 1': 'Total scope 1 emission', 'Scope 3': 'Total scope 3 emission'}
    if df.query('(Scope == "Scope 1") & (Parameter != "Total scope 1 emission" )')['Ongil Estimated'].sum() == 0:
        root_nodes.pop('Scope 1')
    energy_links = pd.DataFrame(
        [
            ['Electricity Produced', 'Energy Produced Direct'],
            ['Electricity Purchased', 'Energy Purchased Direct'],
            ['Energy Produced Direct', 'Energy Use Total'],
            ['Energy Purchased Direct', 'Energy Use Total'],
            ['Indirect Energy Use', 'Energy Use Total'],
            ['Total Renewable Energy', 'Energy Use Total'],
            ['Renewable Energy Produced', 'Total Renewable Energy'],
            ['Renewable Energy Purchased', 'Total Renewable Energy']
        ],
        columns = ['child', 'parent']
    )
    output_dict = {}
    for f, fnodes in emission_nodes.groupby('file'):
        if f == 'Energy':
            param_links = energy_links
        else:
            param_links = (
                fnodes.
                query('Activity == "Total"')[['id','Parameter']].
                rename(columns = {'id':'parent'}).
                merge(
                    fnodes.
                    query('Activity != "Total"')[['id','Parameter']].
                    rename(columns = {'id':'child'}),
                    on = 'Parameter'
                )[['child','parent']]
            )
        if f in root_nodes:
            froot = root_nodes[f]
            subtotals = fnodes.query('(Activity == "Total") & (id != @froot)')['id']
            root_links = pd.DataFrame({'child':subtotals})
            root_links['parent'] = froot
        else:
            root_links = pd.DataFrame(columns = ['child','parent'])
        fmatrix = fnodes.join(matrix, on = ['Scope','Parameter','Activity']).set_index('id')[matrix.columns]
        fmatrix.columns.name = 'name'
        long_inp = fmatrix.stack()
        input_links = (
            long_inp[long_inp>0].
            reset_index()[['id','name']].
            rename(columns = {'id':'parent'}).
            merge(input_nodes, on = 'name', how = 'inner').
            rename(columns = {'id':'child'})[['child','parent']]
        )
        flinks = pd.concat((param_links, input_links), ignore_index = True)
        all_links = pd.concat((flinks, root_links), ignore_index = True)
        fnodeIds = flinks.stack().unique()
        node_vals = all_node_values.query('id.isin(@fnodeIds)')
        out_data = {
            'nodes': node_vals,
            'links': all_links
        }
        output_dict[f] = out_data
    return output_dict


def dict2str(d, keys = None):
    if keys is None:
        keys = d.keys()
    return ' ' + '\n '.join([f'{k}: {v}' for k,v in d.items() if k in keys])


def generate_prompt(i, row, param_descriptions, descriptions):
    s,p,a = i
    act_str = '' if a == "Total " else f'activity "{a}" under '
    checked = row[row].index
    an_params = dict2str(param_descriptions,checked)
    pdesc = descriptions[p]
    p = re.sub(r'\[.*\]','',p).strip()
    param_prefix = f'The parameter "{p}"" is described as {pdesc}\nFor calculating the {s} {act_str}parameter "{p}",the total {p} reported by {company} was used as a starting point.\nThen, '
    an_text = f'The yearly trend of the parameters below was used for correlation analysis to determine confidence in the reported value and to ajdust the corresponding estimate accordingly:\n{an_params}'
    body = an_text
    uinput = param_prefix + body
    return uinput


def generate_explainability_text(dep_matrix, predictor_config, param_config, company):
    param_descriptions = predictor_config.set_index('Parameter')['Description'].to_dict()
    descriptions = param_config.set_index('Parameter')['Description'].to_dict()
    df1 = dep_matrix.copy()
    exp1 = pd.Series(index = df1.index, name = 'Explanation', dtype = object)
    # print(exp1)
    for i, row in df1.iterrows():
        s,p,a = i
        act_str = '' if a == "Total " else f'activity "{a}" under '
        checked = row[row].index
        an_params = dict2str(param_descriptions,checked)
        pdesc = descriptions[p]
        p = re.sub(r'\[.*\]','',p).strip()
        param_prefix = f'The parameter "{p}"" is described as {pdesc}\nFor calculating the {s} {act_str}parameter "{p}",the total {p} reported by {company} was used as a starting point.\nThen, '
        an_text = f'The yearly trend of the parameters below was used for correlation analysis to determine confidence in the reported value and to ajdust the corresponding estimate accordingly:\n{an_params}'
        body = an_text
        uinput = param_prefix + body
        exp1[i] = uinput

    return exp1
