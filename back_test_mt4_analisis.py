import streamlit as st
import datetime
import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
import file_service as fscv

st.set_page_config(layout="wide")

st.header   ("Backtest mt4 analisis")
def enable_fx(state:bool):
    return not state
with st.sidebar:
    with st.container(border=True):
        st.subheader('Parametros iniciales')
        
        fileOpen = st.file_uploader("Seleccione html mt4 backtest",accept_multiple_files=False,type =['htm'])
        
        st.session_state.archivo_cargado  = False

        if fileOpen:
            try:
                operations_df=fscv.load_file_st(fileOpen)
            
            except :
                st.error("Error al cargar el archivo")
            st.session_state.archivo_cargado  = True
            
        ks_threshold = 0.2  # Define el umbral para sobreoptimización (20%)
        toDate = datetime.datetime.now()

        fromDate = datetime.date(2003,1,1)
        jan_1 = datetime.date(fromDate.year,1,1)
        dec_31 = datetime.date(fromDate.year,12,31)

        fromDate= st.date_input("Fecha de inicio",fromDate,disabled=not st.session_state.archivo_cargado)
        
        toDate= st.date_input("Fecha de finalización",toDate,disabled=not st.session_state.archivo_cargado)
        toDate= st.date_input("Fecha de inicio OOS",toDate,disabled=not st.session_state.archivo_cargado)
        toDate= st.date_input("Fecha de finalización OOS",toDate,disabled=not st.session_state.archivo_cargado)

        submitted = st.button('Submit',disabled=not st.session_state.archivo_cargado)
    
    
            
        
        
tab1, tab2, tab3 = st.tabs(["Datos", "Métricas", "Distribución de retornos"])
            
with tab1:
    st.header('Datos')
    if submitted:
        if operations_df is not None and operations_df.shape[0]>1:
            st.write(operations_df)
with tab2:
    st.header('Métricas')
    if submitted:
        if operations_df is not None and operations_df.shape[0]>1:
            st.write(operations_df)
    
with tab3:
    st.header('Distribución de retornos')
        

            