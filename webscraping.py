from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
import re

# Base do site
BASE_URL = "https://panelinha.com.br"
SEARCH_URL = "https://panelinha.com.br/busca?query=&page={}&menu%5Bpage_type%5D=Receitas"

# Inicializa o Selenium com WebDriver Manager
def init_driver():
    options = Options()
    options.add_argument("--headless")       # roda sem abrir janela
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Coleta links de receitas de todas as páginas da busca
def get_recipe_links(driver):
    links = []
    page = 1
    while page <= 235:  # Vi que as receitas vão até a página 233, então deixei esse limite aí, só por precaução, mas poderia ser while True
        url = SEARCH_URL.format(page)
        print(f"Acessando página {page}: {url}")
        driver.get(url)
        time.sleep(3)  # espera o JS carregar

        soup = BeautifulSoup(driver.page_source, "html.parser")
        container = soup.select_one(".hitsContainer2C .ais-Hits ol")
        if not container:
            print(f"Nenhum resultado encontrado na página {page}, parada.")
            break

        for a in container.select("li a[href]"):
            recipe_url = urljoin(BASE_URL, a["href"])
            # Filtra apenas URLs que começam com /receita/
            if re.match(r"^https://panelinha\.com\.br/receita/.+", recipe_url):
                if recipe_url not in links:
                    links.append(recipe_url)

        page += 1  # passa para a próxima página

    return links

# Raspa uma receita individual
def scrape_recipe(driver, url):
    print(f"Coletando receita: {url}")
    driver.get(url)
    time.sleep(2)  # espera a página carregar

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Título
    titulo = soup.find("h1").get_text(strip=True).lower() if soup.find("h1") else ""

    # Ingredientes
    ingredientes = []
    h5_ing = soup.find("h5", string=lambda x: x and "Ingredientes" in x)
    if h5_ing:
        ul = h5_ing.find_next_sibling("ul")
        if ul:
            ingredientes = [li.get_text(strip=True).lower() for li in ul.find_all("li")]

    # Modo de preparo
    preparo = []
    h5_prep = soup.find("h5", string=lambda x: x and "Modo de preparo" in x)
    if h5_prep:
        ol = h5_prep.find_next_sibling("ol")
        if ol:
            preparo = [li.get_text(strip=True).lower() for li in ol.find_all("li")]

    return {
        "url": url.lower(),
        "titulo": titulo,
        "ingredientes": ingredientes,
        "preparo": preparo
    }

if __name__ == "__main__":
    driver = init_driver()

    try:
        # Coleta links de todas as receitas
        receitas_links = get_recipe_links(driver)
        print("Total de receitas encontradas:", len(receitas_links))

        # Coleta os dados de cada receita
        corpus = []
        for link in receitas_links:
            dados = scrape_recipe(driver, link)
            if dados:
                corpus.append(dados)

        # Salva no arquivo corpus.txt, um JSON por linha
        with open("corpus.txt", "w", encoding="utf-8") as f:
            for item in corpus:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print("✅ Coleta concluída! O corpus foi salvo em corpus.txt")
    finally:
        driver.quit()
