import os
import pathlib
from typing import List

import gradio as gr
import lancedb
import openai
import pandas as pd
from constants import VECTORDB_FILE_PATH
from lancedb.context import contextualize
from lancedb.embeddings import with_embeddings
from parse_files import parse_files
from vector_embedding import complete, create_prompt, embed_func

db = lancedb.connect("~/tmp/lancedbprj")

# table_name = "LING200"
table_name = "MATH437"


if table_name not in db.table_names():
    assert len(openai.Model.list()["data"]) > 0
    wd = os.getcwd()
    file_path = os.path.join(wd, VECTORDB_FILE_PATH, "MATH 437 101 2023W1")
    # print(wd)
    # it = os.listdir(os.path.join(wd, VECTORDB_FILE_PATH))
    paths = pathlib.Path(file_path)
    files = list(paths.rglob("*.pdf"))

    # print(files)
    print("start parsing")
    files_strings = []
    for f in files:
        files_strings.append(f.__str__())
    data = parse_files(files_strings)
    # print(len(data))
    df = (
        contextualize(pd.DataFrame({"text": data}))
        .text_col("text")
        .window(3)
        .stride(2)
        .to_pandas()
    )
    # print(df)
    # print(type(df))
    # print(len(df['text'][0]))
    data = with_embeddings(embed_func, df, show_progress=True)
    print(data.to_pandas().head(1))
    tbl = db.create_table(table_name, data)
    print(f"Created LaneDB table of length: {len(tbl)}")
else:
    tbl = db.open_table(table_name)


def query_text(query):
    emb = embed_func(query)[0]
    context = tbl.search(emb).limit(5).to_pandas()
    sources = "Context found: \n"
    count = 1
    for c in context["text"]:
        sources = sources + str(count) + ". " + c + "\n"
        count = count + 1
    prompt = create_prompt(query, context)
    # print(prompt)
    ans = "Answer: " + complete(prompt)
    return ans, sources


demo = gr.Interface(fn=query_text, inputs="text", outputs=["text", "text"])

demo.launch()
