/**
 * Loading Spinner Component
 * Provides a simple way to show loading indicators during AJAX requests
 */

class LoadingSpinner {
    constructor() {
        this.createSpinnerElement();
    }

    createSpinnerElement() {
        // Create spinner container if it doesn't exist
        if (!document.getElementById('global-spinner')) {
            const spinner = document.createElement('div');
            spinner.id = 'global-spinner';
            spinner.className = 'loading-spinner';
            spinner.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
            document.body.appendChild(spinner);

            // Add CSS for the spinner
            const style = document.createElement('style');
            style.textContent = `
                .loading-spinner {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                    opacity: 0;
                    visibility: hidden;
                    transition: opacity 0.3s, visibility 0.3s;
                }
                
                .loading-spinner.show {
                    opacity: 1;
                    visibility: visible;
                }
                
                .loading-spinner .spinner-border {
                    width: 3rem;
                    height: 3rem;
                }
            `;
            document.head.appendChild(style);
        }
    }

    show() {
        const spinner = document.getElementById('global-spinner');
        if (spinner) {
            spinner.classList.add('show');
        }
    }

    hide() {
        const spinner = document.getElementById('global-spinner');
        if (spinner) {
            spinner.classList.remove('show');
        }
    }
}

// Create a global instance
const loadingSpinner = new LoadingSpinner();

// Add AJAX event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Hide spinner when page is fully loaded
    loadingSpinner.hide();
    
    // Show spinner before form submissions
    document.querySelectorAll('form:not([data-no-spinner])').forEach(form => {
        form.addEventListener('submit', function() {
            // Check if global spinner is disabled
            if (typeof window.disableGlobalSpinner === 'undefined' || !window.disableGlobalSpinner) {
                loadingSpinner.show();
            }
        });
    });

    // Add spinner to AJAX requests using jQuery if available
    if (typeof jQuery !== 'undefined') {
        $(document).ajaxStart(function() {
            // Check if global spinner is disabled
            if (typeof window.disableGlobalSpinner === 'undefined' || !window.disableGlobalSpinner) {
                loadingSpinner.show();
            }
        });

        $(document).ajaxStop(function() {
            loadingSpinner.hide();
            // Reset the flag after AJAX completes
            if (typeof window.disableGlobalSpinner !== 'undefined') {
                window.disableGlobalSpinner = false;
            }
        });
    }
    
    // Add spinner to all links except those with data-no-spinner attribute
    document.querySelectorAll('a:not([data-no-spinner])').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't show spinner for links that open in new tab/window or for dropdown toggles
            if (!this.target && this.getAttribute('href') !== '#' && !this.hasAttribute('data-bs-toggle')) {
                // Check if global spinner is disabled
                if (typeof window.disableGlobalSpinner === 'undefined' || !window.disableGlobalSpinner) {
                    // Add a small delay before showing the spinner to prevent flashing for fast loads
                    setTimeout(() => {
                        loadingSpinner.show();
                    }, 100);
                }
            }
        });
    });
});