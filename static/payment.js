document.addEventListener('DOMContentLoaded', function () {
            const cardNumberInput = document.getElementById('card_number');
            const cardNumberMessage = document.getElementById('card_number_validation');
            const form = document.getElementById('payment-form');
            const expirationInput = document.getElementById('expiration');
            const expirationMessage = document.getElementById('expiration_validation');
            const cvvInput = document.getElementById('cvv');
            const cvvMessage = document.getElementById('cvv_validation');

            const showMessage = (element, message, isValid) => {
                element.textContent = message;
                element.classList.remove('hidden');
                element.classList.remove('success-message', 'error-message');
                element.classList.add(isValid ? 'success-message' : 'error-message');
            };

            cardNumberInput.addEventListener('input', function () {
                const cardNumber = cardNumberInput.value;
                const cardNumberPattern = /^\d{16}$/;

                if (cardNumberPattern.test(cardNumber)) {
                    showMessage(cardNumberMessage, "Card number is valid!", true);
                } else {
                    showMessage(cardNumberMessage, "Card number must be 16 digits.", false);
                }
            });

            expirationInput.addEventListener('input', function () {
                const expiration = expirationInput.value;
                const expirationDate = new Date(expiration);
                const currentDate = new Date();

                if (expirationDate >= currentDate) {
                    showMessage(expirationMessage, "Expiration date is valid!", true);
                } else {
                    showMessage(expirationMessage, "Expiration date has expired.", false);
                }
            });

            cvvInput.addEventListener('input', function () {
                const cvv = cvvInput.value;
                const cvvPattern = /^\d{3}$/;

                if (cvvPattern.test(cvv)) {
                    showMessage(cvvMessage, "CVV is valid!", true);
                } else {
                    showMessage(cvvMessage, "CVV must be 3 digits.", false);
                }
            });

            form.addEventListener('submit', function (event) {
                const cardNumber = cardNumberInput.value;
                const cardNumberPattern = /^\d{16}$/;
                const expiration = expirationInput.value;
                const expirationDate = new Date(expiration);
                const currentDate = new Date();
                const cvv = cvvInput.value;
                const cvvPattern = /^\d{3}$/;

                let isValid = true;

                if (!cardNumberPattern.test(cardNumber)) {
                    showMessage(cardNumberMessage, "Card number must be 16 digits.", false);
                    isValid = false;
                } else {
                    showMessage(cardNumberMessage, "Card number is valid!", true);
                }

                if (expirationDate < currentDate) {
                    showMessage(expirationMessage, "Expiration date has expired.", false);
                    isValid = false;
                } else {
                    showMessage(expirationMessage, "Expiration date is valid!", true);
                }

                if (!cvvPattern.test(cvv)) {
                    showMessage(cvvMessage, "CVV must be 3 digits.", false);
                    isValid = false;
                } else {
                    showMessage(cvvMessage, "CVV is valid!", true);
                }

                if (!isValid) {
                    event.preventDefault(); // Prevent form submission
                }
            });
        });