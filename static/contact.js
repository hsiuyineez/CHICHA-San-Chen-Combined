document.addEventListener('DOMContentLoaded', function () {
        const phoneInput = document.getElementById('phone');
        const phoneMessage = document.getElementById('phone-message');
        const form = document.getElementById('contact');
        const dateInput = document.getElementById('date');

        // Set max attribute on date input to today's date
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('max', today);

        phoneInput.addEventListener('input', function () {
            const phone = phoneInput.value;
            const phonePattern = /^[689][0-9]{7}$/; // Phone number must be 8 digits long and start with 6, 8, or 9

            if (phonePattern.test(phone)) {
                phoneMessage.textContent = "Phone number is valid!";
                phoneMessage.classList.remove('invalid');
                phoneMessage.classList.add('valid');
                phoneMessage.style.display = 'block';
            } else {
                phoneMessage.textContent = "Phone number must be 8 digits long and start with 6, 8, or 9.";
                phoneMessage.classList.remove('valid');
                phoneMessage.classList.add('invalid');
                phoneMessage.style.display = 'block';
            }
        });

        form.addEventListener('submit', function (event) {
            const phone = phoneInput.value;
            const phonePattern = /^[689][0-9]{7}$/;

            let isValid = true;

            if (!phonePattern.test(phone)) {
                phoneMessage.textContent = "Phone number must be 8 digits long and start with 6, 8, or 9.";
                phoneMessage.classList.remove('valid');
                phoneMessage.classList.add('invalid');
                phoneMessage.style.display = 'block';
                isValid = false;
            } else {
                phoneMessage.textContent = "Phone number is valid!";
                phoneMessage.classList.remove('invalid');
                phoneMessage.classList.add('valid');
                phoneMessage.style.display = 'block';
            }

            if (!isValid) {
                event.preventDefault(); // Prevent form submission
            }
        });
    });