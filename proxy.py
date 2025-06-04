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
            for tag in soup.find_all(['a', 'link', 'script', 'img']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    original = tag[attr]
                    absolute = urljoin(base_url, original)
                    if tag.name == 'a':
                        tag[attr] = f"/?url={quote(absolute)}"
                    else:
                        tag[attr] = absolute
            return str(soup)
        else:
            return Response(resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500

if __name__ == '__main__':
    app.run()
