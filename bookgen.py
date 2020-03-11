#!/usr/bin/env python

# Usage: ./make.py {path-to-book-source}
# all .md files in the selected directory will be in the single-file HTML book
# sorted order of file names defines the order of content in the book
# use number prefixes for file names to define the desired order of content

import sys
import os
import os.path
from pathlib import Path
import shutil
from glob import glob
import markdown

from nbconvert import MarkdownExporter
from traitlets.config import Config

from mermaid import MermaidExtension

from nbconvert.preprocessors import ClearOutputPreprocessor

class HideSourcePreprocessor(ClearOutputPreprocessor):
    def preprocess(self, nb, resources):
        for cell in nb.cells:
            if cell.cell_type == 'code':
                if cell.get('metadata', {}).get('jupyter', {}).get('source_hidden', False):
                    cell.transient = {
                        'remove_source': True
                    }

        return nb, resources

script_dir = os.path.dirname(os.path.realpath(__file__))

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = '.'

out_path = f'{os.path.realpath(path)}_build'

os.mkdir(out_path)
os.chdir(path)

md = "[TOC]\n\n"

fnames = [fname for fname in Path('.').glob('**/*.md')]
fnames += [fname for fname in Path('.').glob('**/*.ipynb')]
fnames = sorted(fnames)

for fname in fnames:
    if fname.suffix == '.md':
        with open(fname, encoding='utf-8') as f:
            md += f.read()
    elif fname.suffix == '.ipynb':
        c = Config()

        bname = os.path.basename(fname)
        content_fnt = bname+'_{unique_key}_{cell_index}_{index}{extension}'
        c.ExtractOutputPreprocessor.output_filename_template = content_fnt

        c.MarkdownExporter.preprocessors = [HideSourcePreprocessor]

        me = MarkdownExporter(config=c)

        with open(fname, 'r') as f:
            text, res = me.from_file(f)
            md += text
            for cfn, body in res['outputs'].items():
                with open(f'{out_path}/{cfn}', 'wb') as f:
                    f.write(body)
    else:
        raise Excepton(f'unknown extension {fname.suffix}')

body = markdown.markdown(
    md,
    extensions=['fenced_code', 'codehilite', 'toc', MermaidExtension()],
    encoding='utf-8',
    tab_length=2)

with open(os.path.join(script_dir, 'template.html')) as f:
    template = f.read()

html = template + body

with open(f'{out_path}/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

resources = [
    'mdenc.css',
    'pygments.css',
    'mermaid.min.8.3.1.js',
    'katex.min.0.11.1.js',
    'katex.auto-render.min.0.11.1.js',
    'katex.min.0.11.1.css'
]

for fname in resources:
    shutil.copyfile(f'{script_dir}/{fname}', f'{out_path}/{fname}')

for ext in ['png', 'jpg', 'jpeg']:
    for fname in Path('.').glob(f'**/*.{ext}'):
        target_dir = f'{out_path}/{os.path.dirname(fname)}'
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        shutil.copyfile(fname, f'{out_path}/{fname}')
