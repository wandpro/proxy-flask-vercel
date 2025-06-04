from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

app = Flask(__name__)

@app.route('/')
def proxy():
    target_url = request.args.get('url')

    if not target_url:
        return "<h2>Proxy actif. Ajoutez ?url=https://exemple.com</h2>", 200

    try:
        resp = requests.get(target_url, headers={'User-Agent': request.headers.get('User-Agent', '')}, timeout=10)
    except Exception as e:
        return f"Erreur de récupération : {e}", 500

    content_type = resp.headers.get('Content-Type', '')

    if 'text/html' in content_type:
        soup = BeautifulSoup(resp.text, 'html.parser')
        base_url = target_url

        # Injecter une balise <base> pour maintenir le contexte
        if not soup.find('base') and soup.head:
            base_tag = soup.new_tag('base', attrs={'href': f"/?url={quote(base_url)}"})
            soup.head.insert(0, base_tag)

        # Réécrire tous les liens
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe', 'source']):
            for attr in ['href', 'src', 'data-src', 'data-lazy-src', 'srcset']:
                if tag.has_attr(attr):
                    val = tag[attr]
                    if isinstance(val, str) and (val.startswith('/') or val.startswith('http')):
                        absolute = urljoin(base_url, val)
                        tag[attr] = f"/?url={quote(absolute)}"

        # Réécriture des attributs data-* personnalisés
        for tag in soup.find_all():
            for attr in list(tag.attrs):
                if attr.startswith('data-'):
                    val = tag.get(attr)
                    if isinstance(val, str) and (val.startswith('/') or val.startswith('http')):
                        absolute = urljoin(base_url, val)
                        tag[attr] = f"/?url={quote(absolute)}"

        return Response(str(soup), content_type='text/html')

    # Sinon (image, CSS, JS, etc.), ajouter les headers CORS
    headers = {
        "Content-Type": resp.headers.get("Content-Type", ""),
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET"
    }

    return Response(resp.content, status=resp.status_code, headers=headers)

if __name__ == '__main__':
    app.run(debug=True)
