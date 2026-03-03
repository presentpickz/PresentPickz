/**
 * Wishlist Toggle Functionality
 * Handles adding/removing products from wishlist with AJAX
 */

document.addEventListener('DOMContentLoaded', function () {
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    if (!csrfToken) {
        console.error('CSRF token not found!');
        return;
    }

    // Handle all wishlist buttons
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = this.dataset.productId;

            if (!productId) {
                console.error('Product ID not found!');
                return;
            }

            // Disable button during request
            this.disabled = true;

            // Make AJAX request
            fetch(`/users/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    // Update button state
                    if (data.added) {
                        this.classList.add('active');
                        this.setAttribute('aria-label', 'Remove from wishlist');
                        showToast('Added to wishlist ❤️');
                    } else {
                        this.classList.remove('active');
                        this.setAttribute('aria-label', 'Add to wishlist');
                        showToast('Removed from wishlist');
                    }

                    // Update wishlist count in navigation
                    updateWishlistCount(data.count);

                    // Re-enable button
                    this.disabled = false;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error updating wishlist', 'error');
                    this.disabled = false;
                });
        });
    });
});

/**
 * Update wishlist count badge in navigation
 */
function updateWishlistCount(count) {
    const badge = document.querySelector('.wishlist-count');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToast = document.querySelector('.wishlist-toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `wishlist-toast ${type}`;
    toast.textContent = message;

    // Add to page
    document.body.appendChild(toast);

    // Show toast
    setTimeout(() => toast.classList.add('show'), 10);

    // Hide and remove toast
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// Add toast CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .wishlist-toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
    }
    
    .wishlist-toast.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    .wishlist-toast.error {
        background: #e53e3e;
    }
    
    .wishlist-toast.success {
        background: #48bb78;
    }
`;
document.head.appendChild(style);
