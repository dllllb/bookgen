import os
import os.path
from pathlib import Path
import shutil
from glob import glob
import argparse

from nbconvert import MarkdownExporter
from traitlets.config import Config

from mermaid import MermaidExtension
from include import MarkdownInclude

from nbconvert.preprocessors import ClearOutputPreprocessor

import markdown

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

parser = argparse.ArgumentParser()
parser.add_argument('input', default='.')
parser.add_argument('-o', '--output')
args = parser.parse_args()

if args.output is None:
    out_path = f'{os.path.realpath(args.input)}_build'
else:
    out_path = os.path.realpath(args.output)

os.mkdir(out_path)
os.chdir(args.input)

md = ''

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
                print(os.curdir)
                with open(f'{out_path}/{cfn}', 'wb') as fw:
                    fw.write(body)
    else:
        raise AttributeError(f'unknown extension {fname.suffix}')


mdx =  '[TOC]\n'
mdx += md

body = markdown.markdown(
    md,
    extensions=[
        'fenced_code',
        'codehilite',
        'toc',
        MermaidExtension(),
        MarkdownInclude()],
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
