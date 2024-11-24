import requests
import polars as pl
from typing import List

# polars configuration so that printing the dataframes gives the desired result
pl.Config.set_tbl_hide_dataframe_shape(True)


def get_country_data(base_url: str, country_code: str) -> requests.Response:
    return requests.get(f"{base_url}/countries/{country_code}")


def find_missing_countries(base_url: str, df_countries: pl.DataFrame) -> List[str]:
    missing_countries = []
    for row in df_countries.iter_rows(named=True):
        data = get_country_data(base_url=base_url, country_code=row["code"])

        if data.status_code == 404:
            missing_countries.append(row["name"])
        else:
            if (
                data.headers["X-Code-Flag"]
                != "Almost.. but our princess is in another castle!"
            ):
                print(data.headers["X-Code-Flag"])

    return missing_countries


def main() -> None:
    base_url = "http://code001.ecsbdp.com"

    # Part 1
    countries_url = (
        "https://sacodeassessment.blob.core.windows.net/public/countries.csv"
    )
    df_countries = pl.read_csv(countries_url)

    missing_countries = find_missing_countries(
        base_url=base_url, df_countries=df_countries
    )

    print(missing_countries)

    # Part 2
    # create empty text file revenues.txt
    with open("revenues.txt", "w+") as _:
        pass

    files = {"file": open("revenues.txt", "rb")}

    response = requests.post(url=f"{base_url}/revenues?client=abc123", data=files)
    if response.status_code == 201:
        print("Succesfully uploaded file")
    else:
        print(f"Error during uploading file, error code: {response.status_code}")


main()
