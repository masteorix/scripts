import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import os
import sys

# Extensiones que consideramos ARCHIVOS y NO queremos mostrar
EXTENSIONES_ARCHIVO = (
    ".css",".js",".map",".woff",".woff2",".ttf",".eot",".mp4",".mov",".avi"
)

def es_mismo_dominio(base, destino):
    return urlparse(base).netloc == urlparse(destino).netloc

def obtener_carpeta(url):
    """Si es archivo → devolver carpeta. Si es carpeta → devolver igual."""
    ruta = urlparse(url).path
    
    # Si termina con extensión → eliminar archivo
    if ruta.lower().endswith(EXTENSIONES_ARCHIVO):
        carpeta = os.path.dirname(ruta)
        if not carpeta.endswith("/"):
            carpeta += "/"
        return carpeta
    
    # Si ya es carpeta
    if ruta.endswith("/"):
        return ruta
    
    # Si es un archivo PHP, queremos mantenerlo (login.php)
    if ruta.lower().endswith(".php"):
        return url

    # Para URLs tipo ?page=user
    return ruta

def extraer_links(url):

    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    links = set()

    # Extraemos href y src de forma global
    atributos = [
        ("a", "href"),
        ("link", "href"),
        ("img", "src"),
        ("script", "src"),
        ("iframe", "src"),
        ("form", "action")
    ]

    for tag, attr in atributos:
        for elemento in soup.find_all(tag):
            if elemento.has_attr(attr):
                enlace = urljoin(url, elemento[attr])
                links.add(enlace)

    return links


def crawler(inicio):
    visitados = set()
    carpetas_finales = set()
    cola = deque([inicio])

    while cola:
        url = cola.popleft()
        if url in visitados:
            continue

        print(f"Visitando: {url}")
        visitados.add(url)

        # Añadir carpeta procesada del URL actual
        carpeta = obtener_carpeta(url)
        carpetas_finales.add(carpeta)

        for link in extraer_links(url):
            if es_mismo_dominio(inicio, link) and link not in visitados:
                cola.append(link)

    return sorted(carpetas_finales)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python crawler.py <url_inicial>")
        sys.exit(1)

    url_inicial = sys.argv[1]
    rutas = crawler(url_inicial)

    print("\n=== Rutas importantes encontradas ===")
    for r in rutas:
        print(r)
