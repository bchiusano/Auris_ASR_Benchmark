import gradio as gr
import pandas as pd

from normalizer.eval_utils import score_results
from ui.constants import TITLE, INTRODUCTION_TEXT, AURIS_ORIGINAL_DESCRIPTION, METRICS_TEXT, WER, RTFX, GITHUB_REPO


_, _, all_df, composite_df = score_results("results/auris/")
# Save these results to a json or csv file if needed
# _, _, all_df, composite_df = score_results("../results/small/")

numeric_wer = []
numeric_rtfx = []

unique_dataset = list(set(all_df['dataset']))

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

        with gr.TabItem("Composite Results"):
            gr.Markdown("## Average per Model")
            gr.DataFrame(composite_df)
            # TODO: add a bar chart
            # TODO: make sure that results are being displayed directly with the lowest WER at the top

        with gr.TabItem("Filter Examples"):
            gr.Markdown("## Filter Examples")

            with gr.Row():
                all_models = composite_df['model'].tolist()
                models = gr.Dropdown(all_models, value=all_models[0], label="Models", allow_custom_value=True,
                                     interactive=True)
                data = gr.Dropdown(unique_dataset, value=unique_dataset[0], label="Dataset", allow_custom_value=True,
                                   interactive=True)

            examples_df = gr.DataFrame(headers=['Original', 'Predicted'])


            @gr.on(inputs=[models, data], outputs=examples_df)
            def filtered_data(models, data):
                j_file = f"../results/MODEL_{models.replace('/', '-')}_DATASET_{data}.jsonl"
                try:
                    j_df = pd.read_json(j_file, lines=True)
                    return pd.DataFrame({"Original": j_df['text'], "Predicted": j_df['pred_text']})
                except:
                    return pd.DataFrame({"Original": ['work in progress'], "Predicted": ['work in progress']})

        with gr.TabItem("About the Project"):
            gr.Markdown(AURIS_ORIGINAL_DESCRIPTION)
            gr.Markdown(METRICS_TEXT)
            # with gr.Row():
            gr.Markdown(WER)
            gr.Markdown(RTFX)
            gr.Markdown(GITHUB_REPO)

            gr.Markdown("## Datasets Used")

demo.launch()
