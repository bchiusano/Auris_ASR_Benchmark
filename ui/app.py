import gradio as gr
from normalizer.eval_utils import score_results
from constants import TITLE, INTRODUCTION_TEXT, AURIS_ORIGINAL_DESCRIPTION, METRICS_TEXT, WER, RTFX, GITHUB_REPO


_, _, all_df, composite_df = score_results("../results/")
#_, _, all_df, composite_df = score_results("../results/small/")

# TODO: User can see some examples of reference vs prediction

numeric_wer = []
numeric_rtfx = []

for wer in all_df['WER']:
    numeric_wer.append(float(wer.strip().replace('%', '')))
for rtxf in all_df['RTFX']:
    numeric_rtfx.append(float(rtxf.strip()))

with gr.Blocks() as demo:
    gr.HTML(TITLE)
    gr.Markdown(INTRODUCTION_TEXT)

    with gr.Tabs(elem_classes="tab-buttons") as tabs:

        with gr.TabItem("All Tests"):

            gr.Markdown("## Stats")
            with gr.Row():
                gr.Label(f"{min(numeric_wer)}%", label="Lowest WER")
                gr.Label(f"{max(numeric_rtfx)}", label="Highest RTFX")

            gr.Markdown("## Benchmark")
            gr.DataFrame(all_df)

            gr.Markdown("Filter Examples")
            with gr.Row():
                models = gr.Dropdown(composite_df['model'].tolist(), value="All", label="Models", allow_custom_value=True)

        with gr.TabItem("Composite Results"):
            gr.DataFrame(composite_df)

        with gr.TabItem("About the Project"):
            gr.Markdown(AURIS_ORIGINAL_DESCRIPTION)
            gr.Markdown(METRICS_TEXT)
            #with gr.Row():
            gr.Markdown(WER)
            gr.Markdown(RTFX)
            gr.Markdown(GITHUB_REPO)

            gr.Markdown("## Notes and Suggestions")

demo.launch()
