import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import Line,Bar,Scatter,Layout,Figure
from datetime import datetime as dt
import  polars as pl
def fig_main_drawdown(df,
                      start_date=dt.now(),
                      end_date=dt.now(),
                      start_date_oos=dt.now(),
                      end_date_oos=dt.now(),
                      symbol='')->Figure:

    df_start_date= df['OpenTime'][0]
    df_end_date= df['CloseTime'][-1]
    
    #revisa que las fechas esten dentro de los parametros
    if (start_date>df_start_date):
        print('true')
        df=df.filter((pl.col('OpenTime')>=start_date) )
    if (end_date<df_end_date):
        print('true')
        df=df.filter((pl.col('CloseTime')<=end_date))
    
    
    #Dibuja la linea retornos
    fig = make_subplots(rows=2, cols=1,shared_xaxes=True,subplot_titles=("Return", "Drawdown"))
    
    figure0 = Scatter(x=df['CloseTime'], y=df['Balance'],
                line = dict(color='#3E7CFE'),
                name="Close Price"
                
                )
    
 
    
    mean_drawdown=0
    max_close = df['Balance'].max()
    min_close = df['Balance'].min()
    df_tmp =    df.filter((pl.col('OpenTime')>=start_date_oos) & (pl.col('CloseTime')<=end_date_oos))
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