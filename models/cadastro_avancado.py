import requests

class CadastroAvancado:
    """
    Classe de modelo para interagir com APIs externas para auto-preenchimento.
    """
    BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{}"
    VIACEP_URL = "https://viacep.com.br/ws/{}/json/"

    @staticmethod
    def consultar_cnpj(cnpj):
        """
        Consulta um CNPJ na BrasilAPI.
        Retorna um dicionário com os dados ou um dicionário de erro.
        """
        try:
            # Limpa o CNPJ para conter apenas números
            cnpj_limpo = "".join(filter(str.isdigit, cnpj))
            if len(cnpj_limpo) != 14:
                return {"erro": "CNPJ inválido. Deve conter 14 dígitos."}

            response = requests.get(CadastroAvancado.BRASIL_API_URL.format(cnpj_limpo), timeout=5)
            response.raise_for_status()  # Lança exceção para códigos de erro HTTP
            return response.json()
        except requests.Timeout:
            return {"erro": "A consulta ao CNPJ demorou muito para responder (timeout)."}
        except requests.RequestException as e:
            return {"erro": f"Falha ao consultar CNPJ: {e}"}

    @staticmethod
    def consultar_cep(cep):
        """
        Consulta um CEP na API ViaCEP.
        Retorna um dicionário com os dados ou um dicionário de erro.
        """
        try:
            # Limpa o CEP para conter apenas números
            cep_limpo = "".join(filter(str.isdigit, cep))
            if len(cep_limpo) != 8:
                return {"erro": "CEP inválido. Deve conter 8 dígitos."}

            response = requests.get(CadastroAvancado.VIACEP_URL.format(cep_limpo), timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data.get("erro"):
                return {"erro": "CEP não encontrado."}
            return data
        except requests.Timeout:
            return {"erro": "A consulta ao CEP demorou muito para responder (timeout)."}
        except requests.RequestException as e:
            return {"erro": f"Falha ao consultar CEP: {e}"} 