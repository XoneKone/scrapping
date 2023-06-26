from parse.parser import get_data_from_db
from operator import itemgetter
import pandas as pd

if __name__ == '__main__':
    data = get_data_from_db("topics.sqlite")
    df = pd.DataFrame([list(itemgetter(1, 2, 5, 6, 7, 3, 4)(i)) for i in data],
                      columns=['author', 'title', 'url', 'year', 'theme', 'annotation', 'content'])
    html = df.to_html()
    with open("index.html", 'w', encoding="UTF-16") as writer:
        writer.write(html)
