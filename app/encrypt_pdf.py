from PyPDF2 import PdfFileWriter, PdfFileReader


def encrypt_pdf(input_pdf, password):
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(input_pdf)

    for page in range(pdf_reader.numPages):
        pdf_writer.addPage(pdf_reader.getPage(page))

    pdf_writer.encrypt(password, use_128bit=True)

    with open(input_pdf, 'wb') as f:
        pdf_writer.write(f)

    f.close()
