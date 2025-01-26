import time
from flask import Flask, render_template, request, jsonify, send_file
import os
from pdf2docx import Converter

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('nv1.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({"status": "error", "message": "فایل انتخابی باید PDF باشد."}), 400

    # ذخیره فایل آپلودشده
    input_pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_word_path = os.path.join(OUTPUT_FOLDER, file.filename.replace('.pdf', '.docx'))
    file.save(input_pdf_path)

    # تبدیل PDF به Word
    try:
        cv = Converter(input_pdf_path)
        cv.convert(output_word_path, start=0, end=None)
        cv.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطا در تبدیل فایل: {str(e)}"}), 500

    # بازگرداندن مسیر فایل Word
    return jsonify({"status": "success", "file_path": output_word_path})

@app.route('/progress')
def progress():
    # شبیه‌سازی درصد پیشرفت
    for i in range(0, 101, 10):
        time.sleep(0.3)
        yield f"data:{i}\n\n"

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=3728)