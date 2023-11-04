import os
from typing import List

import lancedb
import openai

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
