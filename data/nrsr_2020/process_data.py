import pandas as pd
import json


def saveJson(obj, path):
    if(".json" not in path):
        path += ".json"

    with open(path, 'w', encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


def main():

    polling_places_xls = pd.ExcelFile(
        "polling_places.xlsx")
    as_df = polling_places_xls.parse(
        polling_places_xls.sheet_names[0])

    as_df = as_df.rename(columns={
        "Kód kraja": "region_code",
        "Názov kraja": "region_name",
        "Kód územného obvodu": "administrative_area_code",
        "Názov územného obvodu": "administrative_area_name",
        "Kód okresu": "county_code",
        "Názov okresu": "county_name",
        "Kód obce": "municipality_code",
        "Názov obce": "municipality_name",
        "Okrsok": "polling_place_number",
        "Počet zapísaných voličov": "registered_voters_count"
    })

    as_df = as_df[["region_code", "region_name", "administrative_area_code", "administrative_area_name", "county_code",
                   "county_name", "municipality_code", "municipality_name", "polling_place_number", "registered_voters_count"]]
    saveJson(as_df.fillna('').to_dict(orient="records"),
             "polling_places.json")

    candidates_xls = pd.ExcelFile("candidates.xlsx")
    df = candidates_xls.parse(candidates_xls.sheet_names[0])

    df = df.rename(columns={
        "Číslo politického subjektu": "party_number",
        "Názov politického subjektu": "name",
        "Poradie na hlasovacom lístku": "order",
        "Meno": "first_name",
        "Priezvisko": "last_name",
        "Titul": "degrees_before",
        "Vek": "age",
        "Zamestnanie": "occupation",
        "Obec trvalého pobytu": "residence",
        "Poznámka": "note"
    })

    df = df.drop(['note', 'name'], axis=1)

    print(df.head())
    print(df.info())

    saveJson(df.fillna('').to_dict(orient="records"),
             "candidates_transformed.json")

    parties_xls = pd.ExcelFile("parties.xlsx")
    df = parties_xls.parse(parties_xls.sheet_names[0])

    df = df.rename(columns={
        "Číslo politického subjektu": "party_number",
        "Názov politického subjektu": "name",
        "Oficiálna skratka politického subjektu": "abbreviation",
        "Poznámka": "note",
        "Počet kandidátov": "candidates_count"
    })

    df = df.drop(['candidates_count', 'note'], axis=1)

    print(df.head())
    print(df.info())

    saveJson(df.fillna('').to_dict(orient="records"),
             "parties_transformed.json")


if __name__ == '__main__':
    main()
