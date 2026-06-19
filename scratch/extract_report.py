import pdfplumber

def extract_pdf_info(pdf_path, output_txt_path):
    print("Reading PDF...")
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        print(f"Total pages: {num_pages}")
        
        with open(output_txt_path, "w", encoding="utf-8") as f:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                f.write(f"--- PAGE {i+1} ---\n")
                if text:
                    f.write(text)
                f.write("\n")
    print(f"Finished extracting text to {output_txt_path}")

if __name__ == "__main__":
    extract_pdf_info("INFORME DE GESTIÓN ANUAL 2025.pdf", "scratch/informe_2025_extracted.txt")
