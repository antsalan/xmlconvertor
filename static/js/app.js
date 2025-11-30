let selectedFile = null;

document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    
    uploadZone.addEventListener('click', function(e) {
        if (e.target.tagName !== 'BUTTON') {
            fileInput.click();
        }
    });
    
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });
});

function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.xml')) {
        showError('Please select an XML file.');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showError('File size exceeds 16MB limit.');
        return;
    }
    
    selectedFile = file;
    
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    
    document.getElementById('upload-zone').classList.add('d-none');
    document.getElementById('file-info').classList.remove('d-none');
    hideError();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('upload-zone').classList.remove('d-none');
}

function convertFile() {
    if (!selectedFile) {
        showError('No file selected.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('progress-section').classList.remove('d-none');
    document.getElementById('result-section').classList.add('d-none');
    hideError();
    
    fetch('/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('progress-section').classList.add('d-none');
        
        if (data.error) {
            showError(data.error);
            document.getElementById('upload-zone').classList.remove('d-none');
            return;
        }
        
        showResult(data);
    })
    .catch(error => {
        document.getElementById('progress-section').classList.add('d-none');
        showError('Network error. Please try again.');
        document.getElementById('upload-zone').classList.remove('d-none');
    });
}

function showResult(data) {
    document.getElementById('stats-rows').textContent = data.total_rows + ' rows';
    document.getElementById('stats-cols').textContent = data.total_columns + ' columns';
    
    document.getElementById('download-btn').href = '/download/' + data.file_id;
    document.getElementById('download-btn').download = data.filename;
    
    const headerRow = document.getElementById('preview-header');
    headerRow.innerHTML = '';
    data.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        th.title = col;
        headerRow.appendChild(th);
    });
    
    const tbody = document.getElementById('preview-body');
    tbody.innerHTML = '';
    data.preview.forEach(row => {
        const tr = document.createElement('tr');
        data.columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            td.title = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    
    let previewInfo = `Showing ${data.preview.length} of ${data.total_rows} rows`;
    if (data.preview_limited) {
        previewInfo += ' (preview limited)';
    }
    document.getElementById('preview-info').textContent = previewInfo;
    
    document.getElementById('result-section').classList.remove('d-none');
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-section').classList.remove('d-none');
}

function hideError() {
    document.getElementById('error-section').classList.add('d-none');
}

function resetUpload() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('progress-section').classList.add('d-none');
    document.getElementById('result-section').classList.add('d-none');
    document.getElementById('upload-zone').classList.remove('d-none');
    hideError();
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
