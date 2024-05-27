# WQU Capstone Project: Forex Trading Bot

## Introduction

This project aims to develop an automated Forex trading bot using the OANDA API. The bot manages trades based on economic news impacts, technical indicators, and candlestick patterns. It pulls data, analyzes market conditions, and executes trades accordingly.

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.x
- oandapyV20
- pandas
- numpy
- TA-Lib
- plotly
- matplotlib

You will also need an OANDA API access token and account ID.

## Setup

1. **Clone the Repository**:  
   Clone the repository containing the project files.

2. **Install Required Libraries**:  
   Install the necessary Python libraries using pip:
   ```sh
   pip install oandapyV20 pandas numpy TA-Lib plotly matplotlib
   
3. **Configure OANDA API Credentials**:  
   Update the `access_token` and `accountID` variables with your OANDA API credentials in the script.

## Project Structure

- `main.py`: The main script that contains the logic for managing trades, pulling data, and executing orders.
- `Oanda_Connector/oandaClass.py`: Contains the Oanda_Connector class for interacting with the OANDA API.
- `fx_Econcalendar_2.py`: Module for pulling economic calendar data and identifying high-impact currencies.
- `oanda_backtest.py`: Script for backtesting trading strategies.

## How It Works

1. **Import Necessary Libraries**  
   The script starts by importing all the required libraries and modules for handling API requests, data manipulation, technical analysis, and plotting.

2. **Define Risk Parameters and Initialize Variables**  
   Set the risk percentage for each trade and initialize lists to keep track of open trades and break-even trades.

3. **OANDA API Access**  
   Configure the OANDA API access with the provided access token and account ID. Initialize the API client.

4. **Economic Calendar and Impacted Currencies**  
   Pull the economic calendar data to check for high-impact news events on currencies. Identify the currencies that are highly impacted and store them in a list.

5. **Trade Management Logic**  
   Manage existing trades by checking if they are in profit and adjusting stop losses or taking partial profits accordingly. The script evaluates each trade based on technical indicators and candlestick patterns.

6. **Data Collection for 1-Day Prices**  
   Pull 1-day pricing data for a list of major currency pairs. This data is used to evaluate new trading opportunities.

7. **Trade Execution Logic**  
   Execute buy or sell orders based on the signals from technical indicators and candlestick patterns. The script checks for various bullish and bearish patterns and places market orders accordingly.

8. **Exiting Existing Trades**  
   Exit trades when certain conditions are met, such as the crossing of technical indicators or the appearance of specific candlestick patterns.

9. **Loop Through Currency Pairs**  
   Create a loop to repeat the trade management and data collection steps for each currency pair. The loop ensures that all pairs are evaluated periodically.

## Running the Project

To run the project, execute the `main.py` script:
```sh
python main.py

Ensure that you monitor the output and logs to track the bot's performance and make adjustments as needed.

## Conclusion
This automated Forex trading bot leverages economic news, technical indicators, and candlestick patterns to make informed trading decisions. By continuously monitoring and managing trades, the bot aims to optimize trading performance and manage risk effectively.
