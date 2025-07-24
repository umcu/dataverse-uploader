#!/usr/bin/env python3

import sys
from os.path import abspath, splitext
import pandas as pd
import pyreadstat
from zipfile import ZipFile

def stat_to_csv(fname, fextension):
    """convert SPSS .sav or SAS .sas7bdat files to csv, also creates a codebook csv file"""
    file_path = fname+fextension
    file_name = fname
    # retrieve data and metadata from SPSS or SAS file
    if fextension == '.sav':
        data, metadata = pyreadstat.read_sav(file_path)
    elif fextension == '.sas7bdat':
        data, metadata = pyreadstat.read_sas7bdat(file_path)
    else:
        raise ValueError(f"statistic file extension '{fextension}' not implemented yet")
    # retrieve variable labels from metadata and put these in a dataframe
    variable_labels = pd.DataFrame().\
        from_dict(metadata.column_names_to_labels, orient='index').\
        reset_index().rename(columns={'index': 'variable_name', 0: 'variable_label'})
    # variables are linked to an option label group through an option group ID
    variable_label_id = pd.DataFrame().from_dict(metadata.variable_to_label, orient='index').\
        reset_index().rename(columns={'index': 'variable_name', 0: 'value_label_id'})
    # join the data frames variable_labels and variable_label_id on 'variable_name'
    variable_labels_with_id = pd.merge(variable_labels, variable_label_id, how='left',
        left_on='variable_name', right_on='variable_name').fillna('')
    # value labels are stored in a dictionary;
    # convert this to a table 'value_label', 'value', 'value_label_id'
    value_labels_dict = metadata.value_labels
    if len(value_labels_dict) == 0: # no value labels, so codebook is very simple
        print('no value labels')
        codebook = variable_labels
    else:
        collect = []
        for k1, v1 in value_labels_dict.items():
            for k2, v2 in v1.items():
                # the str.replace is necessary because to_csv adds decimals to the values
                collect.append([str(k2).replace('.0', ''), v2, k1])
        value_labels = pd.DataFrame(collect).\
            rename(columns={0: 'value_label', 1: 'value', 2: 'value_label_id'})
        # final codebook contains variable labels and value labels
        print('variable_labels has columns {}'.format(variable_labels.columns))
        print('value_labels has columns {}'.format(value_labels.columns))
        print('merge variable_labels and value_labels on value_label_id')
        codebook = pd.merge(variable_labels_with_id, value_labels, how='left',
                            left_on='value_label_id',
                            right_on='value_label_id').fillna('').drop('value_label_id', axis=1)
        print('codebook has columns {}'.format(codebook.columns))           

    data_filename = file_name + '.csv'
    codebook_filename = file_name + '_codebook.csv'
    data.to_csv(data_filename, index=False, sep=';')
    codebook.to_csv(codebook_filename, index=False, sep=';')
    zip_filename = file_name + '.zip'
    with ZipFile(zip_filename, 'w') as zip_file:
        zip_file.write(data_filename)
        zip_file.write(codebook_filename)

known_extensions = {
    '.sav'     : 'SPSS',
    '.sas7bdat': 'SAS'
}
fname, fextension = splitext(abspath(sys.argv[1]))
if fextension in known_extensions.keys():
    try:
        stat_to_csv(fname, fextension)
    except Exception as e:
        print(f"could not convert due to {e}")
else:
    print(f"unknown extension {fextension}")
