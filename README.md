# Stock Price Range Prediction with Random Forest

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
A machine learning project that forecasts the next-day stock price range using a Random Forest Regressor trained on historical data from Yahoo Finance. This project automates the entire pipeline from data fetching to generating a final, shareable report.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Example Output](#example-output)
- [Project Flow](#project-flow)
- [License](#license)
- [Contact](#contact)

---

## Project Overview
This project predicts the next day's stock price range by first predicting the **next day's daily return** using a Random Forest Regressor. It uses Open, High, Low, Close, Volume (OHLCV) data along with several days of lagged daily returns as features to train the model. [cite_start]The final output is a user-friendly report containing performance metrics and price predictions in multiple currencies[cite: 4].

---

## Key Features
- **Automated Data Ingestion**: Fetches the latest historical stock data using the `yfinance` library.
- **Time-Series Feature Engineering**: Automatically calculates and uses lagged daily returns to capture recent trends.
- [cite_start]**Multi-Currency Prediction**: Provides the final predicted price range in USD, EUR, and INR[cite: 4].
- [cite_start]**Performance Evaluation**: Calculates Mean Squared Error (MSE) and directional accuracy for model evaluation[cite: 4].
- [cite_start]**Automated Report Generation**: Generates a professional Microsoft Word (`.docx`) report containing results, tables, and plots[cite: 1, 2].

---

## Tech Stack
- **Data Manipulation**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (RandomForestRegressor)
- **Data Source**: yfinance
- **Visualization**: Matplotlib
- **Report Generation**: python-docx, prettytable

---

## Installation and Setup
To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Shreyasnijaguli/Stock-Market.git
    cd Stock-Market
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

**Steps to run the script:**
1. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
2. Modify the `top_stocks_problem_2` list in `script.py` to include the stock symbols you want to analyze (e.g., `['AAPL', 'MSFT', 'GOOG']`).
3. Run the script:
   ```bash
   python script.py
   ```
4. The output prediction ranges will be printed directly to the console.

---

## Example Output
After running the notebook, the script generates a prediction summary in the console, plots for each stock, and a final compiled Word report.

### 1. Console Prediction Summary
A summary table is displayed in the console with key performance metrics for each stock: MSE, accuracy, and predicted price ranges. For example, the model predicted the next-day range for MSFT with an accuracy of 52.80% and an MSE of 0.0003.

![Prediction Summary Table](Screenshot%202025-08-28%20231542.png)

### 2. Visualizations
The script generates plots showing historical prices and model performance. The second plot compares the actual daily return (blue) against the predicted return (red). The model's accuracy for AAPL was 51.20%.

![AAPL Stock Price and Return Prediction](Screenshot%202025-08-28%20231529.jpg)

### 3. Final Word Report
[cite_start]The main output is a `Stock_Report.docx` file that organizes all results into a shareable document, containing a summary table and all generated graphs[cite: 1, 2, 4].

---
---

## Project Flow
This diagram illustrates the end-to-end workflow of the project.

```mermaid
flowchart TD
    A["Historical Stock Data (OHLCV from yfinance)"] --> B["Calculate Daily Return"]
    B --> C["Create Lag Features: lag_1 ... lag_5"]
    C --> D["Combine: OHLCV + Lag Features"]
    D --> E["Random Forest Regressor"]
    E --> F["Predict Next-Day Daily Return"]
    F --> G["Convert to Next-Day Price Range in USD/EUR/INR"]
    G --> H["Generate Formatted Word Report (.docx)"]
