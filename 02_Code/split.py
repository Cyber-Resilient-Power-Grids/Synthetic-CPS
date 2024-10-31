import pandas as pd

# loading excel file
file_path = 'Example/Example.xlsx'  # replace it with your path
data = pd.read_excel(file_path, header=None)

# DataFrame split function
def split_dataframe(df):
    dfs = []
    temp_df = pd.DataFrame()
    for index, row in df.iterrows():
        if pd.isna(row).all():
            if not temp_df.empty:
                dfs.append(temp_df)
                temp_df = pd.DataFrame()
        else:
            temp_df = temp_df.append(row, ignore_index=True)
    if not temp_df.empty:
        dfs.append(temp_df)
    return dfs

# run the function
split_dfs = split_dataframe(data)

# save the splited dataframe into txt files
for i, df in enumerate(split_dfs):
    df = df.applymap(lambda x: int(x) if isinstance(x, (int, float)) and x == x // 1 else x)
    txt_file_path = f'Example/split_data_{i+1}.txt'
    df.to_csv(txt_file_path, index=False, header=False, sep='\t')
