def fig_main_drawdown(df,
                      start_date=dt.now(),
                      end_date=dt.now(),
                      start_date_oos=dt.now(),
                      end_date_oos=dt.now(),
                      symbol='')->Figure:


    fig = make_subplots(rows=2, cols=1,shared_xaxes=True,subplot_titles=("Return", "Drawdown"))
    
    figure0 = Scatter(x=df['CloseTime'], y=df['Balance'],
                line = dict(color='#3E7CFE'),
                name="Close Price"
                
                )
    
    # df_temp = df.reset_index()
 
    
    mean_drawdown=0
    max_close = df['Balance'].max()
    min_close = df['Balance'].min()
    df_tmp =    df.filter((pl.col('OpenTime')>=start_date_oos) & (pl.col('CloseTime')<=end_date_oos))
    figure0B = Scatter(x=df_tmp['CloseTime'], y = [max_close for _ in range(df_tmp.shape[0]) ],
                                line = dict(color='rgba(0,0,0,0)'),
                                # fill='tonexty', 
                                fill='tozeroy', 
                                fillcolor =' rgba(114, 161, 144,0.5)',
                                name="OOS")
    # figure0A = Scatter(x=df_tmp['CloseTime'], y = [min_close for _ in range(df_tmp.shape[0])])


    fig.add_trace(figure0B,row=1, col=1)
    fig.add_trace(figure0,row=1, col=1,)
    # fig.add_trace(figure0A,row=1, col=1)
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
    # fig.update_yaxes(range=[df['drawdown'].min()*1.4,0], row=2, col=1)
    fig.update_layout(height=800,title=f"{symbol} - Monthly performance")
    return fig