# python test_data/preparation_for_evaluation_dataset/messify_hotel_bookings.py

import pandas as pd
import random
from random import randrange
import numpy as np
random.seed(420)


df = pd.read_csv("test_data\preparation_for_evaluation_dataset\hotel_bookings.csv")

# Remove about 90% of the rows to increase performance
df = df.sample(frac=0.1, random_state=42)

# Try not to overload participants with too many columns
df = df.drop(columns=["arrival_date_week_number", "arrival_date_year", "arrival_date_month", "arrival_date_day_of_month", "is_canceled", "reserved_room_type", "assigned_room_type", "booking_changes", "required_car_parking_spaces", "total_of_special_requests"])

# # Clarify abbreviation
# df.rename(columns={"adr": "average_daily_rate"}, inplace=True)

# Generate unclean data additionally to unclean data present
for index, row in df.iterrows():
    # For missing values
    if randrange(10) == 0:
        df.at[index, "adults"] = np.nan
        df.at[index, "children"] = np.nan
        df.at[index, "babies"] = np.nan
    if randrange(1000) == 0:
        df.at[index, "previous_bookings_not_canceled"] = np.nan
    if randrange(5) == 0:
        df.at[index, "reservation_status"] = "missing_status"

    # For capping
    if randrange(100) == 0:
        df.at[index, "lead_time"] = 1000 + randrange(5000)
    if randrange(1000) == 0:
        df.at[index, "adults"] = 10 + randrange(50)
    if randrange(1000) == 0:
        df.at[index, "reservation_status_date"] = '1970-01-01'
    if randrange(500) == 0:
        df.at[index, "stays_in_weekend_nights"] = 20 + randrange(50)
        df.at[index, "stays_in_week_nights"] = 30 + randrange(100)
    
    # For filtering
    if randrange(20) == 0:
        df.at[index, "customer_type"] = "error"
    
    # Add duplicates
    if randrange(200) == 0:
        df.append(row)

print(df)
print(df.columns)
print(df.isna().sum())

df.to_csv("test_data\preparation_for_evaluation_dataset\hotel_bookings_unclean.csv")