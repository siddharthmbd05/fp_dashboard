'''sources used
1)https://github.com/luigibr1/Streamlit-StockSearchWebApp
2)https://towardsdatascience.com/creating-a-financial-dashboard-using-python-and-streamlit-cccf6c026676
3)https://python.plainenglish.io/creating-an-awesome-web-app-with-python-and-streamlit-728fe100cf7
4)https://github.com/didizhx/Streamlit-Financial-Dashboard/blob/main/Streamlit%20Application%20Financial%20Programming%20(Yahoo).py
5)https://github.com/sumanthsripada/Financial-Analysis---Yahoo-Finance/blob/main/findash.py
6)https://github.com/didizhx/Streamlit-Financial-Dashboard/blob/main/Streamlit%20Application%20Financial%20Programming%20(Yahoo).py


'''
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_datareader.data as web

# main body 

# as learnt in class


ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
# Add multiple choices box
tickers = st.multiselect("Ticker(s)", ticker_list)

# --- Select date time ---

# Add select begin-end date
col1, col2 = st.columns(2)  # Create 2 columns
start_date = col1.date_input("Start date", datetime.today().date() - timedelta(days=30))
end_date = col2.date_input("End date", datetime.today().date())

# --- Add a button ---

get = st.button("Get data", key="get")

# --- Table to show data ---

# Add table to show stock data
# This function get the stock data and save it to cache to resuse

@st.cache
def GetStockData(tickers, start_date, end_date):
    global get
    # Loop through the selected tickers
    stock_price = pd.DataFrame()
    for tick in tickers:
            stock_df = yf.Ticker(tick).history(start=start_date, end=end_date)
            stock_df['Ticker'] = tick  # Add the column ticker name
            stock_price = pd.concat([stock_price, stock_df], axis=0)
            print(stock_price)# Comebine results
    return stock_price.loc[:, ['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]

    # def tab1
def tab1():
    
    # --- Line plot ---
    
    # Check if there is/are selected ticker(s)
    def ShowTable():
        global tickers
        global stock_price
        if len(tickers) > 0:
            st.write('Stock price data')
            stock_price = GetStockData(tickers, start_date, end_date)
            st.dataframe(stock_price)
    
    # --- Line plot ---
    
    # Add a line plot
    def ShowLinePlot():
        global tickers
        global stock_price
        if len(tickers) > 0:
            st.write('Close price')
            fig, ax = plt.subplots(figsize=(15, 5))
            for tick in tickers:
                stock_df = stock_price[stock_price['Ticker'] == tick]
                ax.plot(stock_df['Close'], label=tick)
            ax.legend()
            st.pyplot(fig)
        
    # --- Show the above table and plot when the button is clicked ---
    
    if get:
        ShowTable()
        ShowLinePlot()

# taken help from github source mentioned above(5), output as not desired so code has been changed accordingly
def tab2():       
    data_selction =  ['1month', '3month','6month','ytd','1year','2year','5year','max']
    period_selection =  col1.selectbox("time period", data_selction)
    time_interval = ['day','month','year']
    choose_time= col2.selectbox("Select time", time_interval)
    select_graph = st.radio("Select type", ["Line","Candle"])
    data = GetStockData(tickers, start_date, end_date)
    if select_graph == "Line":
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,vertical_spacing=0.07, subplot_titles=('Stock Trend', 'Volume'),row_width=[0.2, 0.7])
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'],name="Stock Trend",showlegend=True),row= 1,col = 1)
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'],name="Volume",showlegend=True),row=2,col = 1)
        fig.update_layout(title="line plot", yaxis_title="close")
        st.plotly_chart(fig)
# monte carlo simulation, error due to miscalculated data reading, took assistance from source 5 
def tab3():
    
    col1,col2 = st.columns([2,2])
    sims =  [200, 500,1000]
    sim =  col1.selectbox("Select simulations", sims)
    horizon = [30, 60,90]
    horizons= col2.selectbox("Select Horizon", horizon)
    

    stock_price = web.DataReader(tickers,start_date, end_date)
   
   
    close_price = stock_price['Close']
    daily_return = close_price.pct_change()
    daily_volatility = np.std(daily_return)

    
    #Monte Carlo
    np.random.seed(9)
    simulations = sim
    time_horizon = horizons

    simulation_df = pd.DataFrame()

    for i in range(simulations):
    
       next_price = []
       last_price = close_price[-1]
    
       for j in range(time_horizon):
          
           future = np.random.normal(0, daily_volatility)

         
           future_price = last_price * (1 + future)

           
           next_price.append(future_price)
           last_price = future_price
    
   
       simulation_df[i] = next_price

    fig, ax = plt.subplots()

    plt.plot(simulation_df)
    plt.title('Monte Carlo simulation')
    plt.xlabel('Day')
    plt.ylabel('Price')

    plt.axhline(y=close_price[-1], color='red')
    plt.legend(['Current stock price is: ' + str(np.round(close_price[-1], 2))])
    ax.get_legend().legendHandles[0].set_color('red')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
    
    ending_price = simulation_df.iloc[-1:, :].values[0, ]
    
    
    future_price_95ci = np.percentile(ending_price, 5)
    
  
    VaR = close_price[-1] - future_price_95ci
    st.write('VAR' + str(np.round(VaR, 2))) 
    
def run():
    
    tab_selection = st.sidebar.selectbox("Select tab", ['Summary','Chart','Monte Carlo Simulation'])
    if tab_selection == 'Summary':
       tab1()
    elif tab_selection == 'Chart' :
        tab2()
    elif tab_selection == 'Monte Carlo Simulation' :
        tab3()
run()

