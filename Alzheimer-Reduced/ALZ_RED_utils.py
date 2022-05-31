# Dependencies 
import os 
import pandas as pd
import numpy as np

from  sdg_utils import Positive, Binary 

import openpyxl

from sklearn.preprocessing import OneHotEncoder

def prepare_ALZ_RED(dataset_path : str = "", filename1 : str = "", filename2 : str = "") :
    """Read the Alzheimer-Balea-Reduced dataset from a .xlsx file and suit it to be processed 
    as a pd.DataFrame. It returns tha dataset dataframe and strings associated to 
    it to easy its management.

    Args:
    -----
            dataset_path: path where ALZ-BALEA dataset is stored. Set by default.
            filename : file name of the .csv containing the dataset. Set by default.

    Returns:
    --------
            data: dataframe containing the whole dataset
            X : dataframe containing the dataset features
            Y : dataframe containing only the target variable
            cols_names: list of strings containing feature names. 
            y_tag: string containing target variable name.
    """

    # Go to dataset path
    os.chdir(dataset_path)

    # Open the Excel file 
    bd1 = openpyxl.load_workbook(filename1)
    bd2 = openpyxl.load_workbook(filename2)

    # Load the useful information of the Excel file 
    sheet1 = bd1['Grupo 1']
    sheet2 = bd2['Grupo 2']

    # Convert sheet into DataFrame 
    data1 = pd.DataFrame(sheet1.values)
    data2 = pd.DataFrame(sheet2.values)

    # Fix data properly in the dataframe 
    tags1 = data1.iloc[0]
    data1.columns = tags1
    tags2 = data2.iloc[0]
    data2.columns = tags2

    # Drop first row, that contains the column names 
    data1 = data1.drop(index = [0])
    data2 = data2.drop(index = [0])

    # Replace "NULL" values by a integer to be handled later 
    data1 = data1.replace(to_replace = "#NULL!", value = 99999)
    data2 = data2.replace(to_replace = "#NULL!", value = 99999)

    # Joint dataframes 
    frames = [data1, data2]
    data = pd.concat(frames)

    # Shuffle dataset to mix both subdatasets
    data = data.sample(frac=1)

    # Swap last column ('ERC') with prior column (target variable) to follow convention
    target = data[['TNC']]
    data = data.drop(columns=['TNC'])
    data['TNC'] = target 

    # Store features' and target variable's names 
    cols_names_prev = data.columns
    y_tag = cols_names_prev[len(cols_names_prev)-1]
    cols_names = cols_names_prev[0:cols_names_prev.size]
    
    # Save X, Y, feature names and Y name 
    y_tag = cols_names[len(cols_names)-1]
    cols_names = cols_names[0:len(cols_names)-1]
    X = data[cols_names]
    Y = data[y_tag]
    
    return data, X, Y, cols_names, y_tag

def numerical_conversion(data : np.array, features : str, y_col : str):
    """Fix all Alzheimer-Balea reduces database features data types to its original type after KNNImputer is used,
    since this functions returns only a floating points ndarray. For more, check sklearn 
    documentation of this function at
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.KNNImputer.html. After 
    fixing datatypes, an ndarray to pd.DataFrame conversion is performed. Notice that this
    operation is only done in the fields that were not originally floats.

    Args:
    -----
            data: data returned by KNN Imputer (float data type).
            features: list of strings containing the feature names of the dataset. 
            y_col: target variable (i.e., Y) name 

    Returns:
    --------
            data: dataframe containing the whole dataset after imputation
            X : dataframe containing the dataset features after imputation
            y : dataframe containing only the target variable after imputation
    """
    # From ndarray to pd.DataFrame
    names = features.insert(len(features), y_col)
    data = pd.DataFrame(data, columns = names)
    
    # Fixing necessary datatypes to int (including categorical variables)
    data['Edad'] = data['Edad'].astype(int)
    data['Sexo'] = data['Sexo'].astype(int)
    data['Convivencia'] = data['Convivencia'].astype(int)
    data['HTA'] = data['HTA'].astype(int)
    data['DM'] = data['DM'].astype(int)
    data['DLP'] = data['DLP'].astype(int)
    data['Depresión'] = data['Depresión'].astype(int)
    data['ERC'] = data['ERC'].astype(int)
    data['TNC'] = data['TNC'].astype(int)

    # Separate X and Y 
    X = data[features]
    y = data[[y_col]]    
     
    return data, X, y

def general_conversion (data : pd.DataFrame) :
    """Fix all Alzheimer-Balea Reduced database features data types to its original type.
    Categorical variables are set as "object" type. A DataFrame with the original 
    datatypes of this database is returned.

    Args:
    -----
            data: dataset with datatypes not corresponding to the original ones.
            features: list of strings containing the feature names of the dataset. 
            y_col: target variable (i.e., Y) name 

    Returns:
    --------
            data: dataframe with the original datatypes 
    """
    data['Edad'] = data['Edad'].astype(int)
    data['Sexo'] = data['Sexo'].astype(int)
    data['Convivencia'] = data['Convivencia'].astype('object')
    data['HTA'] = data['HTA'].astype(int)
    data['DM'] = data['DM'].astype(int)
    data['DLP'] = data['DLP'].astype(int)
    data['Depresión'] = data['Depresión'].astype(int)
    data['ERC'] = data['ERC'].astype(int)
    data['TNC'] = data['TNC'].astype(int)
    
    return data

def replacement(data : pd.DataFrame):
    """This function replaces the numerical values corresponding to categories in 
    the Alzheimer-Balea-Red database by its correspondant category. It returns a DataFrame
    after this replacement.

    Args:
    -----
            data: dataset with categories represented by numbers.

    Returns:
    --------
            data: dataframe with the categories represented by their correspondant string  
    """
    data['Convivencia']  = data['Convivencia'].replace([1,2,3],['conv_1', 'conv_2', 'conv_3'])
    
    return data 

def one_hot_enc(data):
    """This function performs One-Hot Encoding in the Alzheimer-Balea database. Since this
    database is really small, validation and train sets are even smaller. Hence, sometimes 
    columns full of 0s must be manually added, because a certain value of a feature does not 
    appear in the dataset subset. This is the case of category 'Empresarios' of feature "ActLaboral". 

    Args:
    -----
            data: dataset with categories represented by numbers.

    Returns:
    --------
            data: dataframe with the categories represented by their correspondant string  
    """
    
    # One-hot Encoder declaration 
    enc = OneHotEncoder(handle_unknown='ignore')
    # Convivencia 
    cats = ['conv_1', 'conv_2', 'conv_3']
    data[['Convivencia']] = data[['Convivencia']].astype('category')
    convi = pd.DataFrame(enc.fit_transform(data[['Convivencia']]).toarray())
    convi.columns = enc.categories_
    for name in cats:
        if name not in convi:
            convi[name] = 0    
    convi = convi[['conv_1', 'conv_2', 'conv_3']]
    convi.reset_index(drop=True, inplace=True)
    
    # Drop column to add it at the end 
    affected = data[['TNC']]
    affected.reset_index(drop=True, inplace=True)
    
    # Drop original categorical columns
    data = data.drop(['Convivencia', 'TNC'], axis=1)
    data.reset_index(drop=True, inplace=True)
    
    data = pd.concat([data, convi, affected],axis=1)
    
    return data

# Dictionary to specify fields of synthetic data for Alzheimer-Balea database
alz_red_fields = {
    'Sexo' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'Edad' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'Convivencia' : {
        'type' : 'categorical'
    },
    'HTA' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'DM' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'DLP' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'Depresión' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'ERC' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
    'TNC' : {
        'type' : 'numerical',
        'subtype' : 'integer'
    },
 }

# Custom variable constraints to generate synthetic data 
constraints = [ 
                #Positive('Edad',handling_strategy='reject_sampling'),
                #Binary('HTAanterior',handling_strategy='reject_sampling'),
                #Positive('TAS',handling_strategy='reject_sampling'), 
                #Positive('TAD',handling_strategy='reject_sampling'),
                #Binary('DM',handling_strategy='reject_sampling'),
                # Positive('Barthel',handling_strategy='reject_sampling'),
                # Positive('Hb',handling_strategy='reject_sampling'),
                # Positive('VCM',handling_strategy='reject_sampling'),
                # Positive('HCM',handling_strategy='reject_sampling'),
                # Positive('Plaquetas',handling_strategy='reject_sampling'),
                # Positive('Leucocitos',handling_strategy='reject_sampling'),
                # Positive('Neutrófilos',handling_strategy='reject_sampling'),
                # Positive('Linfocitos',handling_strategy='reject_sampling'),
                # Positive('Monocitos',handling_strategy='reject_sampling'),
                # Positive('Glucosa',handling_strategy='reject_sampling'),
                # Positive('Creatinina',handling_strategy='reject_sampling'),
                # Positive('FG',handling_strategy='reject_sampling'),
                # Positive('Na',handling_strategy='reject_sampling'),
                # Positive('K',handling_strategy='reject_sampling'),
                # Positive('ALT',handling_strategy='reject_sampling'),
                # Positive('Colesterol',handling_strategy='reject_sampling'),
                # Positive('LDL',handling_strategy='reject_sampling'),
                #Binary('TNeurocog',handling_strategy='reject_sampling'),
                ]

# Distributions for each field (all set to univariate)
alz_red_distributions = {
    'Sexo' : 'univariate',
    'Edad' : 'univariate', 
    'Convivencia' : 'univariate', 
    'HTA' : 'univariate', 
    'DM' : 'univariate', 
    'DLP' : 'univariate', 
    'Depresión' : 'univariate', 
    'ERC' : 'univariate', 
    'TNC' : 'univariate', 
    }  