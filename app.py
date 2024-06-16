import base64
from flask import Flask, url_for, request, redirect, send_file, jsonify
import fitz
from ebooklib import epub
import os
from io import BytesIO
from flask_cors import CORS, cross_origin
import base64
import tempfile
import shutil
import uuid
app = Flask(__name__)
CORS(app, support_credentials=True)
@app.route('/')
def home():
    return 'Home Page'


@app.route('/hello/<name>')
def hello_name(name):
    return f'Hello {name}'




@app.route('/convert_file')
def convert_pdf_to_epub():
    # Paths for the PDF and EPUB files
    pdf_path = os.path.join(app.root_path, 'static', 'filesample.pdf')
    epub_path = os.path.join(app.root_path, 'static',
                             pdf_path.split("/")[-1].replace('.pdf', '.epub'))

    # Open the PDF document
    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        return "Error: PDF file not found!", 404
    except Exception as e:
        return f"Error: {e}", 500

    # Create a new EPUB book
    book = epub.EpubBook()
    book.set_title(pdf_path.split("/")[-1].replace(".pdf", ""))
    book.set_language('en')
    book.add_author("Converted by Python Script")

    # Initialize a variable to track if any content was added
    content_added = False

    # Process each page in the PDF document
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images(full=True)

        # Check if there is any meaningful content on the page
        if text or images:
            content_added = True

            # Create chapter content with text and images
            chapter_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <title>Chapter {page_num + 1}</title>
              </head>
              <body>
                <p>{text}</p>
            """

            # Add images to chapter content and also add images to the book
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"image_{
                    page_num + 1}_{img_index}.{image_ext}"
                image_path = os.path.join(
                    app.root_path, 'static', image_filename)

                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                # Add image to chapter content
                chapter_content += f'<img src="{
                    image_filename}" alt="Image {img_index + 1}"/>'

                # Add image to EPUB book
                image_item = epub.EpubItem(
                    file_name=image_filename, media_type=f"image/{image_ext}", content=image_bytes)
                book.add_item(image_item)

            chapter_content += "</body></html>"

            # Create a chapter
            chapter = epub.EpubHtml(title=f'Chapter {
                                    page_num + 1}', file_name=f'chapter_{page_num + 1}.xhtml', lang='en')
            chapter.content = chapter_content

            # Add chapter to the book
            book.add_item(chapter)

    # Check if any content was added to the book
    if not content_added:
        return "Error: No content found in the PDF!", 500

    # Define Table Of Contents
    book.toc = tuple(epub.Link(f'chapter_{
                     i + 1}.xhtml', f'Chapter {i + 1}', f'chapter_{i + 1}') for i in range(len(book.items)))

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body { font-family: Cambria, Liberation Serif, serif; }
    h1 { text-align: left; text-transform: uppercase; font-weight: 200; }
    img { max-width: 100%; height: auto; } /* Ensure images fit within the reader's screen */
    '''
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # Add CSS file
    book.add_item(nav_css)

    # Basic spine
    book.spine = ['nav'] + [f'chapter_{i + 1}' for i in range(len(book.items))]

    # Write the EPUB book to file
    epub.write_epub(epub_path, book, {})

    return send_file(epub_path, as_attachment=True, download_name=os.path.basename(epub_path))


@app.route('/convert_file_test')
@cross_origin(origin='*')
def convert_pdf_to_epub_test():
    pdf_path = os.path.join(app.root_path, 'static', 'filesample.pdf')
    try:
        doc = fitz.open(pdf_path)
        # Perform the conversion here
        # Example of sending the file as a response
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return str(e), 500


@app.route('/api/convert_file/<file>', methods=['GET'])
@cross_origin(origin='*')
def convert_pdf_to_epub_api(file):
    # Paths for the PDF and EPUB files
    pdf_path = os.path.join(app.root_path, 'static', file)
    epub_path = os.path.join(app.root_path, 'static', pdf_path.split("/")[-1].replace('.pdf', '.epub'))

    # Open the PDF document
    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        return "Error: PDF file not found!", 404
    except Exception as e:
        return f"Error: {e}", 500

    # Create a new EPUB book
    book = epub.EpubBook()
    book.set_title(pdf_path.split("/")[-1].replace(".pdf", ""))
    book.set_language('en')
    book.add_author("Converted by Python Script")

    # Initialize a variable to track if any content was added
    content_added = False

    # Process each page in the PDF document
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images(full=True)

        # Check if there is any meaningful content on the page
        if text or images:
            content_added = True

            # Create chapter content with text and images
            chapter_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <title>Chapter {page_num + 1}</title>
              </head>
              <body>
                <p>{text}</p>
            """

            # Add images to chapter content and also add images to the book
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"image_{
                    page_num + 1}_{img_index}.{image_ext}"
                image_path = os.path.join(
                    app.root_path, 'static', image_filename)

                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                # Add image to chapter content
                chapter_content += f'<img src="{
                    image_filename}" alt="Image {img_index + 1}"/>'

                # Add image to EPUB book
                image_item = epub.EpubItem(
                    file_name=image_filename, media_type=f"image/{image_ext}", content=image_bytes)
                book.add_item(image_item)

            chapter_content += "</body></html>"

            # Create a chapter
            chapter = epub.EpubHtml(title=f'Chapter {
                                    page_num + 1}', file_name=f'chapter_{page_num + 1}.xhtml', lang='en')
            chapter.content = chapter_content

            # Add chapter to the book
            book.add_item(chapter)

    # Check if any content was added to the book
    if not content_added:
        return "Error: No content found in the PDF!", 500

    # Define Table Of Contents
    book.toc = tuple(epub.Link(f'chapter_{
                     i + 1}.xhtml', f'Chapter {i + 1}', f'chapter_{i + 1}') for i in range(len(book.items)))

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body { font-family: Cambria, Liberation Serif, serif; }
    h1 { text-align: left; text-transform: uppercase; font-weight: 200; }
    img { max-width: 100%; height: auto; } /* Ensure images fit within the reader's screen */
    '''
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # Add CSS file
    book.add_item(nav_css)

    # Basic spine
    book.spine = ['nav'] + [f'chapter_{i + 1}' for i in range(len(book.items))]

    # Write the EPUB book to file
    epub.write_epub(epub_path, book, {})

    return send_file(epub_path, as_attachment=True, download_name=os.path.basename(epub_path))




@app.route('/api/move_file', methods=['POST'])
@cross_origin(origin='*')
def move_file():
    try:
        # Check if the POST request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Generate a unique filename to avoid conflicts
        filename = file.filename
        
        # Save the file to the static folder
        target_folder = os.path.join(app.root_path, 'static')
        target_file_path = os.path.join(target_folder, filename)

        # Move the file to the target folder
        file.save(target_file_path)
        #want to directly download it 
        return jsonify({'filename': filename}), 200


    except Exception as e:
        return str(e), 500
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=True)
