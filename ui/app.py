import gradio as gr
from normalizer.eval_utils import score_results


_, _, all_df, composite_df = score_results("../results/")

# TODO: User can see some examples of reference vs prediction

numeric_wer = []
numeric_rtfx = []

for wer in all_df['WER']:
    numeric_wer.append(float(wer.strip().replace('%', '')))
for rtxf in all_df['RTFX']:
    numeric_rtfx.append(float(rtxf.strip()))

with gr.Blocks() as demo:
    gr.Markdown("# ASR benchmark for Child Speech")

    with gr.Tabs(elem_classes="tab-buttons") as tabs:

        with gr.TabItem("All Tests"):
            with gr.Row():
                gr.Label(f"{min(numeric_wer)}%", label="Lowest WER")
                gr.Label(f"{min(numeric_rtfx)}", label="Lowest RTFX")

            gr.DataFrame(all_df)

        with gr.TabItem("Composite Results"):
            gr.DataFrame(composite_df)

        with gr.TabItem("About the Project"):
            gr.Markdown("### Auris")
            gr.Markdown("### Metrics")
            gr.Markdown("### Notes and Suggestions")

demo.launch()
