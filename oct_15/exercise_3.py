import fitz
import pytesseract
from PIL import Image
doc = fitz.open("EY_Scanned_PDF_OCR_Practice.pdf")
page = doc[0]
pix = page.get_pixmap()
pix.save("scanned_page.png")
image = Image.open("scanned_page.png")
text = pytesseract.image_to_string(image)
# print(text)

text_detected = "Forklift FL-17" in text
print(f"Task 5 Detected {text_detected}")

text_injr = "injuries" in text
print(f"Task 6 injuries Detected {text_injr}")

lines = text.splitlines()

for line in lines:
    if "inspection" in line.lower():
        print(f"Task 7 inspections Detected {line}")


with open("ocr_result.txt","w") as f:
    f.write(text)
    print("Task 8 ocr_result.txt written")

Count_inspection = text.lower().count('inspection')
print(Count_inspection)

for line in lines:
    if "Loading Bay" in line:
        print(f"Task 10 Loading Bay Detected {line}")


