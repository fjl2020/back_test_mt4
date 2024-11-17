import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import Line,Bar,Scatter,Layout,Figure
from datetime import datetime as dt
import  polars as pl

def weekday_mean_profit(df,name_short=False,type_sample="IS"):
    DAYS_FULL=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    DAYS_SHORT=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    all_weekdays = pl.DataFrame({
        'weekday': pl.Series(range(1, 8), dtype=pl.Int8)  # 0 a 6 para todos los días
        })
    # Tu código original para procesar el DataFrame
    # if type_sample== 'IS':
        
    #     df_season = df.filter(pl.col('Type_sample')=='IS').with_columns(
    #         pl.col('CloseTime').dt.weekday().alias('weekday')
    #         )
    # elif type_sample== 'OOS':
        
    #     df_season = df.filter(pl.col('Type_sample')=='OOS').with_columns(
    #         pl.col('CloseTime').dt.weekday().alias('weekday')
    #         )
    # else: 
    df_season = df.with_columns(
        pl.col('CloseTime').dt.weekday().alias('weekday')
         )

    # Agrupación con promedio de Profit
    df_wd_prof = df_season.group_by('weekday','Type_sample').agg(pl.col('Profit').mean())
    if name_short:
        DAYS_NAME= DAYS_FULL
    else:
        DAYS_NAME= DAYS_SHORT
    # Unimos con todos los días y rellenamos los valores faltantes con 0 (o None si prefieres)
    df_wd_prof_complete = (
        all_weekdays
        .join(df_wd_prof, on='weekday', how='left')
        .with_columns(
            pl.col('Profit').fill_null(0),  # Puedes cambiar 0 por None si prefieres
            pl.col('weekday').replace_strict(
                {i: day for i, day in enumerate(DAYS_NAME,start=1)},
                default="unknown"
                ).alias('weekday_name')
            )
        .sort('weekday')
    )
    return df_wd_prof_complete

def month_mean_profit(df,name_short=False):
    MONTH_FULL= ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    MONTH_SHORT= ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    all_weekdays = pl.DataFrame({
        'month': pl.Series(range(1, 13), dtype=pl.Int8)  # 0 a 6 para todos los días
        })
    # Tu código original para procesar el DataFrame
    
    df_season = df.with_columns(
            pl.col('CloseTime').dt.month().alias('month')
            )
    # Agrupación con promedio de Profit
    df_wd_prof = df_season.group_by('month','Type_sample').agg(pl.col('Profit').mean())
    # Unimos con todos los días y rellenamos los valores faltantes con 0 (o None si prefieres)
    if name_short:
        MONTH_NAME= MONTH_FULL
    else:
        MONTH_NAME= MONTH_SHORT
    df_wd_prof_complete = (
        all_weekdays
        .join(df_wd_prof, on='month', how='left')
        .with_columns(
            pl.col('Profit').fill_null(0),  # Puedes cambiar 0 por None si prefieres
            pl.col('month').replace_strict(
                {i: day for i, day in enumerate(MONTH_NAME,start=1)},
                default="unknown"
            ).alias('month_name')
        )
        .sort('month')
    )

    return df_wd_prof_complete
def monthday_mean_profit(df):

    df_season = df.with_columns(
                    pl.col('CloseTime').dt.day().alias('day'),
                    )
    
  
    # df_season.head()

    #Agrupo los profit por día de semana
    
    
    df_wd_prof = df_season.group_by('day','Type_sample').agg(pl.col('Profit').mean())
    #fabrico DF para los días faltantes
    # df_wd_tmp =pl.DataFrame({'day':[i+1 for i in range(12)],'Profit':[0.0 for i in range(12)]})
    # cast al formato esperado
    # df_wd_tmp=df_wd_tmp.cast({'day':pl.Int8})
    #uno y obtengo el dia de la semana vs media de profits y ordenado

    # df_wd_prof=df_wd_prof.merge_sorted(df_wd_tmp,key="day").group_by('day').agg(pl.col('Profit').sum()).sort('day')
    return df_wd_prof


def fig_main_drawdown(df,symbol='')->Figure:

    
    #revisa que las fechas esten dentro de los parametros
    
    #Dibuja la linea retornos
    fig = make_subplots(rows=2, cols=1,shared_xaxes=True,subplot_titles=("Return", "Drawdown"))
    
    figure0 = Scatter(x=df['CloseTime'], y=df['Balance'],
                line = dict(color='#3E7CFE'),
                name="Close Price"
                
                )
    
 
    
    mean_drawdown=0
    max_close = df['Balance'].max()
    min_close = df['Balance'].min()
    df_tmp =    df.filter((pl.col('Type_sample')=='OOS') )
    figure_0b = Scatter(x=df_tmp['CloseTime'], y = [max_close for _ in range(df_tmp.shape[0]) ],
                                line = dict(color='rgba(0,0,0,0)'),
                                fill='tozeroy', 
                                fillcolor =' rgba(114, 161, 144,0.5)',
                                name="OOS")


    fig.add_trace(figure_0b,row=1, col=1)
    fig.add_trace(figure0,row=1, col=1,)


    #Grafica drawdown
    delta=(max_close-min_close)*.2
    fig.update_yaxes(range=[min_close-(delta),max_close+delta],row=1, col=1)


    figure2 = Scatter(x=df['CloseTime'], y = df['Drawdown_pct'],
                                line = dict(color='rgba(230, 30, 30,1)'),
                                fill='tozeroy', 
                                fillcolor = 'rgba(219, 66, 66,0.8)',name="Drawdown")
    figure1 = Scatter(x=df['CloseTime'], y = [mean_drawdown for _ in range(df.shape[0])],
                                line = dict(color='#FF003E',dash = 'dash'),name = "Mean dr")

    fig.add_trace(figure1, row=2, col=1)
    
    fig.add_trace(figure2, row=2, col=1)
    fig.update_layout(height=800,title=f"{symbol}")
    return fig

def dist_returns(df)->Figure:
    fig = px.histogram(df, x="Profit",color='Type_sample',
                       marginal="box",# or violin, rug
                       labels={'Profit':"Profits", 'count':'Frec','Type_sample':"Tipo"})
    fig.update_yaxes(title={'text':'Frec'})

    return fig

def fig_profit_weekday(df)->Figure:
    df=weekday_mean_profit(df)
    fig = px.bar(df, x="weekday_name",y='Profit',color='Type_sample', barmode='group'
            ,labels={'weekday_name':"Week day", 'count':'Frec','Type_sample':"IS/OS"}
            )
    
    fig.update_yaxes(title={'text':'Frec'})
   
    return fig

def fig_profit_month(df)->Figure:
    df=month_mean_profit(df)
    fig = px.bar(df, x="month_name",y='Profit',color='Type_sample', barmode='group'
                 ,labels={'month_name ':"Week day", 'count':'Frec','Type_sample':"IS/OS"}
                   )
    
    fig.update_yaxes(title={'text':'Frec'})
   
    return fig
    
def fig_profit_day(df)->Figure:
    df=monthday_mean_profit(df)
    
    fig = px.bar(df, x="day",y='Profit',color='Type_sample', barmode='group'
            ,labels={'weekday_name':"Week day", 'count':'Frec','Type_sample':"IS/OS"}
            )
    
    fig.update_yaxes(title={'text':'Frec'})
   
    return fig
