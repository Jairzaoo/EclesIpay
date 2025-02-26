document.addEventListener('DOMContentLoaded', function() {
    // Add direct handler for the signup link
    const signupLink = document.getElementById('signup-link');
    if (signupLink) {
        signupLink.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href) {
                window.location.href = href;
            }
        });
    }
    
    // Validação de formulário
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input, select');
            let isValid = true;

            inputs.forEach(input => {
                if(!input.checkValidity()) {
                    input.style.borderColor = 'red';
                    isValid = false;
                }
            });

            if(!isValid) {
                e.preventDefault();
                showMessage('Por favor, preencha todos os campos obrigatórios!', 'error');
            }
        });
    });

    function showMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = `message ${type}`;
        msg.textContent = text;
        
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 3000);
    }
});