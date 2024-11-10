from datetime import datetime as dt
import polars as pl
from bs4 import BeautifulSoup


def process_file(html_content,
                 start_date=dt.now(),
                 end_date=dt.now(),
                 start_date_oos=dt.now(),
                 end_date_oos=dt.now()
                 ):
    
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', align="right")
    # Definir columnas y extraer datos
    data=[]
    columns = ["#", "OpenTime", "Type", "Nb Order", "Volume", "OpenPrice", "SL", "TP", "Beneficios", "Balance_f"]
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == len(columns):
            data.append(tuple([cell.text.strip() for cell in cells]))
        
        else:
            value = tuple([cell.text.strip() for cell in cells][0:-1]+['0.00','0.00'])
            data.append(value)
    data=data[1:]
    columns = ["#", "Tiempo", "Type", "Nb Order", "Volume", "Precio", "SL", "TP", "Beneficios", "Balance"]
    df = pl.DataFrame(data,columns,orient="row")
    df=df.drop('#')
    df= df.with_columns(
    pl.col('Tiempo').str.to_datetime("%Y.%m.%d %H:%M",time_unit='ms').alias('OpenTime'),
    pl.col('Tiempo').str.to_datetime("%Y.%m.%d %H:%M",time_unit='ms').shift(-1).alias('CloseTime'),
    pl.col('Precio').cast(pl.Float64).alias('OpenPrice'),
    pl.col('Precio').cast(pl.Float64).shift(-1).alias('ClosePrice'),
    pl.col('SL').cast(pl.Float64),
    pl.col('TP').cast(pl.Float64),
    pl.col('Volume').cast(pl.Float64),
    pl.col('Beneficios').cast(pl.Float64).shift(-1).alias('Profit'),
    pl.col('Balance').cast(pl.Float64).shift(-1),
    ).filter(
    df['Type']!='close'
    )
    #Filtra las columnas a retornar
    df=df[['OpenTime', 'CloseTime', 'OpenPrice', 'ClosePrice',	'Type',	'Nb Order'	,'Volume' ,'SL', 'TP', 'Profit',	'Balance']]
    
    #Calcula el drawdown
    df=df.with_columns(
    (-pl.col('Balance')-pl.col('Balance').cum_max()).alias('Drawdown')
    )
    #Calcula el drawdown pct
    df=df.with_columns(
    ((pl.col('Balance')/pl.col('Balance').cum_max())-1).alias('Drawdown_pct')
    )

    df=df.with_columns(pl.when((pl.col('OpenTime')>=start_date_oos) & (pl.col('OpenTime')<=end_date_oos))
                    .then(pl.lit("OS")).otherwise(pl.lit("IS")).alias("Type_sample"))
    return df


    return df

def load_file(fileOpen):
    with open(fileOpen, 'r', encoding='ISO-8859-1') as file:
        html_content = file.read()
    df=process_file(html_content)
    return df

def load_file_st(fileOpen):
    # with open(fileOpen, 'r', encoding='ISO-8859-1') as file:
    html_content = fileOpen.read()
    df=process_file(html_content)
    
    return df