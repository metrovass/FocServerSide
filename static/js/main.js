// document.addEventListener('DOMContentLoaded', () => {
//     const nodeForm = document.getElementById('node-form');
//     const successModal = document.getElementById('success-modal');
//     const modalMessage = document.getElementById('modal-message');

//     // Initialize Flowbite Modal instance
//     const modalOptions = {
//         placement: 'center',
//         backdrop: 'dynamic',
//         backdropClasses: 'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40',
//         onHide: () => {
//             // Optional: Actions to perform when the modal is hidden
//             console.log('Modal was hidden');
//         },
//     };
//     const modal = new Flowbite.Modal(successModal, modalOptions);

//     if (nodeForm) {
//         nodeForm.addEventListener('submit', (event) => {
//             event.preventDefault(); // Prevent the default form submission

//             const formData = new FormData(nodeForm);
//             const data = {};
//             formData.forEach((value, key) => {
//                 data[key] = value;
//             });

//             fetch('/submit-node', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify(data),
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     return response.json().then(err => { throw new Error(err.message); });
//                 }
//                 return response.json();
//             })
//             .then(result => {
//                 if (result.success) {
//                     modalMessage.textContent = result.message;
//                     modal.show(); // Show the Flowbite modal on success
//                     nodeForm.reset(); // Reset the form fields
//                 } else {
//                     alert('Error: ' + result.message);
//                 }
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//                 alert('An error occurred: ' + error.message);
//             });
//         });
//     }
// });