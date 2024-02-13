import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from datetime import datetime, timedelta

import mongo_price_table

def create_and_train_model(coin_name):
    data_query = list(mongo_price_table.CryptoPriceClass.objects.filter()) # Only select the specific coin

    if len(data_query) == 0:
        return None

    data = [{'predict': item.predict, 'time': item.time, 'ratio': item.ratio} for item in data_query]

    df = pd.DataFrame(data)

    df["price"] = df["price"].astype(float)
    df["ratio"] = df["ratio"].astype(float)
    df["predict"] = df["predict"].astype(float)

    # Adding missing columns check
    if not {'time', 'predict_price', 'price', 'ratio'}.issubset(df.columns):
        raise ValueError('Columns time, predict_price, volume, price, macd, signal, and/or rsi are not present in the data.')

    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Create labels by shifting the prediction price to the previous row
    df["y"] = df["predict_price"].shift(-1)
    df.dropna(inplace=True)

    # Split the data into features and target
    X = df[['ratio', 'price']]
    y = df['y']

    # Create and train the neural network model
    model = Sequential()
    model.add(Dense(32, input_dim=2, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(1, activation='linear'))

    model.compile(loss='mean_squared_error', optimizer='adam')

    model.fit(X, y, epochs=50, batch_size=10, verbose=0)

    return model

def predict_price(model, price, ratio):
    # Create a feature vector for prediction using the provided inputs
    input_data = np.array([ratio, price]).reshape(1, -1)

    # Predict the next 'predict_price'
    predicted_value = model.predict(input_data)

    return predicted_value[0,0]  # As the output of model.predict is 2D, we need to pick only first element