const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const submitButton = document.querySelector('.submit-button');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress');
const progressText = document.getElementById('progress-text');
const downloadLink = document.getElementById('download-link');
const downloadBtn = document.getElementById('download-btn');

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        submitButton.style.display = 'block';
    } else {
        fileName.textContent = "هیچ فایلی انتخاب نشده است";
        submitButton.style.display = 'none';
    }
});

document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    progressContainer.style.display = 'block';
    submitButton.style.display = 'none';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // نمایش پیشرفت
    const progressSource = new EventSource('/progress');
    progressSource.onmessage = (event) => {
        const progress = event.data;
        progressBar.style.width = progress + '%';
        progressText.textContent = progress + '%';

        if (progress === "100") {
            progressSource.close();
        }
    };

    // ارسال فایل برای تبدیل
    const response = await fetch('/convert', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        downloadBtn.href = `/download/${data.file_path}`;
        downloadLink.style.display = 'block';
    }
});