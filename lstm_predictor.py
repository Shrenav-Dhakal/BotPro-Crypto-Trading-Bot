import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
import numpy as np

class LSTMPredictorApp(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title("LSTM Predictor Window")

        # Components for the LSTM Predictor window
        self.label = tk.Label(self, text="LSTM Predictor Window")
        self.label.pack(pady=20)

        # Dropdown list for cryptocurrencies
        self.crypto_var = tk.StringVar()
        self.crypto_dropdown = ttk.Combobox(self, textvariable=self.crypto_var)
        self.crypto_dropdown['values'] = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'BCH-USD']  # Add more cryptocurrencies as needed
        self.crypto_dropdown.set('Select Cryptocurrency')
        self.crypto_dropdown.pack(pady=10)

        # Entry widget for start date
        self.start_date_var = tk.StringVar()
        self.start_date_entry = tk.Entry(self, textvariable=self.start_date_var, width=20)
        self.start_date_entry.pack(pady=5)
        self.start_date_label = tk.Label(self, text="Start Date (YYYY-MM-DD):")
        self.start_date_label.pack(pady=5)

        # Entry widget for end date
        self.end_date_var = tk.StringVar()
        self.end_date_entry = tk.Entry(self, textvariable=self.end_date_var, width=20)
        self.end_date_entry.pack(pady=5)
        self.end_date_label = tk.Label(self, text="End Date (YYYY-MM-DD):")
        self.end_date_label.pack(pady=5)

        # Entry widget for future days
        self.future_days_var = tk.StringVar()
        self.future_days_entry = tk.Entry(self, textvariable=self.future_days_var, width=10)
        self.future_days_entry.pack(pady=5)
        self.future_days_label = tk.Label(self, text="Future Days:")
        self.future_days_label.pack(pady=5)

        # Predict button
        self.predict_button = tk.Button(self, text="Predict", command=self.predict_crypto)
        self.predict_button.pack(pady=10)

        # Text widget to display predicted future prices
        self.result_text = tk.Text(self, height=10, width=60, wrap=tk.WORD)
        self.result_text.pack(pady=10)

        # Figure for plotting
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def plot_prices_predictions(self, df, predictions):
        # Plotting close prices
        self.ax.plot(df['Close'], label='Close Prices', color='blue')

        # Plotting predictions
        valid = df[len(df) - len(predictions):]
        valid['Predictions'] = predictions
        self.ax.plot(valid[['Close', 'Predictions']], label=['Actual Prices', 'Predicted Prices'], color=['blue', 'red'], linestyle='dashed')

        self.ax.set_title('Model Predictions')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Close Price USD')
        self.ax.legend()
        self.canvas.draw()

    def display_future_prices_table(self, future_dates, future_prices):
        table_str = "Date\t\tPredicted Price\n"
        for date, price in zip(future_dates, future_prices):
            table_str += f"{date}\t\t{price}\n"

        self.result_text.delete(1.0, tk.END)  # Clear previous results
        self.result_text.insert(tk.END, table_str)

    def show_wait_message(self):
        messagebox.showinfo("Please Wait", "The model is running. Please wait...")

    def hide_wait_message(self):
        self.withdraw()  # Hide the Toplevel window
        self.deiconify()  # Show the Toplevel window again

    def predict_crypto_price(self, symbol, start_date, end_date, future_days):
        # Fetch cryptocurrency price data
        df = yf.download(symbol, start=start_date, end=end_date)

        # Extract and scale the closing prices
        data = df.filter(['Close']).values
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # Split data into training and testing sets
        training_data_len = int(np.ceil(len(data) * 0.8))
        train_data = scaled_data[0:training_data_len, :]

        # Create sequences of 60 consecutive closing prices for training
        X_train, y_train = [], []
        for i in range(60, len(train_data)):
            X_train.append(train_data[i-60:i, 0])
            y_train.append(train_data[i, 0])

        X_train, y_train = np.array(X_train), np.array(y_train)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

        # Build and train the LSTM model
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(LSTM(50, return_sequences=True))
        model.add(LSTM(100))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')

        # Show wait message
        self.show_wait_message()

        # Train the model
        model.fit(X_train, y_train, batch_size=1, epochs=10)

        # Hide wait message
        self.hide_wait_message()

        # Create sequences for the test set
        test_data = scaled_data[training_data_len - 60:, :]
        X_test = []
        y_test = data[training_data_len:, :]
        for i in range(60, len(test_data)):
            X_test.append(test_data[i-60:i, 0])

        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        # Make predictions on the test set
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)

        # Plot prices and predictions
        self.plot_prices_predictions(df, predictions)

        # Display the predicted future prices
        future_prices = []
        last_60_days = scaled_data[-60:, :]
        for _ in range(future_days):
            X_future = np.array([last_60_days])
            X_future = np.reshape(X_future, (X_future.shape[0], X_future.shape[1], 1))
            predicted_price = model.predict(X_future)
            last_60_days = np.append(last_60_days, predicted_price, axis=0)[1:]
            future_prices.append(predicted_price[0, 0])

        # Denormalize the predicted prices
        future_prices = scaler.inverse_transform(np.array([future_prices]).T).flatten()

        # Display the predicted future prices in the text widget
        future_dates = pd.date_range(end=end_date, periods=future_days + 1, freq='B')[1:]
        self.display_future_prices_table(future_dates, future_prices)

    def predict_crypto(self):
        # Get the selected cryptocurrency, start date, end date, and future days
        selected_crypto = self.crypto_var.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        future_days = int(self.future_days_var.get())

        # Validate input
        if not selected_crypto or not start_date or not end_date or not future_days:
            messagebox.showinfo("Error", "Please fill in all fields.")
            return

        try:
            future_days = int(future_days)
        except ValueError:
            messagebox.showinfo("Error", "Please enter a valid number for future days.")
            return

        # Perform prediction
        self.predict_crypto_price(selected_crypto, start_date, end_date, future_days)


