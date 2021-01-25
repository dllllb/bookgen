# Markdown book generation

Usage: `pipenv run ./bookgen.py {path-to-book-source}`

All .md files in the selected directory will be in the single-file HTML book. Sorted order of file names defines the order of content in the book (use number prefixes for file names to define the desired order of content).

## Image support

![image](img/markdown.png)

## TeX foruma support

Equation:
$$ \sum_{i=1}^{\infty} x_i $$

Inline equation: $ e^x $

## Mermaid support

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```