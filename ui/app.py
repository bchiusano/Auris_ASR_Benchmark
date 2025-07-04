import gradio as gr
from normalizer.eval_utils import score_results

'''
def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)


demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)
'''

_, _, all_df, composite_df = score_results("../results/")
with gr.Blocks() as demo:
    gr.Markdown("# ASR benchmark for Child Speech")
    gr.DataFrame(all_df)
demo.launch()

# Table
# Filtering
# Explanation
# Notes - people can leave messages (?)
