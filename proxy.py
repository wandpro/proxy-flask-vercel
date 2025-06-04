from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

app = Flask(__name__)

@app.route('/')
def proxy():
    target_url = request.args.get('url')

    if not target_url:
        return "Error: Missing 'url' parameter", 400

    try:
        resp = requests.get(target_url, headers={'User-Agent': request.headers.get('User-Agent', '')})
    except Exception as e:
        return f"Error fetching URL: {e}", 500

    content_type = resp.headers.get('Content-Type', '')

    # Si c'est HTML, on modifie les liens
    if 'text/html' in content_type:
        soup = BeautifulSoup(resp.text, 'html.parser')
        base_url = target_url

        for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe']):
            for attr in ['href', 'src']:
                if tag.has_attr(attr):
                    orig = tag[attr]
                    if orig.startswith('http') or orig.startswith('/'):
                        absolute = urljoin(base_url, orig)
                        tag[attr] = f"/?url={quote(absolute)}"

        # Traiter aussi les attributs data-*
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith('data-') and isinstance(tag[attr], str):
                    val = tag[attr]
                    if val.startswith('http') or val.startswith('/'):
                        absolute = urljoin(base_url, val)
                        tag[attr] = f"/?url={quote(absolute)}"

        return Response(str(soup), content_type='text/html')

    # Si c'est autre chose (images, CSS, JS...), on transmet brut
    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get('Content-Type')
    )

if __name__ == '__main__':
    app.run(debug=True)
