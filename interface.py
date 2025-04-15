import gradio as gr
import os
import shutil
import pandas as pd
from main import main

# Directory to save uploaded files
SAVE_DIR = "resumes"
os.makedirs(SAVE_DIR, exist_ok=True)

# Store uploaded file paths globally (you could also use gr.State)
uploaded_files = []

# Upload handler
def upload_files(files):
    global uploaded_files
    uploaded_files = []
    for file in files:
        filename = os.path.basename(file.name)
        save_path = os.path.join(SAVE_DIR, filename)

        # Only copy if the paths are different
        if os.path.abspath(file.name) != os.path.abspath(save_path):
            shutil.copy(file.name, save_path)
        uploaded_files.append(save_path)

    return f"{len(uploaded_files)} file(s) uploaded and saved."

# Run main based on what's in SAVE_DIR
def run_main():
    files = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if os.path.isfile(os.path.join(SAVE_DIR, f))]

    if len(files) < 1:
        return "No files found in upload directory.", None

    df = main()
    return "Processing complete!", df

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### Upload Files and Run Main Function")

    file_input = gr.File(file_types=[".csv", ".pdf", ".txt"], file_count="multiple", label="Upload Files")
    upload_btn = gr.Button("Upload Files")
    upload_status = gr.Textbox(label="Upload Status", interactive=False)

    run_btn = gr.Button("Run Main")
    run_status = gr.Textbox(label="Run Status", interactive=False)
    result_df = gr.Dataframe(label="Resulting DataFrame", visible=True)

    upload_btn.click(upload_files, inputs=[file_input], outputs=[upload_status])
    run_btn.click(run_main, outputs=[run_status, result_df])

# Launch the app
if __name__ == "__main__":
    demo.launch()
