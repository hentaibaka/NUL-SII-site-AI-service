function handleFormSubmit(event) {
    event.preventDefault()

    let form_data = new FormData(applicantForm);

    fetch('/api/ai/photo/test/offer', {
        method: 'POST',
        body: form_data,
    })
    .then(response => response.blob())
    .then(blob => URL.createObjectURL(blob))
    .then(url => {
        image.src = url;
        link.href = url;
        link.download = 'image.jpg';
    })
    .catch((err) => console.error(err));
}
const link = document.getElementById('download-link');
const image = document.getElementById('processed-image');
const applicantForm = document.getElementById('form');
applicantForm.addEventListener('submit', handleFormSubmit);
  