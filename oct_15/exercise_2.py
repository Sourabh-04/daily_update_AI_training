from pypdf import PdfReader

reader = PdfReader("EY_Digital_PDF_Practice.pdf")

print("Pages:", len(reader.pages))
# for page in reader.pages:
#     print(page.extract_text())


# print("page1 text",reader.pages[0].extract_text())

# print("page1 text",reader.pages[1].extract_text())


text_file =""

for page in reader.pages:
    text_file = text_file + page.extract_text()



if "NorthStar Maintenance" in text_file:
    print("NorthStar Maintenance")


word_cnt = text_file.lower().count("vendor")

print(word_cnt)


with open("pypdf_output.txt", "w") as f:
     f.write(text_file)