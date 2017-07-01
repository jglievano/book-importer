from urllib.request import urlopen
import html5lib
import lxml
import os
import re
import sys

SOURCE_URL = "http://www.69shu.com/"

def import_book(book_id):
    book_url = SOURCE_URL + str(book_id) + "/"
    parser = html5lib.HTMLParser(tree = html5lib.getTreeBuilder("lxml"),
                                 namespaceHTMLElements = False)
    print("Downloading %s." % (book_url))
    chapters = {}
    with urlopen(book_url) as response:
        doc = parser.parse(response)
        html = lxml.etree.tostring(doc.getroot())
        p_str = "<li><a href=\"/txt/%s/\\d+\">[0-9\.$&#;a-zA-Z \(\)~]+</a></li>" % (book_id)
        p = re.compile(p_str)
        chapters_html = p.findall(str(html))
        for c in chapters_html:
            url_re = re.compile("/txt/%s/\\d+" % (book_id))
            n_re = re.compile(">\d+\.")
            chapter_re = re.compile("\..+</a>")
            url = url_re.search(c).group()
            n = n_re.search(c).group()[1:-1]
            chapter = chapter_re.search(c).group()[1:-4]
            chapters[int(n)] = (chapter, url)

    output_path = "output/%s" % (book_id)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Gets chapters and cleans.
    for i in range(1, len(chapters) + 1):
        if i in chapters:
            url = "%s%s" % (SOURCE_URL, chapters[i][1][1:])
            with urlopen(url) as response:
                doc = parser.parse(response)
                root = doc.getroot()
                written = False
                for child in root[1].iter():
                    if child.get('class') == 'yd_text2':
                        html = str(lxml.etree.tostring(child))
                        html = re.sub(r'<br />', '<br />\n', html)
                        html = re.sub(r'<script.+/script>', '', html)
                        html = re.sub(r'<div.*>', '', html)
                        html = re.sub(r'</div>', '', html)
                        html = re.sub(r'<!--.+-->', '', html)
                        html = re.sub(r'\\n', '\n', html)
                        html = re.sub(r'^\n', '', html)
                        html = re.sub(r'^\W+\n', '', html)
                        html = re.sub(r'^\W+$', '', html)
                        with open("%s/%08d.html" % (output_path, i), "w") as out:
                            out.write("<h2>%s</h2>\n" % (chapters[i][0]))
                            out.write("<br />\n")
                            out.write(html[2:-1])
                            print("  Wrote chapter %d" % (i))
        else:
            print("  WARNING: Chapter %d missing" % (i))
    print("Wrote %d chapters." % (len(chapters)))
    print("Finished.")

def main():
    """
    Entry point.
    """
    if len(sys.argv) != 2:
        print("Usage: book-importer.py <book_id>")
        return
    import_book(sys.argv[1])

if __name__ == "__main__":
    main()

