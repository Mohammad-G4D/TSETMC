import time
import pandas as pd
import requests

def Calendar(start_year, end_year):

  """Fetch calendar data for a specified range of Persian years from the API
  and save all records into a single CSV file.
  """
  all_new_rows = []

  # Loop through the specified year range
  for year in range(start_year, end_year + 1):
    url = f"https://pnldev.com/api/calender?year={year}"
    response = requests.get(url, timeout=10)
    data = response.json()

    if data.get("status"):
      year_data = data.get("result", {})

      # Iterate through months and days of the year
      for month_data in year_data.values():
        for day_info in month_data.values():
          solar = day_info.get("solar", {})
          moon = day_info.get("moon", {})

          s_year = solar.get("year")
          s_month = solar.get("month")
          s_day = solar.get("day")

          # Format solar date as YYYY-MM-DD
          date = f"{s_year}-{s_month:02d}-{s_day:02d}"

          # Format lunar date safely
          qamari_month = moon.get("month")
          qamari_day = moon.get("day")
          qamari_str = (
              f"{qamari_month:02d}-{qamari_day:02d}"
              if qamari_month and qamari_day
              else ""
          )

          all_new_rows.append({
              "date": date,
              "is_holiday": 1 if day_info.get("holiday") else 0,
              "qamari_date": qamari_str,
          })

    # Short pause between requests
    time.sleep(0.2)

  # Create DataFrame and save to CSV
  df = pd.DataFrame()
  if all_new_rows:
    df = pd.DataFrame(all_new_rows)
    df.to_csv("Calendar.csv", index=False, encoding="utf-8-sig")

  return df

