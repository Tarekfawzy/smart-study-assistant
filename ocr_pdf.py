import sys
import os
import fitz
from PIL import Image
import pytesseract
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_pdf(input_path):
    output_path = input_path.replace(".pdf", "_ocr.pdf")
    doc = fitz.open(input_path)
    output_doc = fitz.open()
    
    for i, page in enumerate(doc):
        print(f"Processing page {i+1}/{len(doc)}...")
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
        
        temp_path = f"temp_page_{i}.pdf"
        with open(temp_path, "wb") as f:
            f.write(text)
        
        temp_doc = fitz.open(temp_path)
        output_doc.insert_pdf(temp_doc)
        temp_doc.close()
        os.remove(temp_path)
    
    output_doc.save(output_path)
    output_doc.close()
    doc.close()
    print(f"Done! Saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_pdf.py <path_to_pdf>")
    else:
        ocr_pdf(sys.argv[1])