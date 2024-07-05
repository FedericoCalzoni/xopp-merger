import glob
import os
import shutil
import gzip
import pikepdf
import sys
from natsort import natsorted

def check_xopp_files(input_folder):
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return []

    xopp_files = glob.glob(os.path.join(input_folder, "*.xopp"))
    if not xopp_files:
        print("No .xopp files found in the input folder.")
        return []

    xopp_files = natsorted(xopp_files)  # Sort the files using natural sort
    return xopp_files

def create_temp_folder(tmp_folder):
    os.makedirs(tmp_folder, exist_ok=True)
    print(f"Created temporary folder {tmp_folder}")

def copy_and_rename_files(xopp_files, tmp_folder):
    for file in xopp_files:
        dest_file = os.path.join(tmp_folder, f"{os.path.splitext(os.path.basename(file))[0]}.xml.gz")
        shutil.copy(file, dest_file)
        print(f"Copied {file} to {dest_file}")

def decompress_files(tmp_folder):
    for file in glob.glob(os.path.join(tmp_folder, "*.gz")):
        with gzip.open(file, 'rb') as f_in:
            with open(file[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file)
        print(f"Decompressed {file}")



def copy_pdf_backgrounds(tmp_folder):
    pdf_files = []
    for file in glob.glob(os.path.join(tmp_folder, "*.xml")):
        with open(file, 'r') as in_f:
            content = in_f.read()
            if 'background type="pdf"' in content:
                pdf_filename = content.split('filename="', 1)[1].split('"', 1)[0]
                if os.path.exists(pdf_filename):
                    dest_pdf = os.path.join(tmp_folder, os.path.basename(pdf_filename))
                    shutil.copy(pdf_filename, dest_pdf)
                    pdf_files.append(dest_pdf)
                    print(f"Copied PDF background {pdf_filename} to {dest_pdf}")
                else:
                    print(f"PDF background {pdf_filename} not found")
                    sys.exit(1)
    return pdf_files

def merge_pdf_backgrounds(pdf_files, merged_pdf_path):
    if pdf_files:
        with pikepdf.Pdf.new() as merged_pdf:
            for pdf in pdf_files:
                with pikepdf.open(pdf) as src_pdf:
                    merged_pdf.pages.extend(src_pdf.pages)
            merged_pdf.save(merged_pdf_path)
        print(f"Merged PDF backgrounds into {merged_pdf_path}")

def add_common_header(xopp_files, tmp_folder, output_file):
    with open(output_file, 'w') as out_f:
        with open(os.path.join(tmp_folder, f"{os.path.splitext(os.path.basename(xopp_files[0]))[0]}.xml"), 'r') as in_f:
            for line in in_f:
                if '<page' in line:
                    break
                out_f.write(line)

def append_content(tmp_folder, output_file, merged_pdf_path):
    previous_pages = 0
    first_file = True
    for file in glob.glob(os.path.join(tmp_folder, "*.xml")):            
        
        with open(file, 'r') as in_f:
            content = in_f.read()
                  
            page_content = content.split('<page', 1)[1].rsplit('</page>', 1)[0]
            modified_page_content = []
            for line in page_content.splitlines():
                if '<background type="pdf"' in line:
                    if first_file:
                        line = f'<background type="pdf" domain="absolute" filename="{merged_pdf_path}" pageno="1"/>'
                        first_file = False
                    else:
                        # extrapolate the pageno from the line, 
                        # than increment it by the number of pages of previous PDF files
                        extracted_pageno = line.split('pageno="', 1)[1].split('"', 1)[0]
                        page_number = int(extracted_pageno) + previous_pages
                        line = f'<background type="pdf" pageno="{page_number}"/>'
                modified_page_content.append(line)
            modified_page_content = "\n".join(modified_page_content)
            with open(output_file, 'a') as out_f:
                out_f.write(f"<!-- content from {file} -->\n")
                out_f.write(f"<page{modified_page_content}</page>\n")
                print(f"Appended the page content of {file}")
                
            # Count the number of pages of the related PDF file (if any)
            if 'background type="pdf"' in content:
                pdf_filename = content.split('filename="', 1)[1].split('"', 1)[0]
                with pikepdf.open(pdf_filename) as pdf:
                    previous_pages += len(pdf.pages)

def finalize_output(output_file, output_folder):
    with open(output_file, 'a') as out_f:
        out_f.write('</xournal>')

    with open(output_file, 'rb') as f_in:
        with gzip.open(f"{output_file}.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    shutil.move(f"{output_file}.gz", os.path.join(output_folder, "merged_output.xopp"))
    print("Generated merged_output.xopp")
    
    # Remove the merged_output.xml file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed {output_file}")

def cleanup(tmp_folder):
    shutil.rmtree(tmp_folder)
    print(f"Removed {tmp_folder}")

def main():
    input_folder = os.path.join(os.getcwd(), "") # Folder containing the .xopp files
    tmp_folder = ".tmp-xopp-merger"
    output_folder = os.path.join(os.getcwd(), "output-xopp-merger") # output folder
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "merged_output.xml")
    merged_pdf_path = os.path.join(output_folder, "merged_background.pdf")

    xopp_files = check_xopp_files(input_folder)
    if not xopp_files:
        return

    create_temp_folder(tmp_folder)
    copy_and_rename_files(xopp_files, tmp_folder)
    decompress_files(tmp_folder)
    pdf_files = copy_pdf_backgrounds(tmp_folder)
    merge_pdf_backgrounds(pdf_files, merged_pdf_path)
    add_common_header(xopp_files, tmp_folder, output_file)
    append_content(tmp_folder, output_file, merged_pdf_path)
    finalize_output(output_file, output_folder)
    cleanup(tmp_folder) # TODO delete the temporary folder after debugging
    print("Done")

if __name__ == "__main__":
    main()