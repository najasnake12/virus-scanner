import os
import win32file
import win32con
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def get_all_files(directory):
    """Get all files in the specified directory."""
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def load_virus_hashes(file_path):
    """Load virus hashes from a file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def read_locked_file(file_path):
    """Reads the content of a file even if it is locked by another process."""
    hfile = win32file.CreateFile(
        file_path,
        win32con.GENERIC_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        0,
        None
    )
    
    try:
        _, content = win32file.ReadFile(hfile, os.path.getsize(file_path))
        return content.decode('utf-8')
    finally:
        win32file.CloseHandle(hfile)

def virus_hash_detect(directory, result_text_widget):
    """Detect files containing virus hashes and handle them."""
    virus_hashes = load_virus_hashes('virushashes.txt')
    files = get_all_files(directory)
    
    result_text_widget.config(state=tk.NORMAL)
    result_text_widget.delete(1.0, tk.END)
    
    for file_path in files:
        if os.path.basename(file_path) == 'virushashes.txt':
            continue
        
        try:
            content = read_locked_file(file_path)
            if any(hash in content for hash in virus_hashes):
                os.remove(file_path)
                result_text_widget.insert(tk.END, f'⚠️ {file_path} ⚠️ Contains A Virus! Removing affected file! ⚠️\n')
            else:
                result_text_widget.insert(tk.END, f'{file_path} ✅ File Has No Viruses\n')
        
        except Exception as e:
            result_text_widget.insert(tk.END, f'Error: {e}\n')
    
    result_text_widget.config(state=tk.DISABLED)
    messagebox.showinfo("Scan Complete", "Virus scan completed!")

def browse_directory():
    """Open a directory chooser dialog and start the virus scan."""
    directory = filedialog.askdirectory()
    if directory:
        virus_hash_detect(directory, result_text_widget)

# Set up the main window
root = tk.Tk()
root.title("Virus Scanner")

# Set up the UI components
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_browse = tk.Button(frame, text="Choose the folder to scan for viruses", command=browse_directory)
btn_browse.pack()

result_text_widget = scrolledtext.ScrolledText(frame, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)
result_text_widget.pack(pady=10)

# Run the application
root.mainloop()
