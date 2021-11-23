import pandas as pd
import json

def saveJson(obj, path):
    if(".json" not in path):
        path += ".json"

    with open(path, 'w', encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

def main():

    candidates_xls = pd.ExcelFile("candidates.xlsx")
    df = candidates_xls.parse(candidates_xls.sheet_names[0])

    df = df.rename(columns={
        "Číslo politického subjektu": "party_number", 
        "Názov politického subjektu": "name",
        "Poradie na hlasovacom lístku" : "order",
        "Meno" : "first_name",
        "Priezvisko" : "last_name",
        "Titul" : "degrees_before",
        "Vek" : "age",
        "Zamestnanie" : "occupation",
        "Obec trvalého pobytu" : "residence",
        "Poznámka" : "note"
    })

    df = df.drop(['note', 'name'], axis=1)

    print(df.head())
    print(df.info())


    
    saveJson(df.fillna('').to_dict(orient="records"), "candidates_transformed.json")

    parties_xls = pd.ExcelFile("parties.xlsx")
    df = parties_xls.parse(parties_xls.sheet_names[0])

    df = df.rename(columns={
        "Číslo politického subjektu": "party_number", 
        "Názov politického subjektu": "name",
        "Oficiálna skratka politického subjektu" : "abbreviation",
        "Poznámka" : "note",
        "Počet kandidátov" : "candidates_count"
    })

    df["image"] = "don_roberto_logo.jpg"

    df = df.drop(['candidates_count', 'note'], axis=1)

    print(df.head())
    print(df.info())

    saveJson(df.fillna('').to_dict(orient="records"), "parties_transformed.json")

if __name__ == '__main__':
    main()