###############################################################################
#                                                                             #
#           run this to explore the missing values in the dataset             #
#                                                                             #
###############################################################################

import pandas as pd

# read in the dataset
# this path should be the merged dataset, cleaned or uncleaned
merge_data_path = 'cleaned_ihd_merged.csv'

merge_data = pd.read_csv(merge_data_path)

# capture dtypes for all features
types = merge_data.dtypes

# create series for NA count for features
missing_val_count = merge_data.isnull().sum()

# pass this series to a data frame
df = missing_val_count.to_frame()

# drop index and rename columns
df = df.reset_index(col_fill = 'Feature')
df.columns = ['Feature', 'NA Count']

# total number of samples
total_samples = int(merge_data.count()['Id'])

# add percentage column
df['Percentage'] = round(df['NA Count']/(total_samples),5)

# specify data type for these columns
df = df.astype({'Feature': 'str', 'Percentage': 'float'})

# add colummn to preview all dtypes
df['Data Type'] = types.values

# get list of all features with a numeric data type
numerics_list = train_data.select_dtypes(include=['float', 'int']).columns

# add column that describes what values are represented in object types and summarizes values in numeric types
overview = merge_data.apply(lambda x: [round(x.min()), round(x.max()), round(x.mean()),round(x.quantile(0.5))] if x.name in numerics_list else x.unique())

df['Overview'] = overview.values

# sort values by descending percentage of data missing
df = df.sort_values(['Percentage','NA Count'], ascending=False)

df.reset_index(drop=True, inplace=True)

# export df to file
# df.transpose().to_html('missing-values.html')
df.to_html('missing-values.html')
