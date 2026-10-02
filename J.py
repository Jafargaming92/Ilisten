import os
import threading
import tkinter as tk
from tkinter import messagebox
import pygame
import yt_dlp

# Check Android Native MediaPlayer support via pyjnius
USE_ANDROID_MEDIA = False
try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    USE_ANDROID_MEDIA = True
except Exception:
    pygame.mixer.init()

MUSIC_DIR = "astama_music"
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

class AstamaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Astama Music Player")
        self.root.geometry("450x600")
        self.root.configure(bg="#0B0B0F")

        self.yt_url_var = tk.StringVar()
        self.current_song = None
        self.android_player = None
        self.is_paused = False

        self.setup_ui()
        self.refresh_music_list()

    def setup_ui(self):
        # Header
        header = tk.Label(
            self.root, 
            text="ASTAMA MUSIC", 
            font=("Arial", 18, "bold"), 
            bg="#0B0B0F", 
            fg="#7C5CFF"
        )
        header.pack(pady=15)

        sub_header = tk.Label(
            self.root, 
            text="Offline Music Downloader & Player", 
            font=("Arial", 9), 
            bg="#0B0B0F", 
            fg="#A0A0B0"
        )
        sub_header.pack(pady=(0, 15))

        # Input Section
        input_frame = tk.Frame(self.root, bg="#15151C")
        input_frame.pack(fill="x", padx=15, pady=8)

        lbl = tk.Label(
            input_frame, 
            text="Paste YouTube URL:", 
            font=("Arial", 10, "bold"), 
            bg="#15151C", 
            fg="#FFFFFF"
        )
        lbl.pack(anchor="w", padx=10, pady=(10, 4))

        entry = tk.Entry(
            input_frame, 
            textvariable=self.yt_url_var, 
            font=("Arial", 10), 
            bg="#0B0B0F", 
            fg="#FFFFFF", 
            insertbackground="white"
        )
        entry.pack(fill="x", padx=10, pady=5)

        self.download_btn = tk.Button(
            input_frame, 
            text="DOWNLOAD FOR OFFLINE", 
            font=("Arial", 10, "bold"), 
            bg="#7C5CFF", 
            fg="#FFFFFF", 
            command=self.start_download_thread, 
            bd=0
        )
        self.download_btn.pack(fill="x", padx=10, pady=10)

        # Status Indicator
        self.status_lbl = tk.Label(
            self.root, 
            text="Status: Ready", 
            font=("Arial", 9), 
            bg="#0B0B0F", 
            fg="#A0A0B0"
        )
        self.status_lbl.pack(pady=5)

        # Local Songs List
        lib_lbl = tk.Label(
            self.root, 
            text="Offline Library:", 
            font=("Arial", 11, "bold"), 
            bg="#0B0B0F", 
            fg="#FFFFFF"
        )
        lib_lbl.pack(anchor="w", padx=15, pady=(10, 4))

        list_frame = tk.Frame(self.root, bg="#15151C")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.music_listbox = tk.Listbox(
            list_frame, 
            font=("Arial", 10), 
            bg="#15151C", 
            fg="#FFFFFF", 
            selectbackground="#7C5CFF", 
            selectforeground="#FFFFFF", 
            bd=0
        )
        self.music_listbox.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(list_frame, command=self.music_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.music_listbox.config(yscrollcommand=scrollbar.set)

        # Player Controls
        controls_frame = tk.Frame(self.root, bg="#15151C")
        controls_frame.pack(fill="x", padx=15, pady=15)

        self.play_btn = tk.Button(
            controls_frame, 
            text="PLAY", 
            font=("Arial", 10, "bold"), 
            bg="#7C5CFF", 
            fg="#FFFFFF", 
            command=self.play_music, 
            bd=0, 
            width=8
        )
        self.play_btn.pack(side="left", padx=5, pady=8)

        self.pause_btn = tk.Button(
            controls_frame, 
            text="PAUSE", 
            font=("Arial", 10, "bold"), 
            bg="#252532", 
            fg="#FFFFFF", 
            command=self.pause_music, 
            bd=0, 
            width=8
        )
        self.pause_btn.pack(side="left", padx=5, pady=8)

        self.delete_btn = tk.Button(
            controls_frame, 
            text="DELETE", 
            font=("Arial", 10, "bold"), 
            bg="#FF4D4D", 
            fg="#FFFFFF", 
            command=self.delete_music, 
            bd=0, 
            width=8
        )
        self.delete_btn.pack(side="right", padx=5, pady=8)

    def refresh_music_list(self):
        self.music_listbox.delete(0, tk.END)
        files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.m4a', '.webm', '.ogg', '.wav'))]
        for file in files:
            self.music_listbox.insert(tk.END, file)

    def start_download_thread(self):
        url = self.yt_url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please paste a YouTube link first!")
            return

        self.download_btn.config(state="disabled", text="Downloading...")
        self.status_lbl.config(text="Status: Downloading Audio...", fg="#7C5CFF")

        threading.Thread(target=self.download_youtube_audio, args=(url,), daemon=True).start()

    def download_youtube_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/140/bestaudio/best',  # Prefer m4a format
            'outtmpl': os.path.join(MUSIC_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self.on_download_success)
        except Exception as e:
            self.root.after(0, lambda: self.on_download_error(str(e)))

    def on_download_success(self):
        self.yt_url_var.set("")
        self.download_btn.config(state="normal", text="DOWNLOAD FOR OFFLINE")
        self.status_lbl.config(text="Status: Download Complete!", fg="#00FF7F")
        self.refresh_music_list()

    def on_download_error(self, err_msg):
        self.download_btn.config(state="normal", text="DOWNLOAD FOR OFFLINE")
        self.status_lbl.config(text="Status: Download Failed", fg="#FF4D4D")
        messagebox.showerror("Error", f"Failed to download:\n{err_msg}")

    def play_music(self):
        selected = self.music_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a song from the list!")
            return

        song_name = self.music_listbox.get(selected[0])
        song_path = os.path.abspath(os.path.join(MUSIC_DIR, song_name))

        self.stop_current_audio()

        # Try Android Native Player
        if USE_ANDROID_MEDIA:
            try:
                self.android_player = MediaPlayer()
                self.android_player.setDataSource(song_path)
                self.android_player.prepare()
                self.android_player.start()
                self.current_song = song_path
                self.is_paused = False
                self.status_lbl.config(text=f"Playing: {song_name[:20]}...", fg="#00FF7F")
                return
            except Exception as e:
                print("Android player error:", e)

        # Pygame Fallback
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.current_song = song_path
            self.is_paused = False
            self.status_lbl.config(text=f"Playing: {song_name[:20]}...", fg="#00FF7F")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot play file format.\nPlease delete and download again.\nDetails: {e}")

    def pause_music(self):
        if USE_ANDROID_MEDIA and self.android_player:
            try:
                if self.android_player.isPlaying():
                    self.android_player.pause()
                    self.is_paused = True
                    self.status_lbl.config(text="Status: Paused", fg="#A0A0B0")
                elif self.is_paused:
                    self.android_player.start()
                    self.is_paused = False
                    self.status_lbl.config(text="Status: Playing", fg="#00FF7F")
            except Exception:
                pass
        else:
            if pygame.mixer.music.get_busy() and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.status_lbl.config(text="Status: Paused", fg="#A0A0B0")
            elif self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.status_lbl.config(text="Status: Playing", fg="#00FF7F")

    def stop_current_audio(self):
        if USE_ANDROID_MEDIA and self.android_player:
            try:
                self.android_player.stop()
                self.android_player.release()
                self.android_player = None
            except Exception:
                pass
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def delete_music(self):
        selected = self.music_listbox.curselection()
        if not selected:
            return

        song_name = self.music_listbox.get(selected[0])
        song_path = os.path.abspath(os.path.join(MUSIC_DIR, song_name))

        if messagebox.askyesno("Confirm", f"Delete {song_name}?"):
            if self.current_song == song_path:
                self.stop_current_audio()
            if os.path.exists(song_path):
                os.remove(song_path)
            self.refresh_music_list()
            self.status_lbl.config(text="Status: Deleted", fg="#A0A0B0")

if __name__ == "__main__":
    root = tk.Tk()
    app = AstamaApp(root)
    root.mainloop()
  
