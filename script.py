#full 50+ stock price prediction with conversion rates fixed after confirming the outside sources and obtaining historical data from Yahoo Finance
# use README for more information on the calculations  
# Install necessary packages (uncomment if needed)
# !pip install yfinance scikit-learn prettytable

# Ensure that matplotlib plots display inline in Colab
# %matplotlib inline

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import time
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, accuracy_score
from prettytable import PrettyTable
import os
from docx import Document
from docx.shared import Inches

# Set fixed conversion rates (approximate)
CONVERSION_RATE_EUR = 0.93   # 1 USD ≈ 0.93 EUR
CONVERSION_RATE_INR = 82.0   # 1 USD ≈ 82 INR

# Function to calculate daily returns with fallback for missing 'Adj Close'
def calculate_daily_returns(stock_data):
    if 'Adj Close' not in stock_data.columns:
        if 'Close' in stock_data.columns:
            stock_data['Adj Close'] = stock_data['Close']
        else:
            raise KeyError("Neither 'Adj Close' nor 'Close' available in data")
    stock_data['Daily Return'] = stock_data['Adj Close'].pct_change()
    stock_data.dropna(inplace=True)
    return stock_data

# Function to create lag features based on daily returns
def create_lag_features(stock_data, num_days=5):
    for i in range(1, num_days + 1):
        stock_data[f'lag_{i}'] = stock_data['Daily Return'].shift(i)
    stock_data.dropna(inplace=True)
    return stock_data

# Function to train a Random Forest Regressor model
def train_random_forest_model(X_train, y_train):
    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    return model

# Function to visualize results
def visualize_results(stock_symbol, historical_data, y_test, predictions, accuracy, error_margin):
    try:
        plt.figure(figsize=(12, 8))
        # Plot historical stock prices
        plt.subplot(2, 1, 1)
        plt.plot(historical_data.index, historical_data['Adj Close'], label='Adj Close Price')
        plt.title(f'{stock_symbol} Stock Prices')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        # Plot actual and predicted daily returns
        plt.subplot(2, 1, 2)
        plt.plot(y_test.index, y_test, color='blue', label='Actual Daily Return')
        plt.plot(y_test.index, predictions, color='red', label='Predicted Daily Return')
        plt.scatter(y_test.index, y_test, color='blue')
        plt.scatter(y_test.index, predictions, color='red')
        plt.xlabel('Date')
        plt.ylabel('Daily Return')
        plt.legend()
        # Annotate accuracy and error margin
        plt.annotate(f'Accuracy: {accuracy * 100:.2f}%', xy=(0.05, 0.85), xycoords='axes fraction')
        plt.annotate(f'Error Margin: {error_margin * 100:.2f}%', xy=(0.05, 0.80), xycoords='axes fraction')
        plt.tight_layout()
        plt.savefig(f"{stock_symbol}_stock_graph.png")
        plt.close()
    except Exception as e:
        print(f"Visualization error for {stock_symbol}: {e}")

# Function to evaluate the model and show predictions on a test split
def evaluate_model(stock_symbol, X_test, y_test, predictions, historical_data):
    try:
        mse = mean_squared_error(y_test, predictions)
        # Directional accuracy: comparing the sign of actual vs. predicted returns
        acc = accuracy_score(np.sign(y_test), np.sign(predictions))
        error_margin = 1 - acc
        visualize_results(stock_symbol, historical_data, y_test, predictions, acc, error_margin)
        return mse, acc
    except Exception as e:
        print(f"Error evaluating model for {stock_symbol}: {e}")
        return None, None

# Function to process a single stock symbol with retries and error handling,
# and also to predict the next day's price range in USD, EUR, and INR.
def run_problem_1(stock_symbol):
    try:
        attempts = 0
        stock_data = None
        # Use today's date as the end date
        end_date = datetime.today().strftime("%Y-%m-%d")
        # Try up to 3 times to download data (handle rate limits)
        while attempts < 3:
            try:
                stock_data = yf.download(stock_symbol, start='2020-01-01', end=end_date)
                break
            except Exception as e:
                print(f"Download error for {stock_symbol} (attempt {attempts+1}): {e}")
                attempts += 1
                time.sleep(5)
        if stock_data is None or stock_data.empty:
            print(f"Skipping {stock_symbol} due to download issues or no data.")
            return None, None, None, None, None, None

        # Process data: calculate daily returns and create lag features
        stock_data = calculate_daily_returns(stock_data)
        stock_data = create_lag_features(stock_data, num_days=5)

        # Prepare features and target variable
        X = stock_data.drop(['Daily Return'], axis=1)
        y = stock_data['Daily Return']
        if X.empty or y.empty:
            print(f"Insufficient data for {stock_symbol} after processing.")
            return None, None, None, None, None, None

        # Split for evaluation (time series split without shuffling)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = train_random_forest_model(X_train, y_train)
        predictions = model.predict(X_test)
        mse, acc = evaluate_model(stock_symbol, X_test, y_test, predictions, stock_data)

        # --- Next Day Prediction using entire historical data ---
        model_all = train_random_forest_model(X, y)
        # Use the last row of features as a proxy for next day's input
        last_features = X.iloc[-1].values.reshape(1, -1)
        tree_preds = [estimator.predict(last_features)[0] for estimator in model_all.estimators_]
        predicted_return_range = (min(tree_preds), max(tree_preds))
        # Ensure last_adj_close is a scalar float:
        last_adj_close = X.iloc[-1]['Adj Close']
        if isinstance(last_adj_close, pd.Series):
            last_adj_close = last_adj_close.iloc[0]
        last_adj_close = float(last_adj_close)
        # Next day's predicted price range in USD:
        next_day_range_usd = (last_adj_close * (1 + predicted_return_range[0]),
                              last_adj_close * (1 + predicted_return_range[1]))
        # Convert to EUR and INR:
        next_day_range_eur = (next_day_range_usd[0] * CONVERSION_RATE_EUR,
                              next_day_range_usd[1] * CONVERSION_RATE_EUR)
        next_day_range_inr = (next_day_range_usd[0] * CONVERSION_RATE_INR,
                              next_day_range_usd[1] * CONVERSION_RATE_INR)

        print(f"{stock_symbol} next day predicted price range (USD): {next_day_range_usd}")
        print(f"{stock_symbol} next day predicted price range (EUR): {next_day_range_eur}")
        print(f"{stock_symbol} next day predicted price range (INR): {next_day_range_inr}")

        return predictions, mse, acc, next_day_range_usd, next_day_range_eur, next_day_range_inr
    except Exception as e:
        print(f"Error processing {stock_symbol}: {e}")
        return None, None, None, None, None, None

# Function to run the analysis for multiple stock symbols
def run_problem_2(stock_symbols):
    all_predictions = []
    all_mse = []
    all_accuracy = []
    all_next_day_ranges_usd = []
    all_next_day_ranges_eur = []
    all_next_day_ranges_inr = []
    processed_symbols = []  # store symbols that were processed successfully

    for stock_symbol in stock_symbols:
        print(f"\nProcessing {stock_symbol}...")
        preds, mse, acc, next_day_usd, next_day_eur, next_day_inr = run_problem_1(stock_symbol)
        if preds is not None:
            all_predictions.append(preds)
            all_mse.append(mse)
            all_accuracy.append(acc)
            all_next_day_ranges_usd.append(next_day_usd)
            all_next_day_ranges_eur.append(next_day_eur)
            all_next_day_ranges_inr.append(next_day_inr)
            processed_symbols.append(stock_symbol)
        time.sleep(2)  # brief delay to reduce rate limit issues

    if all_predictions:
        average_mse = np.mean(all_mse)
        average_accuracy = np.mean(all_accuracy)
        print(f'\nAverage Mean Squared Error for processed stocks: {average_mse}')
        print(f'Average Accuracy for processed stocks: {average_accuracy * 100:.2f}%')
        result_table = PrettyTable()
        result_table.field_names = ["Stock Symbol", "MSE", "Accuracy",
                                    "Next Day Range (USD)", "Next Day Range (EUR)", "Next Day Range (INR)"]
        for i, symbol in enumerate(processed_symbols):
            result_table.add_row([
                symbol,
                all_mse[i],
                f"{all_accuracy[i]*100:.2f}%",
                all_next_day_ranges_usd[i],
                all_next_day_ranges_eur[i],
                all_next_day_ranges_inr[i]
            ])
        print(result_table)

        # Generate Word Document
        print("\nGenerating Word Document...")
        doc = Document()
        doc.add_heading('Stock Prediction Report', level=1)
        doc.add_paragraph("Stock Price and Daily Return Graphs:")
        
        for symbol in processed_symbols:
            filename = f"{symbol}_stock_graph.png"
            if os.path.exists(filename):
                doc.add_picture(filename, width=Inches(6))
            else:
                doc.add_paragraph(f"(Graph for {symbol} not found)")
                
        doc.add_paragraph("Note: Price ranges are printed with currency names (USD, EUR, INR).")
        
        headers = ["Stock Symbol", "MSE", "Accuracy", "Next Day Range (USD)", "Next Day Range (EUR)", "Next Day Range (INR)"]
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(headers):
            hdr_cells[i].text = col
            
        for i in range(len(processed_symbols)):
            row_cells = table.add_row().cells
            row_cells[0].text = processed_symbols[i]
            row_cells[1].text = str(round(all_mse[i], 4))
            row_cells[2].text = f"{all_accuracy[i]*100:.2f}%"
            row_cells[3].text = f"${all_next_day_ranges_usd[i][0]:.2f} - ${all_next_day_ranges_usd[i][1]:.2f}"
            row_cells[4].text = f"€{all_next_day_ranges_eur[i][0]:.2f} - €{all_next_day_ranges_eur[i][1]:.2f}"
            row_cells[5].text = f"₹{all_next_day_ranges_inr[i][0]:.2f} - ₹{all_next_day_ranges_inr[i][1]:.2f}"
            
        output_filename = "Stock_Report.docx"
        doc.save(output_filename)
        print(f"\nReport successfully saved to {output_filename}")

    else:
        print("No valid predictions were made.")

# Define a list of valid stock symbols (remove any that consistently fail)
top_stocks_problem_2 = list(set([
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'NVDA', 'INTC', 'IBM', 'CSCO',
    'V', 'PYPL', 'ADBE', 'CRM', 'QCOM', 'NFLX', 'GS', 'JPM', 'BA', 'MMM',
    'WMT', 'HD', 'VZ', 'T', 'DIS', 'KO', 'PEP', 'XOM', 'PFE',
    'JNJ', 'MRK', 'WFC', 'CVX', 'GOOG', 'GM', 'F', 'AMGN', 'C', 'CAT',
    'DD', 'GE', 'HPQ'
]))

if __name__ == "__main__":
    # Run the analysis for the defined stock symbols
    run_problem_2(top_stocks_problem_2)
