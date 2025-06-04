from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

app = Flask(__name__)

@app.route('/')
def proxy():
    base_url = request.args.get('url')
    if not base_url or not base_url.startswith('http'):
        return "Invalid or missing URL parameter", 400

    try:
        resp = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = resp.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Réécriture des liens internes
            for tag in soup.find_all(['a', 'link', 'script', 'img']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    original = tag[attr]
                    absolute = urljoin(base_url, original)
                    tag[attr] = f"/?url={quote(absolute)}"

            # Réécriture des formulaires (ex: recherche SteamUnlocked)
            for form in soup.find_all('form'):
                if form.has_attr('action'):
                    original = form['action']
                    absolute = urljoin(base_url, original)
                    form['action'] = f"/?url={quote(absolute)}"
                form['method'] = 'GET'  # pour forcer GET même si c'est POST

            return str(soup)

        else:
            return Response(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get('Content-Type')
            )

    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500

if __name__ == '__main__':
    app.run()
