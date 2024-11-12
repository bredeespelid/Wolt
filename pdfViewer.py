import tkinter as tk
from tkinter import filedialog, messagebox
from langchain_community.document_loaders import PyPDFLoader
import re

def read_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()  # Leser alle sider i PDF-en
    content = "\n".join(page.page_content for page in pages)
    return content

def extract_location(file_path):
    # Trekker ut lokasjonsnavnet fra filstien med hensyn til understreker og mellomrom
    match = re.search(r"Wolt/Godt[ _]Brød[ _]([^_]+)", file_path)
    return match.group(1) if match else ""

def extract_report_type(file_path):
    # Bestemmer rekkefølgen basert på rapporttype: payout_report først, sales_report sist
    if "payout_report" in file_path:
        return 0  # Prioritet 0 for payout_report
    elif "sales_report" in file_path:
        return 2  # Prioritet 2 for sales_report
    else:
        return 1  # Prioritet 1 for andre rapporter

def sort_files(file_paths):
    # Sorter filene på lokasjon først, deretter på rapporttype
    sorted_files = sorted(file_paths, key=lambda x: (
        extract_location(x),        # Sorter på lokasjonsnavn først
        extract_report_type(x)      # Sorter payout før andre typer, og sales til slutt
    ))
    return sorted_files

def main():
    root = tk.Tk()
    root.withdraw()  # Skjul hovedvinduet

    # Åpne dialog for å velge PDF-filer
    file_paths = filedialog.askopenfilenames(
        title="Velg PDF-filer",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_paths:
        messagebox.showinfo("Informasjon", "Ingen filer valgt. Programmet avsluttes.")
        return

    # Sorter filene i ønsket rekkefølge
    sorted_file_paths = sort_files(file_paths)

    # Gå gjennom hver valgt fil i sortert rekkefølge og vis innholdet i konsollen
    for file_path in sorted_file_paths:
        try:
            content = read_pdf(file_path)
            print(f"Innhold fra {file_path}:\n{content}\n")
        except Exception as e:
            messagebox.showerror("Feil", f"Feil ved lesing av {file_path}: {str(e)}")

    messagebox.showinfo("Fullført", "Prosessering av PDF-filer er ferdig.")

if __name__ == "__main__":
    main()
