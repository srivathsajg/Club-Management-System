/**
 * Page-specific fixes for Club Management System
 * This script addresses specific issues mentioned in the requirements
 */

// Disable the global spinner for specific AJAX requests
let disableGlobalSpinner = false;

// Check if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPageFixes);
} else {
    initPageFixes();
}

function initPageFixes() {
    // Fix 1: Remove create project icon for members
    if (document.body.classList.contains('member-role')) {
        const createProjectButtons = document.querySelectorAll('.create-project-btn');
        createProjectButtons.forEach(button => {
            button.style.display = 'none';
        });
    }

    // Fix 2: Fix active members display
    const activeMembersContainers = document.querySelectorAll('.active-members-container');
    if (activeMembersContainers.length > 0) {
        activeMembersContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
            
            // Add a small delay to ensure content is properly loaded
            setTimeout(() => {
                // If the container is empty, add a message
                if (container.querySelectorAll('.member-item').length === 0) {
                    container.innerHTML = '<p class="text-center">No active members found.</p>';
                }
            }, 100);
        });
    }

    // Fix 3: Fix announcements display
    const announcementContainers = document.querySelectorAll('.announcements-container');
    if (announcementContainers.length > 0) {
        announcementContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
            
            // Add a small delay to ensure content is properly loaded
            setTimeout(() => {
                // If the container is empty, add a message
                if (container.querySelectorAll('.announcement-item').length === 0) {
                    container.innerHTML = '<p class="text-center">No announcements found.</p>';
                }
            }, 100);
        });
    }

    // Fix 4: Fix discussions display
    const discussionContainers = document.querySelectorAll('.discussions-container');
    if (discussionContainers.length > 0) {
        discussionContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }

    // Fix 5: Fix notification display
    const notificationContainers = document.querySelectorAll('.notification-container');
    if (notificationContainers.length > 0) {
        notificationContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }

    // Fix 6: Fix admin dashboard display
    const adminDashboardContainers = document.querySelectorAll('.admin-dashboard-container');
    if (adminDashboardContainers.length > 0) {
        adminDashboardContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }

    // Fix 7: Fix club detail display
    const clubDetailContainers = document.querySelectorAll('.club-detail-container');
    if (clubDetailContainers.length > 0) {
        clubDetailContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }

    // Fix 8: Fix event display
    const eventContainers = document.querySelectorAll('.event-container');
    if (eventContainers.length > 0) {
        eventContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }

    // Fix 9: Fix profile display
    const profileContainers = document.querySelectorAll('.profile-container');
    if (profileContainers.length > 0) {
        profileContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }
    
    // Fix 10: Optimize club, project, and event creation forms
    const creationForms = document.querySelectorAll('.creation-form, form[action*="create"]');
    if (creationForms.length > 0) {
        creationForms.forEach(form => {
            // Add data-no-spinner attribute to prevent the global spinner
            form.setAttribute('data-no-spinner', 'true');
            
            // Add custom submission handler with optimized loading
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show a more lightweight spinner inside the form
                const submitBtn = this.querySelector('button[type="submit"]');
                if (!submitBtn) return this.submit(); // If no button, just submit normally
                
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                
                // Set a flag to disable the global spinner
                window.disableGlobalSpinner = true;
                
                // Submit the form after a short delay
                setTimeout(() => {
                    try {
                        this.submit();
                    } catch (err) {
                        console.error('Form submission error:', err);
                        // Reset button state on error
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalBtnText;
                        window.disableGlobalSpinner = false;
                    }
                }, 100);
            });
        });
    }

    // Fix 10: Fix filter display
    const filterContainers = document.querySelectorAll('.filter-container');
    if (filterContainers.length > 0) {
        filterContainers.forEach(container => {
            // Ensure the container is visible
            container.style.display = 'block';
        });
    }
}