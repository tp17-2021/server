from src.server.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_app():
    response = client.get("/")
    assert response.status_code == 200


# NOTES
# TODO k testovaniu
# pripojit sa k test databaze ...
# spustanie vsetkzch testov pomocou pytest automaticky
# fixnut cestu src main (chceme testy dat do server priecinku server/tests/...) -> potom v dockerfile zrusit kopirovanie

# Návrhy na testy
# 1. dá sa poslať vote? dojde spravna response a status? 
# 2. ulozil sa poslanay vote?
# 3. poslat par votov a overit vysledok volieb
# 4. existuje configuracny a obsahuje candidatov partiesa a texty?
# 

# -s for verbose
# --verbose for deatil about each test
# pytest testing.py --verbose -s