import tkinter as tk
from tkinter import filedialog, messagebox
from langchain_community.document_loaders import PyPDFLoader
import re
import pandas as pd

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

def extract_date(content):
    # Trekker ut datoen fra PDF-innholdet med regex som leter etter 'Date of issue'
    match = re.search(r"Date of issue\s+(\d{2}\.\d{2}\.\d{4})", content)
    return match.group(1) if match else "Ikke funnet"

def extract_key_metrics(content):
    # Trekker ut nøkkeltall fra PDF-innholdet ved hjelp av regex
    metrics = {}
    
    # Ekstraksjon av nøkkeltallene
    metrics["Total_sales_excl_VAT"] = re.search(r"Total sales\s+Total amount \(excl\. VAT\)\s+[\d,.]+", content)
    metrics["Total_VAT"] = re.search(r"Total sales\s+VAT NOKTotal sales \(incl\. VAT\)\s+[\d,.]+", content)
    metrics["Total_sales_incl_VAT"] = re.search(r"Total sales \(incl\. VAT\)\s+[\d,.]+", content)
    metrics["Wolt_commission"] = re.search(r"Wolt commission\s+[-\d,.]+", content)
    metrics["Product_sales"] = re.search(r"Product sales\s+[\d,.]+", content)
    metrics["Sales_corrections"] = re.search(r"Sales corrections\s+[-\d,.]+", content)
    metrics["Payout_amount"] = re.search(r"Payout amount\s+[\d,.]+", content)
    
    # Konverter regex-resultater til verdier
    for key, match in metrics.items():
        metrics[key] = match.group().split()[-1] if match else "Ikke funnet"
        
    return metrics

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

    # Lagre data i en liste for DataFrame
    data = []

    # Gå gjennom hver valgt fil i sortert rekkefølge
    for file_path in sorted_file_paths:
        try:
            content = read_pdf(file_path)
            location = extract_location(file_path)
            date_of_issue = extract_date(content)
            metrics = extract_key_metrics(content)
            # Legger til dataen i listen
            data.append([location, date_of_issue] + list(metrics.values()))
        except Exception as e:
            messagebox.showerror("Feil", f"Feil ved lesing av {file_path}: {str(e)}")

    # Kolonnenavn
    columns = [
        "Avdelingsnavn", "Dato", 
        "Total_sales_excl_VAT", "Total_VAT", "Total_sales_incl_VAT", 
        "Wolt_commission", "Product_sales", "Sales_corrections", "Payout_amount"
    ]

    # Opprett en DataFrame med de nødvendige kolonnene
    df = pd.DataFrame(data, columns=columns)
    print(df)

    messagebox.showinfo("Fullført", "Prosessering av PDF-filer er ferdig.")

if __name__ == "__main__":
    main()
