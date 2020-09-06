import pikepdf
from getpass import getpass

password =getpass()

with pikepdf.open("C:/Users/ambik/Downloads/harshala.pdf", password=password) as pdf:
    num_pages = len(pdf.pages)
    print("Total pages:", num_pages)
