from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def proxy():
    base_url = request.args.get('url') or request.form.get('url')
    if not base_url or not base_url.startswith('http'):
        return "Invalid or missing URL parameter", 400

    try:
        resp = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
        content_type = resp.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Réécriture des liens dans <a>, <link>, <script>, <img>
            for tag in soup.find_all(['a', 'link', 'script', 'img']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    original = tag[attr]
                    absolute = urljoin(base_url, original)
                    tag[attr] = f"/?url={quote(absolute)}"

            # Gestion des images lazy-load (data-src)
            for img in soup.find_all('img'):
                if img.has_attr('data-src'):
                    absolute = urljoin(base_url, img['data-src'])
                    img['src'] = f"/?url={quote(absolute)}"

            # Réécriture des formulaires (ex: recherche)
            for form in soup.find_all('form'):
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                absolute = urljoin(base_url, action)

                if method == 'get':
                    form['action'] = '/'
                    hidden_input = soup.new_tag('input', attrs={'type': 'hidden', 'name': 'url', 'value': absolute})
                    form.insert(0, hidden_input)

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
