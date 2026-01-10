import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import sys

def es_mismo_dominio(url_base, url_destino):
    """Comprueba si ambas URLs pertenecen al mismo dominio."""
    return urlparse(url_base).netloc == urlparse(url_destino).netloc

def extraer_links(url):
    """Descarga la página y extrae todos los enlaces <a href="">."""
    
    EXTENSIONES_IGNORADAS = (".mp4", ".avi", ".mov", ".mp3",".pdf", ".zip", ".rar", ".7z",".exe", ".iso", ".jpg", ".png", ".gif")
    if url.lower().endswith(EXTENSIONES_IGNORADAS):
        return []
    try:
        res = requests.get(url, timeout=5, allow_redirects=True)
        res.raise_for_status()
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        enlace = urljoin(url, a["href"])  # convierte enlaces relativos en absolutos
        links.add(enlace)

    return links

def crawler(inicio):
    visitados = set()
    cola = deque([inicio])

    while cola:
        url = cola.popleft()

        if url in visitados:
            continue

        print(f"Visitando: {url}")
        visitados.add(url)

        for link in extraer_links(url):
            if es_mismo_dominio(inicio, link) and link not in visitados:
                cola.append(link)

    return sorted(visitados)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python crawler.py <url_inicial>")
        sys.exit(1)

    url_inicial = sys.argv[1]
    urls = crawler(url_inicial)

    print(f"\n=== URLs encontradas: "+str(len(urls))+" ===")
    for u in urls:
        print(u)
