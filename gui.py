import os
import threading
import logging
import tkinter.messagebox as messagebox
import customtkinter as ctk
from customtkinter import filedialog
from dotenv import load_dotenv

# Import pipeline modules
from video_downloader import download_video
from audio_processor import extract_audio, transcribe_chinese_audio
from translator import translate_subtitles
from voice_generator import generate_vietnamese_voice
from video_composer import compose_final_video

# --- Custom Log Handler for CTkTextbox ---
class CTkTextboxHandler(logging.Handler):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance

    def emit(self, record):
        msg = self.format(record)
        self.app_instance.append_log(msg)


# --- Main GUI Application ---
class LocalizationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. UI Configuration
        self.title("Automated Video Localization Pipeline")
        self.geometry("800x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Load existing .env variables
        load_dotenv()
        env_openai = os.environ.get("OPENAI_API_KEY", "")
        env_azure = os.environ.get("AZURE_SPEECH_KEY", "")

        # Main frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # --- Inputs Section ---
        # 1. Video URL
        self.url_label = ctk.CTkLabel(self, text="Douyin/Bilibili Video URL:", font=("Arial", 12, "bold"))
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.url_entry = ctk.CTkEntry(self, placeholder_text="https://...")
        self.url_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. Output Directory
        self.out_label = ctk.CTkLabel(self, text="Output Directory:", font=("Arial", 12, "bold"))
        self.out_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.out_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.out_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.out_frame.grid_columnconfigure(0, weight=1)
        
        self.out_entry = ctk.CTkEntry(self.out_frame, placeholder_text="Select folder...")
        self.out_entry.grid(row=0, column=0, sticky="ew")
        default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.out_entry.insert(0, default_out)
        
        self.browse_btn = ctk.CTkButton(self.out_frame, text="Browse", width=80, command=self.browse_directory)
        self.browse_btn.grid(row=0, column=1, padx=(10, 0))

        # 3. API Keys Section (Optional Override)
        self.keys_frame = ctk.CTkFrame(self)
        self.keys_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.keys_frame.grid_columnconfigure((1, 3), weight=1)

        self.openai_label = ctk.CTkLabel(self.keys_frame, text="OpenAI Key:")
        self.openai_label.grid(row=0, column=0, padx=10, pady=10)
        self.openai_entry = ctk.CTkEntry(self.keys_frame, show="*")
        self.openai_entry.insert(0, env_openai)
        self.openai_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.azure_label = ctk.CTkLabel(self.keys_frame, text="Azure Speech Key:")
        self.azure_label.grid(row=0, column=2, padx=10, pady=10)
        self.azure_entry = ctk.CTkEntry(self.keys_frame, show="*")
        self.azure_entry.insert(0, env_azure)
        self.azure_entry.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # --- Logging Console Section ---
        self.log_label = ctk.CTkLabel(self, text="Real-time Log Console:", font=("Arial", 12, "bold"))
        self.log_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="sw")
        
        self.log_console = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Consolas", 12))
        self.log_console.grid(row=6, column=0, padx=20, pady=5, sticky="nsew")

        # --- Status & Action Section ---
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.grid(row=7, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.progress_bar.set(0)

        self.start_btn = ctk.CTkButton(self, text="START PIPELINE", font=("Arial", 14, "bold"), height=40, command=self.start_pipeline)
        self.start_btn.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configures the root logger to output to our custom UI handler."""
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates if run multiple times
        if logger.hasHandlers():
            logger.handlers.clear()
            
        ui_handler = CTkTextboxHandler(self)
        ui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(ui_handler)
        
        # Also log to console for debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    def browse_directory(self):
        """Opens a dialog to select the output directory."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.out_entry.delete(0, ctk.END)
            self.out_entry.insert(0, folder_selected)

    def append_log(self, text):
        """Thread-safe way to append text to the CTkTextbox."""
        self.after(0, self._append_log_sync, text)

    def _append_log_sync(self, text):
        self.log_console.configure(state="normal")
        self.log_console.insert(ctk.END, text + "\n")
        self.log_console.see(ctk.END)
        self.log_console.configure(state="disabled")

    def update_progress(self, value):
        """Thread-safe progress bar update (0.0 to 1.0)."""
        self.after(0, self.progress_bar.set, value)

    def set_gui_state(self, is_running):
        """Disables/Enables inputs and buttons during execution."""
        state = "disabled" if is_running else "normal"
        def _update():
            self.start_btn.configure(state=state, text="PROCESSING..." if is_running else "START PIPELINE")
            self.url_entry.configure(state=state)
            self.out_entry.configure(state=state)
            self.browse_btn.configure(state=state)
            self.openai_entry.configure(state=state)
            self.azure_entry.configure(state=state)
        self.after(0, _update)

    def start_pipeline(self):
        """Validates inputs and starts the pipeline thread."""
        video_url = self.url_entry.get().strip()
        out_dir = self.out_entry.get().strip()
        openai_key = self.openai_entry.get().strip()
        azure_key = self.azure_entry.get().strip()

        if not video_url:
            messagebox.showwarning("Validation Error", "Please enter a valid Video URL.")
            return
        if not out_dir:
            messagebox.showwarning("Validation Error", "Please select an Output Directory.")
            return
        if not openai_key or not azure_key:
            messagebox.showwarning("Validation Error", "Please provide both OpenAI and Azure API Keys.")
            return

        # Override environment variables for the current session
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["AZURE_SPEECH_KEY"] = azure_key
        
        # Make sure Azure Region is set (defaulting to eastus if not set in .env)
        if not os.environ.get("AZURE_SPEECH_REGION"):
            os.environ["AZURE_SPEECH_REGION"] = "eastus"

        self.set_gui_state(is_running=True)
        self.progress_bar.set(0)
        
        # Clear log console
        self.log_console.configure(state="normal")
        self.log_console.delete("1.0", ctk.END)
        self.log_console.configure(state="disabled")

        # Start background thread
        thread = threading.Thread(target=self.run_pipeline_thread, args=(video_url, out_dir), daemon=True)
        thread.start()

    def run_pipeline_thread(self, video_url, base_out_dir):
        """The core orchestration logic running in a separate thread."""
        logger = logging.getLogger(__name__)
        
        try:
            # Setup working directories
            workspace_dir = os.path.join(base_out_dir, "workspace")
            tts_dir = os.path.join(workspace_dir, "tts_segments")
            
            for directory in [base_out_dir, workspace_dir, tts_dir]:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            # STEP 1
            logger.info("--- STEP 1: Video Scraping & Downloading ---")
            self.update_progress(0.1)
            original_video_path = download_video(video_url, workspace_dir)
            self.update_progress(0.2)

            # STEP 2
            logger.info("--- STEP 2: Audio Extraction & STT ---")
            audio_path = os.path.join(workspace_dir, "extracted_audio.wav")
            extract_audio(original_video_path, audio_path)
            self.update_progress(0.3)
            chinese_subtitles = transcribe_chinese_audio(audio_path)
            self.update_progress(0.4)

            # STEP 3
            logger.info("--- STEP 3: Context-Aware Machine Translation ---")
            vietnamese_subtitles = translate_subtitles(chinese_subtitles)
            self.update_progress(0.6)

            # STEP 4
            logger.info("--- STEP 4: Vietnamese TTS & Audio Alignment ---")
            voice_segments = generate_vietnamese_voice(vietnamese_subtitles, tts_dir)
            self.update_progress(0.8)

            # STEP 5
            logger.info("--- STEP 5: Video Composition & Spintax ---")
            final_video_name = os.path.basename(original_video_path).rsplit('.', 1)[0] + "_vi.mp4"
            final_video_path = os.path.join(base_out_dir, final_video_name)
            compose_final_video(original_video_path, voice_segments, final_video_path)
            
            self.update_progress(1.0)
            logger.info(f"Pipeline completed successfully!\nSaved to: {final_video_path}")
            
            # Show success message
            self.after(0, lambda: messagebox.showinfo("Success", f"Video Localized Successfully!\n\nSaved at:\n{final_video_path}"))

        except Exception as e:
            logger.error(f"Pipeline Failed: {e}", exc_info=True)
            self.after(0, lambda: messagebox.showerror("Pipeline Error", f"An error occurred:\n{str(e)}\n\nCheck the logs for details."))
            
        finally:
            self.set_gui_state(is_running=False)


if __name__ == "__main__":
    app = LocalizationApp()
    app.mainloop()