import requests

class EmpresaAPI:
    """
    Classe utilitária para interagir com APIs externas de consulta de CNPJ e CEP.
    """

    def get_dados_cnpj(self, cnpj: str):
        """
        Consulta os dados de um CNPJ na BrasilAPI.

        Args:
            cnpj (str): O CNPJ a ser consultado (pode conter pontuação).

        Returns:
            dict: Um dicionário com os dados da empresa ou um dicionário de erro.
        """
        if not cnpj:
            return {"erro": "CNPJ não fornecido."}

        # Limpa o CNPJ para conter apenas dígitos
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))

        if len(cnpj_limpo) != 14:
            return {"erro": "CNPJ inválido. Deve conter 14 dígitos."}

        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao consultar BrasilAPI para CNPJ {cnpj_limpo}: {e}")
            return {"erro": f"Falha na comunicação com a API de CNPJ: {e}"}

    def get_endereco_cep(self, cep: str):
        """
        Consulta os dados de um CEP na ViaCEP.

        Args:
            cep (str): O CEP a ser consultado (pode conter pontuação).

        Returns:
            dict: Um dicionário com os dados do endereço ou um dicionário de erro.
        """
        if not cep:
            return {"erro": "CEP não fornecido."}

        # Limpa o CEP para conter apenas dígitos
        cep_limpo = "".join(filter(str.isdigit, cep))

        if len(cep_limpo) != 8:
            return {"erro": "CEP inválido. Deve conter 8 dígitos."}

        try:
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("erro"):
                return {"erro": "CEP não encontrado."}
            return data
        except requests.RequestException as e:
            print(f"Erro ao consultar ViaCEP para CEP {cep_limpo}: {e}")
            return {"erro": f"Falha na comunicação com a API de CEP: {e}"} 