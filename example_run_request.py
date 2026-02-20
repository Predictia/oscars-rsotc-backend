import requests

body = {
    "dataset": "ERA5",
    "variable": "r1mm;r20mm",
    "pressure_level": "None",
    "region_set": "NUTS-3",
    "region_name": "ES130",
    "period": "1940-2026",
    "season_filter": "01-12",
    "reference_period": "1981-2010",
}
response = requests.post(
    "https://dev.oscars-rsotc.predictia.es/api/time_series", json=body
)
if response.status_code == 200:
    data = response.json()
    # Process the data as needed
else:
    print("Error fetching data:", response.status_code)
