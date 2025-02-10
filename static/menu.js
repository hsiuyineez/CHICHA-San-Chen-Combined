document.addEventListener('DOMContentLoaded', function() {
    function updateCartCount(cartCount) {
        const cartCountElement = document.getElementById('cart-count');
        cartCountElement.textContent = cartCount;
    }

    function displayFlashMessage(message, type) {
        const flashMessageElement = document.getElementById('flash-message');
        flashMessageElement.innerHTML = message;
        flashMessageElement.className = `alert alert-${type}`;
        flashMessageElement.style.display = 'block';

        // Automatically hide the flash message after 3 seconds
        setTimeout(() => {
            flashMessageElement.style.display = 'none';
        }, 3000);
    }

    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const menuInfo = this.closest('.menu-info');
            const itemData = {
                item: menuInfo.querySelector('input[name="name"]').value,
                price: menuInfo.querySelector('input[name="price"]').value,
                base: menuInfo.querySelector('select[name^="base"]').value,
                sugar: menuInfo.querySelector('select[name^="sugar"]').value,
                ice: menuInfo.querySelector('select[name^="ice"]').value,
                size: menuInfo.querySelector('select[name^="size"]').value,
                remark: menuInfo.querySelector('select[name^="remark"]').value,
                quantity: menuInfo.querySelector('input[name^="quantity"]').value
            };

            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemData)
            })
            .then(response => response.json())
            .then(data => {
                updateCartCount(data.cart_count);
                displayFlashMessage('Successfully added to cart', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                displayFlashMessage('An error occurred while adding to cart', 'danger');
            });
        });
    });

    const locationSelect = document.getElementById('location');
    const viewCartButton = document.querySelector('.view-cart');

    // Save selected location to local storage when changed
    locationSelect.addEventListener('change', function() {
        localStorage.setItem('selectedLocation', locationSelect.value);
    });

    // Handle view cart button click
    viewCartButton.addEventListener('click', function(event) {
        const selectedLocation = localStorage.getItem('selectedLocation');
        if (!selectedLocation || selectedLocation === 'Choose a Location') {
            event.preventDefault();
            displayFlashMessage('Please select a location.', 'warning');
        }
    });

    // Retrieve and display the selected location from local storage on page load
    const savedLocation = localStorage.getItem('selectedLocation');
    if (savedLocation && savedLocation !== 'Choose a Location') {
        locationSelect.value = savedLocation;
    }
});