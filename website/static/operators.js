// // app.js
// function showOperators() {
//     document.getElementById('operatorList').classList.remove('hidden');
//     document.getElementById('callsContainer').classList.add('hidden');
//     document.getElementById('backButton').classList.add('hidden');
// }
//
// function showCalls(operatorNumber) {
//     console.log(`Fetching calls for operator ${operatorNumber}`);
//     fetch(`/operator_data/${operatorNumber}`)
//         .then(response => response.json())
//         .then(data => {
//             console.log(data); // Add this to check if data is being received
//             const callTableBody = document.getElementById('callTableBody');
//             callTableBody.innerHTML = ''; // Clear previous data
//
//             if (data.calls.length > 0) {
//                 document.getElementById('noRecords').classList.add('hidden');
//                 data.calls.forEach(call => {
//                     const row = document.createElement('tr');
//                     row.innerHTML = `
//                         <td>${call.phone_number}</td>
//                         <td>${call.operator_number}</td>
//                         <td>${call.call_date}</td>
//                         <td>${call.call_time}</td>
//                         <td>${call.transcript.replace(/\n/g, '<br>')}</td>
//                         <td>${call.call_type}</td>
//                         <td>${call.result}</td>
//                     `;
//                     callTableBody.appendChild(row);
//                 });
//             } else {
//                 document.getElementById('noRecords').classList.remove('hidden');
//             }
//
//             document.getElementById('operatorNumber').innerText = operatorNumber;
//             document.getElementById('operatorList').classList.add('hidden');
//             document.getElementById('callsContainer').classList.remove('hidden');
//             document.getElementById('backButton').classList.remove('hidden');
//         })
//         .catch(error => console.error('Error fetching call data:', error)); // Add error handling
// }

document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebarMenu');
    const mainContent = document.getElementById('main-content');

    sidebarToggle.addEventListener('click', function() {
        if (sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            mainContent.classList.add('sidebar-hidden');
            mainContent.classList.remove('sidebar-show');
        } else {
            sidebar.classList.add('show');
            mainContent.classList.remove('sidebar-hidden');
            mainContent.classList.add('sidebar-show');
        }
    });
});