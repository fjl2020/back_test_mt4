import polars as pl
from scipy.stats import kstest, ttest_1samp, t
import numpy as np

def nb_samples(df):
    return df.filter(pl.col('Type_sample')=='IS').shape[0], df.filter(pl.col('Type_sample')=='OOS').shape[0]

def separate_df(df):
    is_data = df.filter(pl.col('Type_sample')=='IS')
    oos_data = df.filter(pl.col('Type_sample')=='OOS')
    return is_data, oos_data

def ks_test(df,threshold):
    # Filtrar periodos IS y OS 
    is_data,oos_data = separate_df(df)
    is_data = is_data ['Profit']
    oos_data = oos_data['Profit']

    # Aplicar el test KS
    ks_statistic, p_value = kstest(is_data, oos_data)
    
    return ks_statistic, p_value

def calcular_ratio_sharpe(df, risk_free=0.0):
    
    
    
    df=df.with_columns(
        (pl.col('Balance')/pl.col('Balance').shift(1)-1).alias('Profit_pct')
    )
        
    return (df['Profit_pct'].mean()-risk_free)/df['Profit_pct'].std()

def calcular_pf(df):
    return abs(df.filter(pl.col('Profit')>0)['Profit'].sum()/df.filter(pl.col('Profit')<0)['Profit'].sum())

def calcular_winrate(df):

    return abs(df.filter(pl.col('Profit')>0)['Profit'].shape[0]/df.shape[0])

def daily_avg_profit(df):
    cnt_days=df.with_columns(
                pl.col('OpenTime').dt.strftime("%Y%m%d").alias('days_txt'),
                )['days_txt'].unique().shape[0]
    total_profit= df['Profit'].sum()
    return total_profit/cnt_days

def monthly_avg_profit(df):
    cnt_month= df.with_columns(
                pl.col('OpenTime').dt.strftime("%Y%m").alias('month_txt'),
                )['month_txt'].unique().shape[0]
    total_profit= df['Profit'].sum()
    return total_profit/cnt_month

def year_avg_profit(df):
    cnt_year= df.with_columns(
                pl.col('OpenTime').dt.strftime("%Y").alias('year_txt'),
                )['year_txt'].unique().shape[0]
    total_profit= df['Profit'].sum()
    return total_profit/cnt_year
def calcular_ret_dd(df):
    return df['Profit'].sum()/-df['Drawdown'].min()

def gross_profit(df):
    return win_df(df)['Profit'].sum()

def gross_loss(df):
    return loss_df(df)['Profit'].sum()

def win_df(df):
    return df.filter(pl.col('Profit')>0)

def loss_df(df):
    return df.filter(pl.col('Profit')<0)
    

def calc_expectancy(df):
    win=wind_df(df)['Profit']
    loss=loss_df(df)['Profit']

    avg_win=win.mean()
    avg_loss=loss.mean()
    prop_win = win.shape[0]/df.shape[0]
    prop_loss = loss.shape[0]/df.shape[0]

    expectancy=((avg_win*prop_win)+(avg_loss*prop_loss))
    return expectancy

def calc_expectancy(df):
    win=win_df(df)['Profit']
    loss=loss_df(df)['Profit']

    avg_win=win.mean()
    avg_loss=loss.mean()
    prop_win = win.shape[0]/df.shape[0]
    prop_loss = loss.shape[0]/df.shape[0]

    expectancy=((avg_win*prop_win)+(avg_loss*prop_loss))
    return expectancy

def calc_win_loss_ratio(df):
    win=win_df(df)['Profit']
    loss=loss_df(df)['Profit']

    win_loss_ratio=(win.shape[0]/loss.shape[0])
    return  win_loss_ratio

def calc_payout_ratio(df):
    win=win_df(df)['Profit']
    loss=loss_df(df)['Profit']

    avg_win=win.mean()
    avg_loss=loss.mean()

    payout_ratio= (avg_win/avg_loss)

    return  payout_ratio
def calcular_max_consecutivos(df: pl.DataFrame, columna: str) -> dict:
    """
    Calcula la máxima cantidad de 1s y 0s consecutivos en una columna.
    
    Parámetros:
    df (pl.DataFrame): DataFrame de Polars
    columna (str): Nombre de la columna que contiene los valores binarios
    
    Retorna:
    dict: Diccionario con estadísticas de consecutivos para 1s y 0s
    """
    # Crear una columna que indica cuando hay un cambio en el valor
    df=df.with_columns(pl.when(pl.col(columna)>0).then(1).otherwise(0).alias('win_op'))
    
    df_with_changes = df.with_columns([
        pl.col('win_op').ne(pl.col('win_op').shift()).fill_null(True).alias("cambio")
    ])
    
    # Crear un grupo para cada secuencia consecutiva
    df_with_groups = df_with_changes.with_columns([
        pl.col("cambio").cum_sum().alias("grupo")
    ])
    
    # Calcular estadísticas para 1s y 0s
    stats = (df_with_groups
        .group_by(["grupo", 'win_op'])
        .agg(pl.len().alias("consecutivos"))
        .group_by('win_op')
        .agg([
            pl.col("consecutivos").max().alias("max_consecutivos"),
            pl.col("consecutivos").mean().alias("promedio_consecutivos"),
            pl.col("consecutivos").count().alias("num_secuencias")
        ]))
    
    # Convertir a diccionario para fácil acceso
    resultado = {
        "unos": {
            "max_consecutivos": stats.filter(pl.col('win_op') == 1)["max_consecutivos"][0],
            "promedio_consecutivos": stats.filter(pl.col('win_op') == 1)["promedio_consecutivos"][0],
            "num_secuencias": stats.filter(pl.col('win_op') == 1)["num_secuencias"][0]
        },
        "ceros": {
            "max_consecutivos": stats.filter(pl.col('win_op') == 0)["max_consecutivos"][0],
            "promedio_consecutivos": stats.filter(pl.col('win_op') == 0)["promedio_consecutivos"][0],
            "num_secuencias": stats.filter(pl.col('win_op') == 0)["num_secuencias"][0]
        }
    }
    return resultado
def calc_win_consec(df):
    return calcular_max_consecutivos(df,'Profit')['unos']['max_consecutivos']

def calc_loss_consec(df):
    return calcular_max_consecutivos(df,'Profit')['ceros']['max_consecutivos']
def yield_by_month_day(df):
    df_tmp=df.with_columns(
                pl.col('OpenTime').dt.month().alias('Month'),
                pl.col('OpenTime').dt.year().alias('Year'),)


    df_pivot=df_tmp.pivot(index='Year',values='Profit',on='Month',aggregate_function="sum")
    df_pivot = df_pivot[['Year']+[f'{c}' for c in list(set([int(d) for d in  df_pivot.columns[1:]]))]]
    df_pivot=df_pivot.with_columns(ytd=pl.sum_horizontal(df_pivot.columns[1:]))

    df_pivot=df_pivot.fill_null(0)
    return df_pivot
def metrics(df):
    
    df_is,df_oos=separate_df(df)
    statistics=[]
    statistics+=[
            {'statistic':'Nb trades',
             'IS':df_is.shape[0],
             'OS':df_oos.shape[0],
             'IS_OOS':df_is.shape[0]},
            {'statistic':'Total profit',
             'IS':f'{df_is['Profit'].sum():.2f}',
             'OS':f'{df_oos['Profit'].sum():.2f}',
             'IS_OOS':f'{df['Profit'].sum():.2f}'},
            {'statistic':'Sharpe IS',
             'IS':f'{calcular_ratio_sharpe(df_is,risk_free=0):.2f}',
             'OS':f'{calcular_ratio_sharpe(df_oos,risk_free=0):.2f}',
             'IS_OOS':f'{calcular_ratio_sharpe(df,risk_free=0):.2f}'},
            {'statistic':'PF',
             'IS':f'{calcular_pf(df_is):.2f}',
             'OS':f'{calcular_pf(df_oos):.2f}',
             'IS_OOS':f'{calcular_pf(df):.2f}'},
            {'statistic':'Win Rate',
             'IS':f'{calcular_winrate(df_is)*100:.2f}%',
             'OS':f'{calcular_winrate(df_oos)*100:.2f}%',
             'IS_OOS':f'{calcular_winrate(df)*100:.2f}%'},
            {'statistic':'Drawdown Max PCT',
             'IS':f'{-df_is['Drawdown_pct'].min()*100:.2f}%',
             'OS':f'{-df_oos['Drawdown_pct'].min()*100:.2f}%',
             'IS_OOS':f'{-df['Drawdown_pct'].min()*100:.2f}%'},
            {'statistic':'Drawdown Max',
             'IS':f'{-df_is['Drawdown'].min():.2f} $',
             'OS':f'{-df_oos['Drawdown'].min():.2f} $',
             'IS_OOS':f'{-df['Drawdown'].min():.2f} $'},
            {'statistic':'Return/DD ratio',
             'IS':f'{calcular_ret_dd(df_is):.2f}',
             'OS':f'{calcular_ret_dd(df_is):.2f}',
             'IS_OOS':f'{calcular_ret_dd(df_is):.2f}'},
            
            {'statistic':'Daily AVG Profit',
             'IS':f'{daily_avg_profit(df_is):.2f} $',
             'OS':f'{daily_avg_profit(df_oos):.2f} $',
             'IS_OOS':f'{daily_avg_profit(df):.2f} $'},
            
            {'statistic':'Monthly AVG Profit',
             'IS':f'{monthly_avg_profit(df_is):.2f} $',
             'OS':f'{monthly_avg_profit(df_oos):.2f} $',
             'IS_OOS':f'{monthly_avg_profit(df):.2f} $'},
            {'statistic':'Year AVG Profit',
             'IS':f'{year_avg_profit(df_is):.2f} $',
             'OS':f'{year_avg_profit(df_oos):.2f} $',
             'IS_OOS':f'{year_avg_profit(df):.2f} $'},
           
            ]

    df_statistics=pl.DataFrame(statistics)
    return df_statistics

def st_metrics(df):
    
    df_is,df_oos=separate_df(df)
    statistics=[]
    statistics+=[
            {'statistic':'Expentancy',
             'IS':f'{calc_expectancy(df_is) :.2f} $',
             'OS':f'{calc_expectancy(df_oos):.2f} $',
             'IS_OOS':f'{calc_expectancy(df):.2f} $'},
            {'statistic':'Win Loss Ratio',
             'IS':f'{calc_win_loss_ratio(df_is):.2f} ',
             'OS':f'{calc_win_loss_ratio(df_oos):.2f} ',
             'IS_OOS':f'{calc_win_loss_ratio(df):.2f} '},
             {'statistic':'Expentancy',
             'IS':f'{calc_win_loss_ratio(df_is):.2f}',
             'OS':f'{calc_win_loss_ratio(df_oos):.2f}',
             'IS_OOS':f'{calc_win_loss_ratio(df):.2f}'},
             
            
            ]

    df_statistics=pl.DataFrame(statistics)
    return df_statistics

def trades_metrics(df):
    
    df_is,df_oos=separate_df(df)
    statistics=[]
    
    statistics+=[
          
            {'statistic':'Gross Profit',
             'IS':f'{gross_profit(df_is):.2f} $',
             'OS':f'{gross_profit(df_oos):.2f} $',
             'IS_OOS':f'{gross_profit(df):.2f} $'},
            {'statistic':'Gross Loss',
             'IS':f'{gross_loss(df_is):.2f} $',
             'OS':f'{gross_loss(df_oos):.2f} $',
             'IS_OOS':f'{gross_loss(df):.2f} $'},
            {'statistic':'# Win',
             'IS':f'{win_df(df_is).shape[0]}',
             'OS':f'{win_df(df_oos).shape[0]}',
             'IS_OOS':f'{win_df(df).shape[0]}'},
            {'statistic':'# Loss',
             'IS':f'{loss_df(df_is).shape[0]}',
             'OS':f'{loss_df(df_oos).shape[0]}',
             'IS_OOS':f'{loss_df(df).shape[0]}'},
            {'statistic':'Average Win',
             'IS':f'{win_df(df_is)['Profit'].mean():.2f} $',
             'OS':f'{win_df(df_oos)['Profit'].mean():.2f} $',
             'IS_OOS':f'{win_df(df)['Profit'].mean():.2f} $'},
            {'statistic':'Average Loss',
             'IS':f'{loss_df(df_is)['Profit'].mean():.2f} $',
             'OS':f'{loss_df(df_oos)['Profit'].mean():.2f} $',
             'IS_OOS':f'{loss_df(df)['Profit'].mean():.2f} $'},
             {'statistic':'Largest Win',
             'IS':f'{win_df(df_is)['Profit'].max():.2f} $',
             'OS':f'{win_df(df_oos)['Profit'].max():.2f} $',
             'IS_OOS':f'{win_df(df)['Profit'].max():.2f} $'},
            {'statistic':'Largest Loss',
             'IS':f'{loss_df(df_is)['Profit'].min():.2f} $',
             'OS':f'{loss_df(df_oos)['Profit'].min():.2f} $',
             'IS_OOS':f'{loss_df(df)['Profit'].min():.2f} $'},
            {'statistic':'Max consecutive Win',
             'IS':f'{calc_win_consec(df_is)}',
             'OS':f'{calc_win_consec(df_oos)} ',
             'IS_OOS':f'{calc_win_consec(df)} '},
            {'statistic':'Max consecutive Loss',
             'IS':f'{calc_loss_consec(df_is)} ',
             'OS':f'{calc_loss_consec(df_oos)} ',
             'IS_OOS':f'{calc_loss_consec(df)} '},
            ]

    df_statistics=pl.DataFrame(statistics)
    return df_statistics