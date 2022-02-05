import requests
import os

openapi_endpoint = "http://localhost:8222/openapi.json"
generation_command = "widdershins openapi.json -e settings.json -o api_docs.md"

res = requests.get(openapi_endpoint)

if(res.status_code == 200):
    open("openapi.json", "wb").write(res.content)
    try:

        # fire command resposible for generating markdown from swagger json
        os.system(generation_command)

        # get original README file
        main_md = open("../README.md", "r+", encoding="utf-8")
        main_md_lines = main_md.readlines()

        # get generated markdown file
        api_docs_md = open("api_docs.md", "r+", encoding="utf-8")
        api_docs_lines = api_docs_md.readlines()

        # remove lines that were generated and inserted into original README (after specific title)
        title_of_section = "## API endpoints"
        index_of_title_line = [i for i, line in enumerate(main_md_lines) if title_of_section in line]

        if(len(index_of_title_line)):

            index_of_title_line = index_of_title_line[0]
            
            # preserve only lines before this title (split by index), do not preserve the title line (exlusive)
            main_md_lines = main_md_lines[:index_of_title_line]

        # tmp = "For detailed information about endpoint request and response schemas please see the Swagger Docs at  ```http://localhost:8222/docs``` after building the containers"
        api_docs_lines = [f"{title_of_section}\n"] + api_docs_lines
        # print(api_docs_lines)

        joined_md_lines = main_md_lines + api_docs_lines
        open("new_README.md", "w").writelines(joined_md_lines)

    except Exception as e:
        print(e)
else:
    print(f"Endpoint not reachable")
