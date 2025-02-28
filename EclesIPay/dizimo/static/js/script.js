document.addEventListener('DOMContentLoaded', function() {


    document.getElementById('salvarParoquia').addEventListener('click', async () => {
        const select = document.getElementById('paroquiaSelect');
        const selectedParoquia = select.options[select.selectedIndex];
        
        try {
            const response = await fetch('/atualizar-paroquia/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    paroquia_id: select.value
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                document.getElementById('paroquiaAtual').textContent = selectedParoquia.text;
                //dropdown.style.display = 'none';
            } else {
                alert('Erro ao atualizar paróquia: ' + data.message);
            }
        } catch (error) {
            //console.error('Erro:', error);
            //alert('Erro na comunicação com o servidor');
            console.log(error)
        }
    });

    // Função para pegar o cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

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
    
    // Funcionalidade para mudar paróquia
    const mudarParoquiaBtn = document.getElementById('mudarParoquia');
    const salvarParoquiaBtn = document.getElementById('salvarParoquia');
    const cancelarParoquiaBtn = document.getElementById('cancelarParoquia');
    const paroquiaDropdown = document.getElementById('paroquiaDropdown');
    
    if (mudarParoquiaBtn) {
        mudarParoquiaBtn.addEventListener('click', function() {
            paroquiaDropdown.style.display = 'block';
            mudarParoquiaBtn.style.display = 'none';
        });
    }
    
    if (cancelarParoquiaBtn) {
        cancelarParoquiaBtn.addEventListener('click', function() {
            paroquiaDropdown.style.display = 'none';
            mudarParoquiaBtn.style.display = 'inline-block';
        });
    }
    
    if (salvarParoquiaBtn) {
        salvarParoquiaBtn.addEventListener('click', function() {
            const paroquiaSelect = document.getElementById('paroquiaSelect');
            const paroquiaId = paroquiaSelect.value;
            const paroquiaText = paroquiaSelect.options[paroquiaSelect.selectedIndex].text;
            
            // Enviar a alteração para o servidor via AJAX
            fetch('/atualizar-paroquia/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ paroquia_id: paroquiaId })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Erro ao atualizar paróquia');
            })
            .then(data => {
                // Atualizar a interface do usuário
                document.getElementById('paroquiaAtual').textContent = paroquiaText;
                paroquiaDropdown.style.display = 'none';
                mudarParoquiaBtn.style.display = 'inline-block';
                showMessage('Paróquia atualizada com sucesso!', 'success');
            })
            .catch(error => {
                console.error('Erro:', error);
                showMessage('Erro ao atualizar paróquia. Tente novamente.', 'error');
            });
        });
    }
    
    // Função auxiliar para obter o token CSRF
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length, cookie.length);
            }
        }
        return null;
    }
});