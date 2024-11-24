import polars as pl
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# Q1
# polars configuration so that printing the dataframes gives the desired result
pl.Config.set_tbl_hide_dataframe_shape(True)
pl.Config(set_tbl_rows=239)

# Reading the dataframes from the storageaccount, polars read_csv function handles this automatically
airports_url = "https://sacodeassessment.blob.core.windows.net/public/airports.csv"
countries_url = "https://sacodeassessment.blob.core.windows.net/public/countries.csv"
runways_url = "https://sacodeassessment.blob.core.windows.net/public/runways.csv"

df_airports = pl.read_csv(airports_url)
df_countries = pl.read_csv(countries_url)
# Because of null values we need to use more rows to infer the schema
df_runways = pl.read_csv(runways_url, infer_schema_length=10000)


# Combining the airport and country data
df_airports_per_country = df_countries.join(
    df_airports, left_on="code", right_on="iso_country", suffix="_airport"
)

df_airports_per_country = df_airports_per_country.rename(
    {"name": "country", "name_airport": "airport"}
)

# Aggregating the data
df_country_grouped_airports = df_airports_per_country.group_by("country").agg(
    pl.col("id").count().alias("n_airports")
)

# Printing results
print("The 3 countries with the most airports are:")
print(df_country_grouped_airports.sort("n_airports", descending=True).limit(3))

print("The 10 countries with the least airports are:")
print(df_country_grouped_airports.sort("n_airports", descending=False).limit(10))

print("All the 14 countries with only 1 airport are:")
print(df_country_grouped_airports.filter(pl.col("n_airports") == 1))


# Combining the combined airport and country data with the runway data
df_runway_per_airport_per_country = df_airports_per_country.join(
    df_runways, left_on="ident", right_on="airport_ident", suffix="_runway", how="inner"
).select("country", "airport", "length_ft", "width_ft")

# Filling null values
df_runway_per_airport_per_country = df_runway_per_airport_per_country.fill_null(0)

# Using a window like function to get the max per country
df_airport_per_country_with_longest_runway = (
    df_runway_per_airport_per_country.filter(
        pl.col("length_ft") == pl.max("length_ft").over("country")
    )
    .group_by("country")
    .agg(
        pl.col("airport"),
        pl.col("length_ft"),
        pl.col("width_ft"),
    )
)

# Print results
print(df_airport_per_country_with_longest_runway.sort("country"))

# Adding an extra condition on selecting the max width_ft runways
df_airport_per_country_with_longest_runway = (
    df_runway_per_airport_per_country.filter(
        (pl.col("length_ft") == pl.max("length_ft").over("country"))
        & (pl.col("width_ft") == pl.max("width_ft").over("country"))
    )
    .group_by("country")
    .agg(
        pl.col("airport"),
        pl.col("length_ft"),
        pl.col("width_ft"),
    )
)

## Print results
print(df_airport_per_country_with_longest_runway.sort("country"))

# Question 2

buffer = BytesIO()

account_name = "sacodeassessment"
account_url = f"https://{account_name}.dfs.core.windows.net"
container_name = "results"
blob_name = "ingest-assessment-202411230-RdH.csv"

# Storing the sas token in a separate file that is in the .gitignore
with open("sastoken.secret", "r") as f:
    sas_token = f.read().strip()
print(sas_token)

blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)

df_country_grouped_airports.write_csv(buffer, include_header=True)

blob_client = blob_service_client.get_blob_client(
    container=container_name, blob=blob_name
)

blob_client.upload_blob(buffer, overwrite=True)
