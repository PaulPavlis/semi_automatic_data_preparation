# python test_data/preparation_for_evaluation_dataset/temp.py

import pandas as pd
import random
from random import randrange
import numpy as np
random.seed(420)


df = pd.read_csv("stored_user_files\\active_dataset\\hotel_bookings_prepared.csv")

for index, row in df.iterrows():
    if row["reservation_status_Canceled"] == 1:
        reservation_status = "Canceled"
    if row["reservation_status_Check-Out"] == 1:
        reservation_status = "Check-Out"
    if row["reservation_status_No-Show"] == 1:
        reservation_status = "No-Show"
    df.at[index, "reservation_status"] = reservation_status

print(df)

df.to_csv("test_data\\preparation_for_evaluation_dataset\\hotel_bookings_prepared.csv")