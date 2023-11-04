import os
from typing import List

import lancedb
import openai
import pandas as pd
from constants import VECTORDB_FILE_PATH
from lancedb.context import contextualize
from lancedb.embeddings import with_embeddings
from parse_files import parse_files

OPENAI_MODEL = "text-embedding-ada-002"

db = lancedb.connect("~/tmp/lancedbprj")


def embed_func(c):
    rs = openai.Embedding.create(input=c, engine=OPENAI_MODEL)
    return [record["embedding"] for record in rs["data"]]


def create_prompt(query, context):
    limit = 3750

    prompt_start = "Answer the question based on the context below:"
    prompt_end = f"Question: {query}\nAnswer:"
    # append contexts until hitting limit
    for i in range(1, len(context)):
        if len("\n\n---\n\n".join(context.text[:i])) >= limit:
            context_formatted = "\n\n---\n\n".join(context.text[: i - 1])
            break
        elif i == len(context) - 1:
            context_formatted = "\n\n---\n\n".join(context.text)
    prompt = [
        {
            "role": "system",
            "content": "You are an assistant, helping answer questions based on given context.",
        },
        {"role": "user", "content": prompt_start},
        {
            "role": "user",
            "content": "Context:\n"
            # + "We are talking about SQL Injection.\n\n---\n\n"
            + context_formatted,
        },
        {"role": "user", "content": prompt_end},
    ]
    return prompt


def complete(prompt):
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0,
        max_tokens=3000,
    )
    return res["choices"][0]["message"]["content"]


db = lancedb.connect("~/tmp/lancedbprj")

table_name = "CanvasPapers"

if table_name not in db.table_names():
    assert len(openai.Model.list()["data"]) > 0
    wd = os.getcwd()
    # print(wd)
    it = os.listdir(os.path.join(wd, VECTORDB_FILE_PATH))
    files = []
    for i in it:
        files.append(os.path.join(wd, VECTORDB_FILE_PATH, i))
    # print(files)
    data = parse_files(files)
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
    context = tbl.search(emb).limit(3).to_df()
    # print(context)
    prompt = create_prompt(query, context)
    # print(prompt)
    ans = complete(prompt)
    return ans
