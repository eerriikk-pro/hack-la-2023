import gradio as gr
from vector_embedding import query_text

demo = gr.Interface(fn=query_text, inputs="text", outputs="text")

demo.launch()
