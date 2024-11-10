import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import Line,Bar,Scatter,Layout,Figure
from datetime import datetime as dt
import  polars as pl
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
                       marginal="box", # or violin, rug
                       labels={'Profit':"Profits", 'count':'Frec','Type_sample':"Tipo"})
    fig.update_yaxes(title={'text':'Frec'})

    return fig
    