"""Publish the existing website homepage verbatim, without an intermediate page."""
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SOURCE = 'https://coderzhh.github.io/DailyChange-Web/'
ROOT = 'https://coderzhh.github.io/'


def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'DailyChange-site-publisher/1.0'}), timeout=30) as response:
        if response.status != 200:
            raise ValueError(f'Cannot read {url}: {response.status}')
        return response.read()


class Homepage(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.canonicals, self.resources, self.schemas = [], set(), []
        self.parts, self.capture = [], False
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag in ('script', 'img') or tag == 'link' and a.get('rel') in ('stylesheet', 'icon'):
            ref = a.get('src') or a.get('href')
            if ref and ref.startswith('/DailyChange-Web/'):
                self.resources.add(urljoin(ROOT, ref))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.capture, self.parts = True, []

    def handle_data(self, text):
        if self.capture:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag == 'script' and self.capture:
            self.schemas.append(json.loads(''.join(self.parts)))
            self.capture = False


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    html = get(SOURCE)
    page = Homepage(html.decode('utf-8'))
    assert page.canonicals == [ROOT], 'Publish the source website with the root canonical URL first'
    assert b'id="hero-title"' in html, 'Expected the complete existing homepage'
    graphs = [node for block in page.schemas for node in block.get('@graph', [block])]
    assert any(node.get('@type') == 'WebSite' and node.get('name') == 'DailyChange' and node.get('url') == ROOT for node in graphs)
    for url in sorted(page.resources):
        get(url)
    # Exact bytes: the existing design, writing, interactions and links are preserved.
    (out / 'index.html').write_bytes(html)
    for file in ['favicon.png', 'sitemap.xml', 'robots.txt', 'google7cbc3f23d772c830.html', 'BingSiteAuth.xml']:
        (out / file).write_bytes(get(urljoin(SOURCE, file)))
    assert struct.unpack('>II', (out / 'favicon.png').read_bytes()[16:24]) == (96, 96)
    urls = [node.text for node in ET.parse(out / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(urls) == 14 and ROOT in urls and all(urlparse(url).hostname == 'coderzhh.github.io' for url in urls)
    assert f'Sitemap: {ROOT}sitemap.xml' in (out / 'robots.txt').read_text()
    (out / '.nojekyll').touch()
    print(f'Packaged the existing homepage unchanged; verified {len(page.resources)} resources and {len(urls)} canonical URLs.')


if __name__ == '__main__':
    main()
