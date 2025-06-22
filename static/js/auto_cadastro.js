document.addEventListener('DOMContentLoaded', function() {
    const cnpjInput = document.getElementById('cnpj');
    const cepInput = document.getElementById('cep');
    
    const cnpjSpinner = document.getElementById('cnpj-spinner');
    const cepSpinner = document.getElementById('cep-spinner');

    if (cnpjInput) {
        cnpjInput.addEventListener('blur', handleCnpjBlur);
    }

    if (cepInput) {
        cepInput.addEventListener('blur', handleCepBlur);
    }

    async function handleCnpjBlur() {
        const cnpj = cnpjInput.value.replace(/\D/g, '');
        if (cnpj.length !== 14) return;

        toggleSpinner(cnpjSpinner, true);
        
        try {
            const response = await fetch('/api/consultar_cnpj', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cnpj: cnpj })
            });
            
            if (!response.ok) throw new Error(`Erro na API: ${response.statusText}`);
            
            const data = await response.json();
            if (data.erro) {
                 alert(`Erro ao consultar CNPJ: ${data.erro}`);
                 return;
            }

            fillFormFields(data);

        } catch (error) {
            console.error('Falha ao buscar CNPJ:', error);
            alert('Não foi possível consultar o CNPJ. Verifique o console para mais detalhes.');
        } finally {
            toggleSpinner(cnpjSpinner, false);
        }
    }

    function fillFormFields(data) {
        // Preencher dados da empresa
        const razaoSocialField = document.getElementById('razao_social');
        if (razaoSocialField) {
            razaoSocialField.value = data.razao_social || '';
        }
        
        // Preencher nome da obra - prioriza Nome Fantasia, fallback para Razão Social
        const nomeObraInput = document.getElementById('nome_fantasia');
        if (nomeObraInput) {
            if (data.nome_fantasia && data.nome_fantasia.trim() !== '') {
                nomeObraInput.value = data.nome_fantasia.trim();
            } else if (data.razao_social && data.razao_social.trim() !== '') {
                nomeObraInput.value = data.razao_social.trim();
            } else {
                nomeObraInput.value = '';
            }
        }
        
        // Preencher dados de endereço
        const enderecoField = document.getElementById('endereco');
        if (enderecoField) {
            enderecoField.value = data.logradouro || '';
        }
        
        const numeroField = document.getElementById('numero');
        if (numeroField) {
            // Remove pontos e vírgulas do número se existirem
            const numero = (data.numero || '').replace(/[.,]/g, '');
            numeroField.value = numero;
        }
        
        const bairroField = document.getElementById('bairro');
        if (bairroField) {
            bairroField.value = data.bairro || '';
        }
        
        const cidadeField = document.getElementById('cidade');
        if (cidadeField) {
            cidadeField.value = data.municipio || '';
        }
        
        const ufField = document.getElementById('uf');
        if (ufField) {
            ufField.value = data.uf || '';
        }
        
        // Preencher CEP
        const cepField = document.getElementById('cep');
        if (cepField) {
            const cep = (data.cep || '').replace(/\D/g, '');
            cepField.value = cep;
        }
        
        // Mostrar feedback visual de sucesso
        showSuccessMessage('Dados da empresa carregados com sucesso!');
    }

    function showSuccessMessage(message) {
        // Remove mensagem anterior se existir
        const existingMessage = document.querySelector('.alert-success-auto');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Cria nova mensagem de sucesso
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-success-auto mt-2';
        successDiv.innerHTML = `
            <i class="bi bi-check-circle"></i> ${message}
        `;
        
        // Insere a mensagem após o campo CNPJ
        const cnpjContainer = cnpjInput.closest('.col-md-4');
        if (cnpjContainer) {
            cnpjContainer.appendChild(successDiv);
            
            // Remove a mensagem após 5 segundos
            setTimeout(() => {
                if (successDiv.parentNode) {
                    successDiv.remove();
                }
            }, 5000);
        }
    }

    async function handleCepBlur() {
        const cep = cepInput.value.replace(/\D/g, '');
        if (cep.length !== 8) return;

        toggleSpinner(cepSpinner, true);

        try {
            const response = await fetch('/api/consultar_cep', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cep: cep })
            });

            if (!response.ok) throw new Error(`Erro na API: ${response.statusText}`);
            
            const data = await response.json();
            if (data.erro) {
                alert('CEP não encontrado.');
                return;
            }

            document.getElementById('endereco').value = data.logradouro || '';
            document.getElementById('bairro').value = data.bairro || '';
            document.getElementById('cidade').value = data.localidade || '';
            document.getElementById('uf').value = data.uf || '';
            
            document.getElementById('numero').focus();

        } catch (error) {
            console.error('Falha ao buscar CEP:', error);
            alert('Não foi possível consultar o CEP. Verifique o console para mais detalhes.');
        } finally {
            toggleSpinner(cepSpinner, false);
        }
    }
    
    function toggleSpinner(spinner, show) {
        if (spinner) {
            spinner.classList.toggle('d-none', !show);
        }
    }
}); 