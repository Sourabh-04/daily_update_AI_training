import fitz

doc = fitz.open("EY_Digital_PDF_Practice.pdf")

print("Pages",len(doc))

# for page in doc:
#     print(page.get_text())

# print("page1 text",doc[0].get_text())

for page in doc:
    page_t = page.get_text()
    words = page_t.split()
    for word in words:
        if "maintenance" in word.lower():
            print('Appears')
            break

Count_V303 =0
for page in doc:
    page_t = page.get_text()
    words = page_t.split()
    for word in words:
        if "V303" in word:
            Count_V303 +=1
print(Count_V303)


# 2 page
# print(doc[1].get_text())

text_file =""

for page in doc:
    text_file = text_file + page.get_text()

print(text_file)

with open("didgital_pdf_text.txt", "w") as f:
    f.write(text_file)
