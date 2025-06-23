from flask import Blueprint, render_template, request, jsonify
from models.cadastro_avancado import CadastroAvancado
import os

cadastro_bp = Blueprint('cadastro_avancado', __name__,
                        template_folder='templates')


@cadastro_bp.route('/cadastro-obra', methods=['GET'])
def pagina_cadastro():
    """Renderiza a página de cadastro avançado de obras."""
    return render_template('cadastro_avancado.html')


@cadastro_bp.route('/api/consultar-cnpj/<string:cnpj>', methods=['GET'])
def api_consultar_cnpj(cnpj):
    """Endpoint da API para consultar CNPJ."""
    resultado = CadastroAvancado.consultar_cnpj(cnpj)
    if "erro" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado)


@cadastro_bp.route('/api/consultar-cep/<string:cep>', methods=['GET'])
def api_consultar_cep(cep):
    """Endpoint da API para consultar CEP."""
    resultado = CadastroAvancado.consultar_cep(cep)
    if "erro" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado)


@cadastro_bp.route('/api/renomear-pasta', methods=['POST'])
def api_renomear_pasta():
    """
    Endpoint para renomear uma pasta de obra no sistema de arquivos.
    Recebe o caminho antigo e o novo nome da obra.
    """
    dados = request.get_json()
    caminho_antigo = dados.get('caminho_antigo')
    novo_nome_obra = dados.get('novo_nome_obra')

    if not all([caminho_antigo, novo_nome_obra]):
        return jsonify({"erro": "Dados insuficientes para renomear."}), 400

    try:
        # Extrai o diretório pai e constrói o novo caminho
        diretorio_pai = os.path.dirname(caminho_antigo)
        novo_caminho = os.path.join(diretorio_pai, novo_nome_obra)

        # Verifica se o caminho antigo existe e renomeia
        if os.path.exists(caminho_antigo):
            os.rename(caminho_antigo, novo_caminho)
            return jsonify({
                "sucesso": True,
                "mensagem": "Pasta da obra renomeada com sucesso.",
                "novo_caminho": novo_caminho
            })
        else:
            return jsonify({"erro": "O caminho da pasta original não foi encontrado."}), 404

    except OSError as e:
        return jsonify({"erro": f"Erro ao renomear a pasta: {e}"}), 500
