document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebarMenu');
    const mainContent = document.querySelector('.main-content');

    sidebarToggle.addEventListener('click', function() {
        if (sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            mainContent.classList.add('sidebar-hidden');
        } else {
            sidebar.classList.add('show');
            mainContent.classList.remove('sidebar-hidden');
        }
    });
});