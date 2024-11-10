import streamlit as st
from datetime import datetime as dt
import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
import file_service as fscv
import visualization as vs

st.set_page_config(layout="wide")

st.header   ("Backtest mt4 analisis")

def date_to_datetime(_date):
    return dt.combine(_date,dt.min.time())
with st.sidebar:
    with st.container(border=True):
        st.subheader('Parametros iniciales')
        
        fileOpen = st.file_uploader("Seleccione html mt4 backtest",accept_multiple_files=False,type =['htm'])
        
        st.session_state.archivo_cargado  = False
        st.session_state.st_date=dt.now()
        st.session_state.end_date=dt.now()

        if fileOpen:
            try:
                operations_df=fscv.load_file_st(fileOpen)
            except :
                st.error("Error al cargar el archivo")
            st.session_state.archivo_cargado  = True
            st.session_state.st_date=operations_df['OpenTime'].min()
            st.session_state.end_date=operations_df['CloseTime'].max()
            
            
        ks_threshold = 0.2  # Define el umbral para sobreoptimización (20%)

        start_date= st.date_input("Fecha de inicio",value=st.session_state.st_date,disabled=not st.session_state.archivo_cargado)
        
        end_date= st.date_input("Fecha de finalización",value=st.session_state.end_date,disabled=not st.session_state.archivo_cargado)
        start_date_oos= st.date_input("Fecha de inicio OOS",value=st.session_state.st_date,disabled=not st.session_state.archivo_cargado)
        end_date_oos= st.date_input("Fecha de finalización OOS",value=st.session_state.end_date,disabled=not st.session_state.archivo_cargado)

        ks_th=st.number_input("KS threshold",ks_threshold,disabled=not st.session_state.archivo_cargado)
        submitted = st.button('Submit',disabled=not st.session_state.archivo_cargado)
    

            
        
        
tab1, tab2, tab3 = st.tabs(["Datos", "Métricas", "Distribución de retornos"])
            
with tab1:
    st.header('Datos')
    if submitted and  operations_df is not None and operations_df.shape[0]>1:
            operations_df=operations_df.with_columns(pl.when((pl.col('OpenTime')>=start_date_oos) & (pl.col('OpenTime')<=end_date_oos))
                    .then(pl.lit("OS")).otherwise(pl.lit("IS")).alias("Type_sample"))
            
            st.dataframe(operations_df)
            fig = vs.fig_main_drawdown(operations_df,
                                 date_to_datetime(start_date),
                                 date_to_datetime(end_date),
                                 date_to_datetime(start_date_oos),
                                 date_to_datetime(end_date_oos))
            st.plotly_chart(fig)

            
with tab2:
    st.header('Métricas')
    if submitted and operations_df is not None and operations_df.shape[0]>1:
            st.write(operations_df)
    
with tab3:
    st.header('Distribución de retornos')
        

            