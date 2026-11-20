"""Download, refresh and search official AWS documentation with a local change ledger."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import difflib
import fcntl
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(text)
    temporary.replace(path)


def save_json(path, value):
    atomic_write(path, json.dumps(value, indent=2) + '\n')


def validate_source(item):
    if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in ('url', 'product')):
        raise ValueError('Source must be an object with string url and product fields')
    parsed = urlsplit(item['url'])
    if parsed.scheme != 'https' or parsed.netloc != 'docs.aws.amazon.com' or not parsed.path.endswith(('.html', '.md')):
        raise ValueError('Source must be an official docs.aws.amazon.com article URL')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', item['product']):
        raise ValueError('Invalid product label')
    if not isinstance(item.get('topics'), list) or not all(isinstance(t, str) for t in item['topics']):
        raise ValueError('Topics must be a list of strings')
    return dict(item)


class ArticleParser(HTMLParser):
    """Small HTML tree used only for AWS's article container."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ['root', {}, []]
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        node = [tag, dict(attrs), []]
        self.stack[-1][2].append(node)
        if tag not in {'meta', 'link', 'br', 'img', 'hr', 'input', 'source', 'wbr'}:
            self.stack.append(node)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        self.stack[-1][2].append(data)


def nodes(node):
    if isinstance(node, list):
        yield node
        for child in node[2]:
            yield from nodes(child)


def plain(node):
    return node if isinstance(node, str) else ''.join(plain(c) for c in node[2])


def markdown(node, url, pre=False):
    if isinstance(node, str):
        return node if pre else re.sub(r'\s+', ' ', node)
    tag, attrs, children = node
    if tag in {'script', 'style', 'nav', 'noscript', 'footer'}:
        return ''
    if tag == 'pre':
        content = plain(node).strip('\n')
        fence = '`' * max(3, max((len(m) + 1 for m in re.findall(r'`+', content)), default=3))
        return f'\n\n{fence}\n{content}\n{fence}\n\n'
    body = ''.join(markdown(c, url, pre) for c in children)
    if re.fullmatch('h[1-6]', tag):
        anchor = f'<a id="{attrs["id"]}"></a>\n' if attrs.get('id') else ''
        return '\n\n'+anchor+'#'*int(tag[1])+' '+body.strip()+'\n\n'
    if tag == 'a' and attrs.get('href'):
        return f'[{body}]({urljoin(url, attrs["href"])})'
    if tag == 'code':
        return '`'+body+'`'
    if tag in {'strong', 'b'}:
        return '**'+body+'**'
    if tag == 'li':
        return '\n- '+body.strip()+'\n'
    if tag in {'p', 'div', 'section', 'ul', 'ol', 'blockquote'}:
        return '\n\n'+body.strip()+'\n\n'
    if tag == 'br':
        return '\n'
    if tag == 'table':
        rows = [n for n in nodes(node) if n[0] == 'tr']
        values = [[markdown(c, url).strip().replace('\n', '<br>').replace('|', '\\|')
                   for c in row[2] if isinstance(c, list) and c[0] in {'td', 'th'}] for row in rows]
        if not values:
            return ''
        width = max(map(len, values))
        lines = ['| '+' | '.join(row+['']*(width-len(row)))+' |' for row in values]
        lines.insert(1, '| '+' | '.join(['---']*width)+' |')
        return '\n\n'+'\n'.join(lines)+'\n\n'
    return body


def extract(html, url):
    tree = ArticleParser()
    tree.feed(html)
    all_nodes = list(nodes(tree.root))
    article = next((n for key in ('main-col-body', 'main-content') for n in all_nodes if n[1].get('id') == key), None)
    if article is None:
        raise ValueError('AWS article container missing; rejected landing/error page')
    title = next((plain(n).strip() for n in nodes(article) if n[0] == 'h1'), '')
    body = markdown(article, url).strip()+'\n'
    if not title or len(body) < 100:
        raise ValueError('Article is empty or too short')
    date = next((n[1].get('content') for n in all_nodes if n[0] == 'meta' and n[1].get('name') in {'date', 'last_updated', 'last-modified'}), None)
    return {'title': title, 'body': body, 'source_modified': date, 'representation': 'html-converted', 'partial': False}


def fetch(item):
    try:
        validate_source(item)
        url = item['url']
        candidates = [url[:-5]+'.md', url] if url.endswith('.html') else [url]
        error = ''
        for target in candidates:
            proc = subprocess.run(['curl', '-fsSL', '--proto', '=https', '--proto-redir', '=https', '--retry', '1',
                                   '--max-time', '45', '--write-out', '\n%{url_effective}', target], capture_output=True, text=True)
            if proc.returncode:
                error = proc.stderr.strip()
                continue
            try:
                content, final = proc.stdout.rsplit('\n', 1)
                if final != target and final != url:
                    raise ValueError(f'Unexpected redirect to {final}')
                if '<html' in content[:1000].lower() or '<!doctype' in content[:1000].lower():
                    article = extract(content, url)
                else:
                    title = re.search(r'^# (.+)$', content, re.M)
                    if not title or len(content.strip()) < 100:
                        raise ValueError('Response is not a substantial Markdown article')
                    article = {'title': title.group(1).strip(), 'body': content.strip()+'\n', 'source_modified': None, 'representation': 'native-markdown', 'partial': False}
                return {**item, **article, 'download_url': final}
            except ValueError as exc:
                error = str(exc)
                continue
        raise ValueError(error or 'Download failed')
    except (ValueError, OSError, KeyError) as exc:
        return {**item, 'error': str(exc)}


@contextmanager
def lock(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root/'.refresh.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('Another refresh is running') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def sections(text):
    result, heading, lines, fence = [], 'Introduction', [], False
    for line in text.splitlines():
        if not fence and re.fullmatch(r'<a id="[^"]+"></a>', line):
            continue
        if line.startswith('```'):
            fence = not fence
        if not fence and re.match(r'^#{1,6} ', line):
            if lines and '\n'.join(lines).strip():
                result.append((heading, '\n'.join(lines).strip()))
            heading, lines = line.lstrip('# ').strip(), []
        else:
            lines.append(line)
    if lines:
        result.append((heading, '\n'.join(lines).strip()))
    return result


def merge_result(root, item, old, stamp):
    previous = old.get(item['url'])
    if 'error' in item:
        return ({**previous, 'status': 'stale', 'last_checked': stamp, 'last_refresh_error': item['error']} if previous else None), 'failed'
    body = item['body']
    digest = hashlib.sha256(body.encode()).hexdigest()
    relative = 'current/'+item['product']+'/'+urlsplit(item['url']).path.strip('/').replace('/', '__').rsplit('.', 1)[0]+'.md'
    target = root/relative
    before = target.read_text() if target.exists() else None
    outcome = 'added' if before is None else 'unchanged' if before == body else 'changed'
    if before is not None and previous and previous.get('representation') != item.get('representation'):
        outcome = 'representation-changed'
    if outcome in {'changed', 'representation-changed'}:
        backup = root/'backups'/stamp.replace(':', '-')/relative
        atomic_write(backup, before)
        atomic_write(backup.with_suffix('.md.diff'), ''.join(difflib.unified_diff(before.splitlines(True), body.splitlines(True), fromfile='previous', tofile='current')))
    if outcome != 'unchanged':
        atomic_write(target, body)
    metadata = {k: v for k, v in item.items() if k != 'body'}
    return {**metadata, 'path': relative, 'sha256': digest, 'status': 'current', 'last_checked': stamp,
            'retrieved_at': stamp, 'first_observed': previous.get('first_observed', stamp) if previous else stamp}, outcome


def refresh(root=ROOT, workers=4):
    with lock(root):
        seeds = [validate_source(s) for s in read_json(root/'sources.json', [])]
        if not seeds or len({s['url'] for s in seeds}) != len(seeds):
            raise ValueError('sources.json must contain a nonempty list of unique sources')
        stamp = now()
        old = {x['url']: x for x in read_json(root/'manifest.json', [])}
        with ThreadPoolExecutor(max_workers=max(1, min(workers, 4))) as pool:
            results = list(pool.map(fetch, seeds))
        entries, changes = dict(old), []
        for item in results:
            entry, outcome = merge_result(root, item, old, stamp)
            if entry:
                entries[item['url']] = entry
            changes.append({'url': item['url'], 'outcome': outcome, **({'error': item['error']} if 'error' in item else {})})
        report = {'checked_at': stamp, 'counts': {key: sum(c['outcome'] == key for c in changes) for key in ('added', 'changed', 'representation-changed', 'unchanged', 'failed')}, 'sources': changes}
        save_json(root/'manifest.json', list(entries.values()))
        save_json(root/'download-gaps.json', [c for c in changes if c['outcome'] == 'failed'])
        save_json(root/'refresh-report.json', report)
        save_json(root/'reports'/('refresh-'+stamp.replace(':', '-')+'.json'), report)
        lines = ['# Refresh report', '', 'Checked at (UTC): '+stamp, '', json.dumps(report['counts']), '',
                 'Added means first downloaded here, not newly released. Changed means article content changed; inspect the saved diff.',
                 'Representation-changed means the acquisition format changed (for example web excerpt to native Markdown); it does not establish an upstream update.',
                 'Retrieval dates are not publication dates. Failed sources retain their last successful copy, marked stale.', '']
        lines.extend('- '+c['outcome']+': '+c['url']+(' — '+c['error'] if 'error' in c else '') for c in changes)
        atomic_write(root/'REFRESH-REPORT.md', '\n'.join(lines)+'\n')
        reindex(root)
        print(json.dumps(report['counts']))
        return int(report['counts']['failed'] > 0)


def reindex(root=ROOT):
    articles = read_json(root/'manifest.json', [])
    temporary = root/'search.next.sqlite'
    temporary.unlink(missing_ok=True)
    with closing(sqlite3.connect(temporary)) as db, db:
        db.execute('CREATE VIRTUAL TABLE passages USING fts5(title, heading, body, product UNINDEXED, topics UNINDEXED, path UNINDEXED, url UNINDEXED, status UNINDEXED)')
        for item in articles:
            text = (root/item['path']).read_text()
            anchors = {heading.strip(): anchor for anchor, heading in re.findall(r'<a id="([^"]+)"></a>\s*\n#{1,6} ([^\n]+)', text)}
            for heading, body in sections(text):
                source = item['url'] + ('#'+anchors[heading] if heading in anchors else '')
                db.execute('INSERT INTO passages VALUES (?,?,?,?,?,?,?,?)', (item['title'], heading, body, item['product'], ','.join(item['topics']), item['path'], source, item['status']))
    temporary.replace(root/'search.sqlite')
    lines = ['# AWS AgentCore documentation library', '', f'{len(articles)} locally available articles.', '',
             '[Refresh report](REFRESH-REPORT.md) · [Source registry](sources.json) · [Download gaps](download-gaps.json)', '',
             '```sh', 'python3 documentation/tools/library.py search "runtime"', 'python3 documentation/tools/library.py refresh', '```', '',
             'Search combines words with AND. Optional filters: --product, --topic, --limit. Refresh downloads up to four sources in parallel.', '',
             'Retrieval time does not establish release date. Inspect source history and saved content diffs before treating a change as a release.', '']
    for product in sorted({x['product'] for x in articles}):
        lines.extend(['## '+product, ''])
        lines.extend(f"- [{x['title']}]({x['path']}) — {', '.join(x['topics'])}; {x['status']}" for x in articles if x['product'] == product)
        lines.append('')
    atomic_write(root/'INDEX.md', '\n'.join(lines)+'\n')


def search(root, value, product=None, topic=None, limit=8):
    if not value.strip():
        raise ValueError('Enter one or more search words')
    if not (root/'search.sqlite').exists():
        raise ValueError('No search index; run refresh or reindex first')
    query = ' AND '.join('"'+word.replace('"', '""')+'"' for word in value.split())
    sql = "SELECT title,heading,snippet(passages,2,'[',']',' … ',35),path,url,status FROM passages WHERE passages MATCH ?"
    params = [query]
    for field, value in [('product', product), ('topics', topic)]:
        if value:
            sql += ' AND '+field+(' = ?' if field == 'product' else ' LIKE ?')
            params.append(value if field == 'product' else '%'+value+'%')
    sql += " ORDER BY (status = 'current') DESC,bm25(passages) LIMIT ?"
    params.append(max(1, min(limit, 100)))
    with closing(sqlite3.connect(root/'search.sqlite')) as db:
        return db.execute(sql, params).fetchall()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['refresh', 'reindex', 'search'])
    parser.add_argument('query', nargs='?', default='')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--product')
    parser.add_argument('--topic')
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(argv)
    try:
        if args.command == 'refresh':
            return refresh(args.root, args.workers)
        if args.command == 'reindex':
            with lock(args.root):
                reindex(args.root)
        else:
            for title, heading, excerpt, path, url, status in search(args.root, args.query, args.product, args.topic, args.limit):
                print(f'[{status}] {title} > {heading}\n{args.root/path}\n{url}\n{excerpt}\n')
        return 0
    except (ValueError, OSError, RuntimeError, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
