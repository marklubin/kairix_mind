import gradio as gr

from kairix.ui.functions import load_from_file

file_import_output = gr.Textbox(
    label="output", placeholder="This is where the import will be displayed."
)
summarizer_output = gr.TextArea(
    label="Summarizer Output",
    placeholder="This is where the summarizer output will be displayed.",
)
with gr.Blocks() as history_importer:
    gr.Markdown("# Kairix Memory Architecture Pipline")
    gr.Markdown("### ChatGPT History Importer")
    file = gr.FileExplorer(label="Select ChatGPT export file", value="test-convos.json")
    gr.Button("Import").click(
        fn=load_from_file, inputs=[file], outputs=[file_import_output]
    )
    file_import_output.render()


def main():
    history_importer.launch()


if __name__ == "__main__":
    main()

    # gr.Markdown("### Chunking Summarizer")
    # model_provider = gr.Dropdown(
    #     label="Select Summarizer Model Provider", choices=["Ollama"]
    # )
    # model = gr.Dropdown(
    #     label="Select Summarizer Model",
    #     choices=["gpt-3.5-turbo", "gpt-4", "llama-2", "mistral-7b"],
    # )
    # prompt = gr.FileExplorer(
    #     label="Select System Prompt File",
    #     value="prompts/system_prompt.txt",
    # )
    # max_tokens = gr.Number(
    #     label="Max Tokens",
    #     value=300,
    # )
    # temp = gr.Number(
    #     label="Temperature",
    #     value=0.7,
    # )
    # chunk_size = gr.Number(
    #     label="Chunk Size",
    #     value=1000,
    # )
    # overlap = gr.Number(
    #     label="Overlap",
    #     value=1000,
    # )
    # gr.Button("Start Summarizer").click(
    #     inputs=[
    #         model_provider,
    #         model,
    #         prompt,
    #         max_tokens,
    #         temp,
    #         chunk_size,
    #         overlap,
    #     ],
    #     outputs=summarizer_output,
    # )
