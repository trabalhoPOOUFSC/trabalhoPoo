from datetime import date
import pickle
from abc import ABC, abstractmethod
import PySimpleGUI as sg


class EntidadeNaoEncontradaException(Exception):
    def __init__(self, entidade: str = "", id_entidade=None, mensagem: str = ""):
        self.entidade = entidade
        self.id_entidade = id_entidade
        
        if not mensagem:
            if id_entidade is not None:
                mensagem = f"{entidade} com ID {id_entidade} não encontrada"
            else:
                mensagem = f"{entidade} não encontrada" if entidade else "Entidade não encontrada"
                
        super().__init__(mensagem)

class DadoInvalidoException(Exception):
    def __init__(self, campo: str = "", valor=None, mensagem: str = ""):
        self.campo = campo
        self.valor = valor

        if valor and campo:
            mensagem = f"Valor inválido para {campo}: {valor}. {mensagem}"
        elif campo:
            mensagem = f"Dado inválido: {campo}. {mensagem}"
        else:
            mensagem = mensagem if mensagem else "Dado inválido"
                
        super().__init__(mensagem)

class CampoObrigatorioException(Exception):
    def __init__(self, campo: str):
        mensagem = f"{campo} é obrigatório e não pode ser vazio"
        super().__init__(mensagem)

class ViolacaoRegraNegocioException(Exception):
    def __init__(self, mensagem: str = "Violação de regra de negócio!"):
        super().__init__(mensagem)

class DAO(ABC):
    @abstractmethod
    def __init__(self, datasource=''):
        self.__datasource = datasource
        self.__cache = {}
        try:
            self.__load()
        except FileNotFoundError:
            self.__dump()

    def __dump(self):
        pickle.dump(self.__cache, open(self.__datasource, 'wb'))

    def __load(self):
        self.__cache = pickle.load(open(self.__datasource,'rb'))

    def add(self, key, obj):
        self.__cache[key] = obj
        self.__dump()

    def update(self, key, obj):
        try:
            if(self.__cache[key] != None):
                self.__cache[key] = obj
                self.__dump()
        except KeyError:
            pass

    def get(self, key):
        try:
            return self.__cache[key]
        except KeyError:
            pass

    def remove(self, key):
        try:
            self.__cache.pop(key)
            self.__dump()
        except KeyError:
            pass

    def get_all(self):
        return self.__cache.values()

class Pessoa(ABC):
    @abstractmethod
    def __init__(self, id, nome, contato):
        if not isinstance(id, int):
            raise TypeError("id deve ser int")
        if not isinstance(nome, str):
            raise TypeError("nome deve ser str")
        if not isinstance(contato, str):
            raise TypeError("contato deve ser str")
        self.__id = id
        self.__nome = nome
        self.__contato = contato

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError("id deve ser int")
        self.__id = value

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, value):
        if not isinstance(value, str):
            raise TypeError("nome deve ser str")
        self.__nome = value

    @property
    def contato(self):
        return self.__contato

    @contato.setter
    def contato(self, value):
        if not isinstance(value, str):
            raise TypeError("contato deve ser str")
        self.__contato = value

class Afiliado(Pessoa):
    def __init__(self, id, nome, contato, parent=None):
        super().__init__(id, nome, contato)
        if parent is not None and not isinstance(parent, Afiliado):
            raise TypeError("Coloque o id de um afiliado ou nada para não ter afiliado 'pai'.")
        self.__parent = parent
        self.__vendas = []

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        if value is not None and not isinstance(value, Afiliado):
            raise TypeError("Coloque o id de um afiliado ou nada para não ter afiliado 'pai'.")
        self.__parent = value

    @property
    def vendas(self):
        return self.__vendas

    @vendas.setter
    def vendas(self, value):
        if not isinstance(value, list):
            raise TypeError("vendas deve ser uma lista de Venda")
        for item in value:
            if not isinstance(item, Venda):
                raise TypeError("Cada item em vendas deve ser do tipo Venda")
        self.__vendas = value

class AfiliadoDAO(DAO):
    def __init__(self):
        super().__init__('afiliado.pkl')
    
    def add(self, afiliado: Afiliado):
        if((afiliado is not None) and isinstance(afiliado, Afiliado) and isinstance(afiliado.id, int)):
            super().add(afiliado.id, afiliado)
    
    def update(self, afiliado: Afiliado):
        if((afiliado is not None) and isinstance(afiliado, Afiliado) and isinstance(afiliado.id, int)):
            super().update(afiliado.id, afiliado)

    def get(self, key:int):
        if isinstance(key, int):
            return super().get(key)

    def remove(self, key:int):
        if(isinstance(key, int)):
            return super().remove(key)

class TelaAfiliado:
    def __init__(self):
        self.__window = None

    def init_components(self):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Escolha uma opção', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Cadastrar afiliado', "RD1", default=False, key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Listar afiliados', "RD1", default=False, key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Modificar afiliado', "RD1", default=False, key='3', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Excluir afiliado', "RD1", default=False, key='4', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), 
            sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(10,1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]
        self.__window = sg.Window('Menu de Afiliado').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):
        botao, opc = self.__window.Read()
        return botao, opc

    def ler_dados(self):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Incluir Novo Afiliado', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('Id', size=(15, 1), font=('Helvetica', 12)), sg.InputText(key='id', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Nome', size=(15, 1), font=('Helvetica', 12)), sg.InputText(key='nome', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Contato', size=(15, 1), font=('Helvetica', 12)), sg.InputText(key='contato', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Parent ID', size=(15, 1), font=('Helvetica', 12)), sg.InputText(key='parent', font=('Helvetica', 12), size=(30, 1))],
            [sg.HorizontalSeparator(pad=(5, 15))],
            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]

        window = sg.Window('Cadastro de Afiliado', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def mostrar_afiliado(self, lista_afiliados):
        texto = "=== Lista de Afiliados ===\n\n"
        for info in lista_afiliados:
            parent_id = info['parent']
            if parent_id is None:
                parent_id = 'Nenhum'
            texto += f"ID: {info['id']} | Nome: {info['nome']} | Contato: {info['contato']} | Parent ID: {parent_id}\n"

        sg.theme('DarkBlue14')
        layout = [
            [sg.Multiline(texto, size=(60, len(lista_afiliados) + 6), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Afiliados Cadastrados", layout)
        window.read()
        window.close()

    def selecionar_afiliado(self, titulo: str):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text(titulo)],
            [sg.Text('ID do Afiliado:'), sg.InputText(key='id')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]
        window = sg.Window('Selecionar Afiliado', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values['id']

    def modificar_dados(self, afiliado_data):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Modificar Afiliado', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('ID Atual:', size=(15, 1), font=('Helvetica', 12)), 
            sg.Text(str(afiliado_data['id']), key='id_atual', font=('Helvetica', 12))],
            [sg.Text('Novo ID:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(str(afiliado_data['id']), key='id', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Nome:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(afiliado_data['nome'], key='nome', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Contato:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(afiliado_data['contato'], key='contato', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Parent ID:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(str(afiliado_data['parent']) if afiliado_data['parent'] else '', key='parent', font=('Helvetica', 12), size=(30, 1))],
            [sg.HorizontalSeparator(pad=(5, 15))],

            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]

        window = sg.Window('Modificar Afiliado', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def confirmar_exclusao(self, afiliado_data):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text(f'Confirmar exclusão do afiliado?')],
            [sg.Text(f'ID: {afiliado_data["id"]}')],
            [sg.Text(f'Nome: {afiliado_data["nome"]}')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]
        window = sg.Window('Confirmar Exclusão', layout)
        botao, _ = window.read()
        window.close()
        return botao == 'Confirmar'

    def mostrar_mensagem_popup(self, mensagem):
        sg.popup(mensagem)

class ControllerAfiliado:
    def __init__(self, tela):
        self.__tela = tela
        self.__afiliado_DAO = AfiliadoDAO()

    @property
    def afiliado_DAO (self):
        return self.__afiliado_DAO

    def executar(self):
        self.__tela.init_components()
        while True:
            botao, opc = self.__tela.mostrar_menu()
            if botao == 'Confirmar':
                self.__tela.close()
                if opc['1'] == True:
                    self.__cadastrar()
                elif opc['2'] == True:
                    self.__listar()
                elif opc['3'] == True:
                    self.__modificar()
                elif opc['4'] == True:
                    self.__excluir()
                else:
                    self.__tela.opcao_invalida()
                self.__tela.init_components()
            elif botao == 'Cancelar':
                self.__tela.close()
                break
            
    def __cadastrar(self):
        while True:
            try:
                dados = self.__tela.ler_dados()
                if dados is None:
                    break

                id = dados['id']
                nome = dados['nome']
                contato = dados['contato']
                parent_id = dados['parent']
                try:
                    id = int(dados['id'])
                except ValueError:
                    raise DadoInvalidoException("Id", dados['id'], "Id deve ser um inteiro!")
                if parent_id:
                    try:
                        parent_id = int(dados['parent'])
                    except ValueError:
                        raise DadoInvalidoException("Id Afiliado Pai", dados['parent'], "Id deve ser um inteiro!")

                parent = None
                for a in self.__afiliado_DAO.get_all():
                    if a.id == id:
                        raise DadoInvalidoException("Id", id, "ID já existe")
                    if parent_id and a.id == parent_id:
                        parent = a

                if parent_id and not parent:
                    raise sg.popup(EntidadeNaoEncontradaException("Afiliado", parent_id))

                afiliado = Afiliado(id, nome, contato, parent)
                self.__afiliado_DAO.add(afiliado)

                self.__tela.mostrar_mensagem_popup("Afiliado cadastrado com sucesso!")

                break
            except Exception as e:
                self.__tela.mostrar_mensagem_popup(f"Erro ao cadastrar afiliado: {e}")
            

    def __listar(self):
        afiliados = self.__afiliado_DAO.get_all()
        if not afiliados:
            sg.popup(EntidadeNaoEncontradaException("Afiliado"))
        else:
            lista_afiliados = []
            for a in afiliados:
                if a.parent is None:
                    info = {'id': a.id, 'nome': a.nome, 'contato': a.contato, 'parent': None}
                else:
                    info = {'id': a.id, 'nome': a.nome, 'contato': a.contato, 'parent': a.parent.id}
                lista_afiliados.append(info)
            self.__tela.mostrar_afiliado(lista_afiliados)

    def __modificar(self):
        try:
            id_str = self.__tela.selecionar_afiliado("Digite o ID do afiliado para modificar")
            if not id_str: return
            id = int(id_str)
            
            afiliado = self.__afiliado_DAO.get(id)
            if not afiliado:
                raise EntidadeNaoEncontradaException("Afiliado", id)
            
            afiliado_data = {
                'id': afiliado.id,
                'nome': afiliado.nome,
                'contato': afiliado.contato,
                'parent': afiliado.parent.id if afiliado.parent else None
            }

            dados = self.__tela.modificar_dados(afiliado_data)
            if not dados: return

            novo_id = dados['id']
            nome = dados['nome']
            contato = dados['contato']
            parent_id = dados['parent']
            try:
                novo_id = int(dados['id'])
            except ValueError:
                raise DadoInvalidoException("Id", dados['id'], "Id deve ser um inteiro!")
            if parent_id:
                try:
                    parent_id = int(dados['parent'])
                except ValueError:
                    raise DadoInvalidoException("Id Afiliado Pai", dados['parent'], "Id deve ser um inteiro!")

            if novo_id != id and self.__afiliado_DAO.get(novo_id):
                raise DadoInvalidoException("ID", novo_id, "ID já existe")

            afiliado.id = novo_id
            afiliado.nome = nome
            afiliado.contato = contato

            if parent_id:
                parent = self.__afiliado_DAO.get(parent_id)
                if not parent:
                    raise EntidadeNaoEncontradaException("Afiliado", parent_id)
                afiliado.parent = parent
            else:
                afiliado.parent = None

            self.__afiliado_DAO.update(afiliado)

            self.__tela.mostrar_mensagem_popup("Afiliado modificado com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao modificar afiliado: {e}")

    def __excluir(self):
        try:
            id_str = self.__tela.selecionar_afiliado("Digite o ID do afiliado para excluir")
            if not id_str: return
            id = int(id_str)
            
            afiliado = self.__afiliado_DAO.get(id)
            if not afiliado:
                raise EntidadeNaoEncontradaException("Afiliado", id)

            for a in self.__afiliado_DAO.get_all():
                if a.parent and a.parent.id == id:
                    raise ViolacaoRegraNegocioException(
                        f"Não é possível excluir {afiliado.nome} pois é parente de outros afiliados"
                    )
                
            dados_afiliado = {
                "id": afiliado.id,
                "nome": afiliado.nome
            }

            if not self.__tela.confirmar_exclusao(dados_afiliado):
                return

            self.__afiliado_DAO.remove(id)
            self.__tela.mostrar_mensagem_popup("Afiliado excluído com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao excluir afiliado: {e}")

class ProdutoDetalhes:
    def __init__(self, nome, descricao):
        self.__nome = nome
        self.__descricao = descricao

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, value):
        if not isinstance(value, str):
            raise TypeError("nome deve ser str")
        self.__nome = value

    @property
    def descricao(self):
        return self.__descricao

    @descricao.setter
    def descricao(self, value):
        if not isinstance(value, str):
            raise TypeError("descricao deve ser str")
        self.__descricao = value

class Produto:
    def __init__(self, codigo, nome, descricao, preco):
        if not isinstance(codigo, str):
            raise TypeError("codigo deve ser str")
        if not isinstance(nome, str):
            raise TypeError("nome deve ser str")
        if not isinstance(descricao, str):
            raise TypeError("descricao deve ser str")
        if not isinstance(preco, (int, float)):
            raise TypeError("preco deve ser numérico")
        self.__codigo = codigo
        self.__detalhes = ProdutoDetalhes(nome, descricao)
        self.__preco = float(preco)

    @property
    def codigo(self):
        return self.__codigo

    @codigo.setter
    def codigo(self, value):
        if not isinstance(value, str):
            raise TypeError("codigo deve ser str")
        self.__codigo = value

    @property
    def detalhes(self):
        return self.__detalhes

    @detalhes.setter
    def detalhes(self, value):
        if not isinstance(value, ProdutoDetalhes):
            raise TypeError("detalhes deve ser do tipo ProdutoDetalhes")
        self.__detalhes = value

    @property
    def preco(self):
        return self.__preco

    @preco.setter
    def preco(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("preco deve ser numérico")
        self.__preco = float(value)

class ProdutoDAO(DAO):
    def __init__(self):
        super().__init__('produto.pkl')
    
    def add(self, produto: Produto):
        if((produto is not None) and isinstance(produto, Produto) and isinstance(produto.codigo, str)):
            super().add(produto.codigo, produto)
    
    def update(self, produto: Produto):
        if((produto is not None) and isinstance(produto, Produto) and isinstance(produto.codigo, str)):
            super().update(produto.codigo, produto)

    def get(self, key:str):
        if isinstance(key, str):
            return super().get(key)

    def remove(self, key:str):
        if(isinstance(key, str)):
            return super().remove(key)

class TelaProduto:
    def __init__(self):
        self.__window = None

    def init_components(self):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Escolha uma opção', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Cadastrar produto', "RD1", default=False, key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Listar produtos', "RD1", default=False, key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Modificar produto', "RD1", default=False, key='3', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Excluir produto', "RD1", default=False, key='4', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')),
            sg.Button('Cancelar', size=(10,1), button_color=('white', 'firebrick3')), sg.Push()]
        ]
        self.__window = sg.Window('Menu de Produtos').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):
        botao, opc = self.__window.Read()
        return botao, opc

    def ler_dados(self):
        sg.theme('DarkBlue14')
        layout = [
        [sg.Text('Incluir Novo Produto', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
        [sg.Text('Código:', size=(15, 1), font=('Helvetica', 10)), sg.InputText(key='codigo', font=('Helvetica', 10), size=(30, 1))],
        [sg.Text('Nome:', size=(15, 1), font=('Helvetica', 10)), sg.InputText(key='nome', font=('Helvetica', 10), size=(30, 1))],
        [sg.Text('Descrição:', size=(15, 1), font=('Helvetica', 10)), sg.InputText(key='descricao', font=('Helvetica', 10), size=(30, 1))],
        [sg.Text('Preço:', size=(15, 1), font=('Helvetica', 10)), sg.InputText(key='preco', font=('Helvetica', 10), size=(30, 1))],

        [sg.HorizontalSeparator(pad=(5, 15))],

        [sg.Push(), 
         sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
         sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
         sg.Push()]
    ]

        window = sg.Window('Cadastro de Produto', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def mostrar_produto(self, lista_produtos):
        texto = "=== Lista de Produtos ===\n\n"
        for info in lista_produtos:
            texto += f"Código: {info['codigo']} | Nome: {info['nome']} | Descrição: {info['descricao']} | Preço: {info['preco']}\n"

        layout = [
            [sg.Multiline(texto, size=(60, len(lista_produtos) + 6), disabled=True)],
            [sg.Button("Fechar", size=(7, 1), button_color=('white', 'firebrick3'))]
        ]

        window = sg.Window("Produtos Cadastrados", layout)
        window.read()
        window.close()

    def selecionar_produto(self, titulo: str):
        layout = [
            [sg.Text(titulo)],
            [sg.Text('Código do Produto:'), sg.InputText(key='codigo')],
            [sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3'))]
        ]
        window = sg.Window('Selecionar Produto', layout)
        botao, values = window.read()
        window.close()

        return None if botao == 'Cancelar' else values['codigo']

    def modificar_dados(self, produto_data):
        layout = [
            [sg.Text('Modificar Produto', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('Código atual:', size=(15, 1), font=('Helvetica', 12)), 
            sg.Text(str(produto_data['codigo']), key='codigo_atual', font=('Helvetica', 12))],
            [sg.Text('Nome:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(produto_data['nome'], key='nome', font=('Helvetica', 12), size=(40, 1))],
            [sg.Text('Descrição:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(produto_data['descricao'], key='descricao', font=('Helvetica', 12), size=(40, 1))],
            [sg.Text('Preço:', size=(15, 1), font=('Helvetica', 12)), 
            sg.InputText(str(produto_data['preco']), key='preco', font=('Helvetica', 12), size=(40, 1))],
            [sg.HorizontalSeparator(pad=(5, 15))],

            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]

        window = sg.Window('Modificar Produto', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def confirmar_exclusao(self, produto_data):
        layout = [
            [sg.Text(f'Confirmar exclusão do produto?')],
            [sg.Text(f'Código: {produto_data["codigo"]}')],
            [sg.Text(f'Nome: {produto_data["nome"]}')],
            [sg.Push(), 
            sg.Button('Confirmar', size=(9, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(9, 1), button_color=('white', 'firebrick3')),
            sg.Push()]
        ]
        window = sg.Window('Confirmar Exclusão', layout)
        botao, _ = window.read()
        window.close()
        return botao == 'Confirmar'
    
    def mostrar_mensagem_popup(self, mensagem):
        sg.popup(mensagem)

class ControllerProduto:
    def __init__(self, tela):
        self.__tela = tela
        self.__produto_DAO = ProdutoDAO()
        self.__controller_venda = None  # Será injetado posteriormente

    def set_controller_venda(self, controller_venda):
        self.__controller_venda = controller_venda

    @property
    def produto_DAO(self):
        return self.__produto_DAO

    @produto_DAO.setter
    def produto_DAO(self, value):
        if not isinstance(value, list):
            raise TypeError("listaProdutos deve ser uma lista de Produto")
        for item in value:
            if not isinstance(item, Produto):
                raise TypeError("Cada item em listaProdutos deve ser do tipo Produto")
        self.__produto_DAO = value

    def executar(self):
        self.__tela.init_components()
        while True:
            botao, opc = self.__tela.mostrar_menu()
            if botao == 'Confirmar':
                self.__tela.close()
                if opc['1'] == True:
                    self.__cadastrar()
                elif opc['2'] == True:
                    self.__listar()
                elif opc['3'] == True:
                    self.__modificar()
                elif opc['4'] == True:
                    self.__excluir()
                else:
                    self.__tela.opcao_invalida()
                self.__tela.init_components()
            elif botao == 'Cancelar':
                self.__tela.close()
                break

    def __cadastrar(self):
        while True:
            try:
                dados = self.__tela.ler_dados()
                if dados is None:
                    break

                codigo = str(dados['codigo'])
                nome = str(dados['nome'])
                descricao = str(dados['descricao'])
                preco = dados['preco']
                try:
                    preco = float(dados['preco'])
                except ValueError:
                    raise DadoInvalidoException("Preço", dados['preco'], "Preço deve ser numérico")

                for item in self.__produto_DAO.get_all():
                    if item.codigo == dados['codigo']:
                        raise DadoInvalidoException("Código", dados['codigo'], "Código já existe")

                produto = Produto(codigo, nome, descricao, preco)
                self.__produto_DAO.add(produto)
                self.__tela.mostrar_mensagem_popup("Produto cadastrado com sucesso!")
                
                break
            except Exception as e:
                self.__tela.mostrar_mensagem_popup(f"Erro ao cadastrar Produto: {e}")

    def __listar(self):
        produtos = self.__produto_DAO.get_all()
        if not produtos:
            sg.popup(EntidadeNaoEncontradaException("Produto"))
        else:
            lista_produtos = []
            for p in produtos:
                info = {'codigo': p.codigo, 'nome': p.detalhes.nome, 'descricao': p.detalhes.descricao, 'preco': p.preco}
                lista_produtos.append(info)
            self.__tela.mostrar_produto(lista_produtos)

    def __modificar(self):
        try:
            codigo = self.__tela.selecionar_produto("Digite o Código do produto para modificar")
            if not codigo: return

            produto = None

            produto = self.__produto_DAO.get(codigo)
            if not produto:
                raise EntidadeNaoEncontradaException("Produto", codigo)
            produto_data = {
                'codigo': produto.codigo,
                'nome': produto.detalhes.nome,
                'descricao': produto.detalhes.descricao,
                'preco': produto.preco
            }
            dados = self.__tela.modificar_dados(produto_data)
            if not dados:
                return

            nome = dados['nome']
            descricao = dados['descricao']
            preco = dados['preco']
            try:
                preco = float(dados['preco'])
            except ValueError:
                raise DadoInvalidoException("Preço", dados['preco'], "Preço deve ser numérico")

            produto.detalhes.nome = nome
            produto.detalhes.descricao = descricao
            produto.preco = preco
            
            self.__produto_DAO.update(produto)

            self.__tela.mostrar_mensagem_popup("Produto modificado com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao modificar produto: {e}")

    def __excluir(self):
        try:
            codigo = self.__tela.selecionar_produto("Digite o Código do produto para modificar")
            if not codigo: return
            produto = None

            produto = self.__produto_DAO.get(codigo)
            if not produto:
                raise EntidadeNaoEncontradaException("Produto", codigo)

            tem_venda = False
            if self.__controller_venda:
                for venda in self.__controller_venda.venda_DAO.get_all():
                    if venda.produto == produto:
                        tem_venda = True
                        break
            
            if tem_venda:
                raise ViolacaoRegraNegocioException(
                    "Produto está vinculado a vendas e não pode ser excluído"
                )
            
            dados_produto = {
                "codigo": produto.codigo,
                "nome": produto.detalhes.nome
            }
            if not self.__tela.confirmar_exclusao(dados_produto):
                return
            
            self.__produto_DAO.remove(codigo)

            self.__tela.mostrar_mensagem_popup("Produto excluído com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao excluir produto: {e}")

class Venda:
    def __init__(self, id, data, afiliado, produto, quantidade):
        if not isinstance(id, int):
            raise TypeError("id deve ser int")
        if not isinstance(data, date):
            raise TypeError("data deve ser do tipo date")
        if not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        if not isinstance(produto, Produto):
            raise TypeError("produto deve ser do tipo Produto")
        if not isinstance(quantidade, int):
            raise TypeError("quantidade deve ser int")
        self.__id = id
        self.__data = data
        self.__afiliado = afiliado
        self.__produto = produto
        self.__quantidade = quantidade
        self.__total = self.calcularTotal()
        self.__pagamento_afiliado = 'não realizado'

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError("id deve ser int")
        self.__id = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if not isinstance(value, date):
            raise TypeError("data deve ser do tipo date")
        self.__data = value

    @property
    def afiliado(self):
        return self.__afiliado

    @afiliado.setter
    def afiliado(self, value):
        if not isinstance(value, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        self.__afiliado = value

    @property
    def produto(self):
        return self.__produto

    @produto.setter
    def produto(self, value):
        if not isinstance(value, Produto):
            raise TypeError("produto deve ser do tipo Produto")
        self.__produto = value
        self.calcularTotal()

    @property
    def quantidade(self):
        return self.__quantidade

    @quantidade.setter
    def quantidade(self, value):
        if not isinstance(value, int):
            raise TypeError("quantidade deve ser int")
        self.__quantidade = value
        self.calcularTotal()

    @property
    def total(self):
        return self.__total

    @total.setter
    def total(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("total deve ser numérico")
        self.__total = float(value)

    @property
    def pagamento_afiliado(self):
        return self.__pagamento_afiliado

    @pagamento_afiliado.setter
    def pagamento_afiliado(self, value):
        if value not in ('não realizado', 'aguardando confirmação', 'realizado'):
            raise ValueError("pagamento_afiliado deve ser 'não realizado', 'aguardando confirmação' ou 'realizado'")
        self.__pagamento_afiliado = value

    def calcularTotal(self):
        self.__total = self.quantidade * self.produto.preco
        return self.__total
    
class VendaDAO(DAO):
    def __init__(self):
        super().__init__('venda.pkl')
    
    def add(self, venda: Venda):
        if((venda is not None) and isinstance(venda, Venda) and isinstance(venda.id, int)):
            super().add(venda.id, venda)
    
    def update(self, venda: Venda):
        if((venda is not None) and isinstance(venda, Venda) and isinstance(venda.id, int)):
            super().update(venda.id, venda)

    def get(self, key:int):
        if isinstance(key, int):
            return super().get(key)

    def remove(self, key:int):
        if(isinstance(key, int)):
            return super().remove(key)

class TelaVenda:
    def __init__(self):
        self.__window = None

    def init_components(self):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Escolha uma opção', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Registrar venda', "RD1", default=False, key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Listar vendas', "RD1", default=False, key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Modificar venda', "RD1", default=False, key='3', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Excluir venda', "RD1", default=False, key='4', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')),
            sg.Button('Cancelar', size=(10,1), button_color=('white', 'firebrick3')), sg.Push()]
        ]
        self.__window = sg.Window('Sistema de Vendas').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):
        botao, opc = self.__window.Read()
        return botao, opc

    def ler_dados(self):
        layout = [
            [sg.Text('Registrar Nova Venda', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('ID:', size=(19, 1), font=('Helvetica', 12)), 
            sg.InputText(key='id', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Data (AAAA-MM-DD):', size=(19, 1), font=('Helvetica', 12)), 
            sg.InputText(key='data', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('ID Afiliado:', size=(19, 1), font=('Helvetica', 12)), 
            sg.InputText(key='afiliado_id', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Código Produto:', size=(19, 1), font=('Helvetica', 12)), 
            sg.InputText(key='produto_codigo', font=('Helvetica', 12), size=(30, 1))],
            [sg.Text('Quantidade:', size=(19, 1), font=('Helvetica', 12)), 
            sg.InputText(key='quantidade', font=('Helvetica', 12), size=(30, 1))],
            [sg.HorizontalSeparator(pad=(5, 15))],

            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]


        window = sg.Window('Registrar Venda', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def mostrar_vendas(self, lista_vendas):
        texto = "=== Lista de Vendas ===\n\n"
        for info in lista_vendas:
            texto += (f"ID: {info['id']} | Data: {info['data']} | "
                      f"Afiliado: {info['afiliado']} | Produto: {info['produto']} | "
                      f"Quantidade: {info['quantidade']} | Total: R${info['total']:.2f} | "
                      f"Status: {info['pagamento_afiliado']}\n")

        layout = [
            [sg.Multiline(texto, size=(100, len(lista_vendas) + 6), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Vendas Registradas", layout)
        window.read()
        window.close()

    def selecionar_venda(self, titulo: str):
        layout = [
            [sg.Text(titulo)],
            [sg.Text('ID da Venda:'), sg.InputText(key='id')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]
        window = sg.Window('Selecionar Venda', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values['id']

    def modificar_dados(self, venda_data):
        layout = [
            [sg.Text('Modificar Venda', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('ID:', size=(22, 1), font=('Helvetica', 12)), sg.Text(str(venda_data['id']), key='id_atual', font=('Helvetica', 12))],
            [sg.Text('Nova Data (AAAA-MM-DD):', size=(22, 1), font=('Helvetica', 12)), sg.InputText(venda_data['data'], key='data', font=('Helvetica', 12))],
            [sg.Text('Novo ID Afiliado:', size=(22, 1), font=('Helvetica', 12)), sg.InputText(str(venda_data['afiliado_id']), key='afiliado_id', font=('Helvetica', 12))],
            [sg.Text('Novo Código Produto:', size=(22, 1), font=('Helvetica', 12)), sg.InputText(venda_data['produto_codigo'], key='produto_codigo', font=('Helvetica', 12))],
            [sg.Text('Nova Quantidade:', size=(22, 1), font=('Helvetica', 12)), sg.InputText(str(venda_data['quantidade']), key='quantidade', font=('Helvetica', 12))],
            [sg.HorizontalSeparator(pad=(5, 15))],
            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]

        window = sg.Window('Modificar Venda', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def confirmar_exclusao(self, venda_data):
        layout = [
            [sg.Text(f'Confirmar exclusão da venda?')],
            [sg.Text(f'ID: {venda_data["id"]}')],
            [sg.Text(f'Produto: {venda_data["produto"]}')],
            [sg.Text(f'Quantidade: {venda_data["quantidade"]}')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]
        window = sg.Window('Confirmar Exclusão', layout)
        botao, _ = window.read()
        window.close()
        return botao == 'Confirmar'

    def mostrar_mensagem_popup(self, mensagem):
        sg.popup(mensagem)

class ControllerVenda:
    def __init__(self, tela, controller_afiliado, controller_produto):
        self.__tela = tela
        self.__controller_afiliado = controller_afiliado
        self.__controller_produto = controller_produto
        self.__venda_DAO = VendaDAO()

    @property
    def venda_DAO(self):
        return self.__venda_DAO

    def executar(self):
        self.__tela.init_components()
        while True:
            botao, opc = self.__tela.mostrar_menu()
            if botao == 'Confirmar':
                self.__tela.close()
                if opc['1'] == True:
                    self.__cadastrar()
                elif opc['2'] == True:
                    self.__listar()
                elif opc['3'] == True:
                    self.__modificar()
                elif opc['4'] == True:
                    self.__excluir()
                else:
                    self.__tela.mostrar_mensagem_popup("Opção inválida!")
                self.__tela.init_components()
            elif botao == 'Cancelar':
                self.__tela.close()
                break

    def __cadastrar(self):
        while True:
            try:
                data_atual = date.today()
                dados = self.__tela.ler_dados()
                if dados is None:
                    break

                id = dados['id']
                data = dados['data']
                try:
                    id = int(dados['id'])
                except ValueError:
                    raise DadoInvalidoException("Id", dados['id'], "Id deve ser um inteiro!")
                try:
                    data = date.fromisoformat(data)
                except ValueError:
                    raise DadoInvalidoException("Data", data, "Formato inválido. Use AAAA-MM-DD")
                
                if data > data_atual:
                    raise ValueError("Data não pode ser futura")

                try:
                    afiliado_id = int(dados['afiliado_id'])
                    produto_codigo = dados['produto_codigo']
                    quantidade = int(dados['quantidade'])
                except Exception:
                    raise Exception("Id de afiliado, código de produto e quantidade devem ser inteiros!")

                if self.__venda_DAO.get(id):
                    raise DadoInvalidoException("ID", id, "ID já existe")

                afiliado = None
                for a in self.__controller_afiliado.afiliado_DAO.get_all():
                    if a.id == afiliado_id:
                        afiliado = a
                        break
                if afiliado is None:
                    raise EntidadeNaoEncontradaException("Afiliado", afiliado_id)

                produto = None
                for p in self.__controller_produto.produto_DAO.get_all():
                    if p.codigo == produto_codigo:
                        produto = p
                        break
                if produto is None:
                    raise EntidadeNaoEncontradaException("Produto", produto_codigo)

                venda = Venda(id, data, afiliado, produto, quantidade)
                afiliado.vendas.append(venda)
                self.__venda_DAO.add(venda)

                self.__tela.mostrar_mensagem_popup("Venda registrada com sucesso!")
                break
            except Exception as e:
                self.__tela.mostrar_mensagem_popup(f"Erro ao registrar venda: {e}")

    def __listar(self):
        vendas = self.__venda_DAO.get_all()
        if not vendas:
            self.__tela.mostrar_mensagem_popup("Nenhuma venda registrada")
        else:
            lista_vendas = []
            for v in vendas:
                info = {
                    'id': v.id,
                    'data': str(v.data),
                    'afiliado': v.afiliado.nome,
                    'produto': v.produto.detalhes.nome,
                    'quantidade': v.quantidade,
                    'total': v.total,
                    'pagamento_afiliado': v.pagamento_afiliado
                }
                lista_vendas.append(info)
            self.__tela.mostrar_vendas(lista_vendas)

    def __modificar(self):
        try:
            id = self.__tela.selecionar_venda("Digite o ID da venda para modificar")
            if not id: 
                return

            try:
                id = int(id)
            except ValueError:
                raise DadoInvalidoException("Id", id, "Id deve ser um inteiro!")
            venda = self.__venda_DAO.get(id)
            
            if not venda:
                raise EntidadeNaoEncontradaException("Venda", id)

            if venda.pagamento_afiliado != 'não realizado':
                raise ViolacaoRegraNegocioException(
                    "Não é permitido modificar venda com pagamento realizado ou em andamento"
                )

            venda_data = {
                'id': venda.id,
                'data': str(venda.data),
                'afiliado_id': venda.afiliado.id,
                'produto_codigo': venda.produto.codigo,
                'quantidade': venda.quantidade
            }

            dados = self.__tela.modificar_dados(venda_data)
            if not dados:
                return

            data_atual = date.today()
            nova_data = date.fromisoformat(dados['data'])
            if nova_data > data_atual:
                raise ValueError("Data não pode ser futura")

            try:
                novo_afiliado_id = int(dados['afiliado_id'])
                novo_produto_codigo = dados['produto_codigo']
                nova_quantidade = int(dados['quantidade'])
            except Exception:
                raise Exception("Id de afiliado, código de produto e quantidade devem ser inteiros!")
            
            novo_afiliado = next((a for a in self.__controller_afiliado.afiliado_DAO.get_all() if a.id == novo_afiliado_id), None)
            if not novo_afiliado:
                raise EntidadeNaoEncontradaException("Afiliado", novo_afiliado_id)

            novo_produto = next((p for p in self.__controller_produto.produto_DAO.get_all() if p.codigo == novo_produto_codigo), None)
            if not novo_produto:
                raise EntidadeNaoEncontradaException("Produto", novo_produto_codigo)

            venda.data = nova_data
            venda.afiliado.vendas.remove(venda)
            venda.afiliado = novo_afiliado
            venda.produto = novo_produto
            venda.quantidade = nova_quantidade
            venda.calcularTotal()
            venda.pagamento_afiliado = 'não realizado'
            
            novo_afiliado.vendas.append(venda)
            self.__venda_DAO.update(venda)
            self.__tela.mostrar_mensagem_popup("Venda modificada com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao modificar venda: {e}")

    def __excluir(self):
        try:
            id = self.__tela.selecionar_venda("Digite o ID da venda para excluir")
            if not id: 
                return
                
            try:
                id = int(id)
            except ValueError:
                raise DadoInvalidoException("Id", id, "Id deve ser um inteiro!")
            venda = self.__venda_DAO.get(id)
            
            if not venda:
                raise EntidadeNaoEncontradaException("Venda", id)
            
            if venda.pagamento_afiliado != 'não realizado':
                raise ViolacaoRegraNegocioException(
                    "Não é permitido excluir venda com pagamento realizado ou em andamento"
                )

            venda_data = {
                "id": venda.id,
                "produto": venda.produto.detalhes.nome,
                "quantidade": venda.quantidade
            }

            if not self.__tela.confirmar_exclusao(venda_data):
                return

            venda.afiliado.vendas.remove(venda)
            self.__venda_DAO.remove(id)
            
            self.__tela.mostrar_mensagem_popup("Venda excluída com sucesso!")
            
        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao excluir venda: {e}")

class Comissao:
    def __init__(self, vendedor, recebedor, venda, tipo, valor):
        if not isinstance(vendedor, Afiliado):
            raise TypeError("vendedor deve ser do tipo Afiliado")
        if not isinstance(recebedor, Afiliado):
            raise TypeError("recebedor deve ser do tipo Afiliado")
        if not isinstance(venda, Venda):
            raise TypeError("venda deve ser do tipo Venda")
        if not isinstance(tipo, str) or tipo not in ("direto", "indireto"):
            raise ValueError("tipo deve ser a string 'direto' ou 'indireto'")
        if not isinstance(valor, (int, float)):
            raise TypeError("valor deve ser numérico")
        self.__vendedor = vendedor
        self.__recebedor = recebedor
        self.__venda = venda
        self.__tipo = tipo
        self.__valor = float(valor)

    @property
    def vendedor(self):
        return self.__vendedor

    @property
    def recebedor(self):
        return self.__recebedor

    @property
    def venda(self):
        return self.__venda

    @property
    def tipo(self):
        return self.__tipo

    @property
    def valor(self):
        return self.__valor

    def calcular(self):
        return self.__valor

class Pagamento:
    def __init__(self, id, data, afiliado, valorPago):
        if not isinstance(id, int):
            raise TypeError("id deve ser int")
        if not isinstance(data, date):
            raise TypeError("data deve ser do tipo date")
        if not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        if not isinstance(valorPago, (int, float)):
            raise TypeError("valorPago deve ser numérico")
        self.__id = id
        self.__data = data
        self.__afiliado = afiliado
        self.__valorPago = float(valorPago)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise TypeError("id deve ser int")
        self.__id = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if not isinstance(value, date):
            raise TypeError("data deve ser do tipo date")
        self.__data = value

    @property
    def afiliado(self):
        return self.__afiliado

    @afiliado.setter
    def afiliado(self, value):
        if not isinstance(value, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        self.__afiliado = value

    @property
    def valorPago(self):
        return self.__valorPago

    @valorPago.setter
    def valorPago(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("valorPago deve ser numérico")
        self.__valorPago = float(value)

class PagamentoDAO(DAO):
    def __init__(self):
        super().__init__('pagamento.pkl')
    
    def add(self, pagamento: Pagamento):
        if((pagamento is not None) and isinstance(pagamento, Pagamento) and isinstance(pagamento.id, int)):
            super().add(pagamento.id, pagamento)
    
    def update(self, pagamento: Pagamento):
        if((pagamento is not None) and isinstance(pagamento, Pagamento) and isinstance(pagamento.id, int)):
            super().update(pagamento.id, pagamento)

    def get(self, key:int):
        if isinstance(key, int):
            return super().get(key)

    def remove(self, key:int):
        if(isinstance(key, int)):
            return super().remove(key)

class TelaPagamento:
    def __init__(self):
        self.__window = None

    def init_components(self):
        sg.ChangeLookAndFeel('DarkBlue14')
        layout = [
            [sg.Text('Escolha uma opção', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Gerar Comissões', "RD1", default=False, key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Listar Comissões', "RD1", default=False, key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Processar Pagamento das Comissões', "RD1", default=False, key='3', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Listar Pagamentos Efetuados', "RD1", default=False, key='4', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')),
            sg.Button('Cancelar', size=(10,1), button_color=('white', 'firebrick3')), sg.Push()]
        ]
        self.__window = sg.Window('Menu Pagamento').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):

        botao, valores = self.__window.read()
        return botao, valores
    
    def ler_dados(self):
        try:
            id = int(input("Id: ").strip())
        except ValueError:
            raise DadoInvalidoException("Id", "não numérico", "Id deve ser um número inteiro")
        
        data_str = input("Data no formato AAAA-MM-DD: ").strip()
        try:
            data = date.fromisoformat(data_str)
        except ValueError:
            raise DadoInvalidoException("Data", data_str, "Formato de data inválido. Use AAAA-MM-DD")

        try:
            afiliado_id = int(input("Id do Afiliado: ").strip())
        except ValueError:
            raise DadoInvalidoException("Afiliado", "não numérico", "ID do Afiliado deve ser um número inteiro")
        
        valorPago_str = input("Valor Pago: ").strip()
        try:
            valorPago = float(valorPago_str)
        except ValueError:
            raise DadoInvalidoException("Valor Pago", valorPago_str, "Valor pago deve ser numérico")
        
        return id, data, afiliado_id, valorPago

    def mostrar_comissao(self, lista_comissoes):
        texto = "=== Lista de Comissões ===\n\n"
        for info in lista_comissoes:
            texto += f"Recebedor: {info['recebedor']} | Valor: R${info['valor']:.2f} | Venda: {info['venda']} | Tipo: {info['tipo']} | Vendedor: {info['vendedor']}\n"

        layout = [
            [sg.Multiline(texto, size=(60, len(lista_comissoes) + 6), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Lista de Comissões", layout)
        window.read()
        window.close()

    def mostrar_pagamento(self, lista_pagamentos):
        texto = "=== Lista de Pagamentos ===\n\n"
        for info in lista_pagamentos:
            texto += f"ID Pagamento: {info['id']} | Data: {info['data']} | Afiliado: {info['afiliado']} | Valor Pago: R${info['valorPago']:.2f}\n"

        layout = [
            [sg.Multiline(texto, size=(70, len(lista_pagamentos) + 6), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Lista de Pagamentos", layout)
        window.read()
        window.close()
 
    def popup(self, mensagem):
        sg.popup(mensagem)
class ControllerPagamento:
    def __init__(self, tela, controller_venda):
        self.__tela = tela
        self.__controller_venda = controller_venda
        self.__pagamento_DAO = PagamentoDAO()
        self.__listaComissoes = []

    @property
    def listaComissoes(self):
        return self.__listaComissoes

    @listaComissoes.setter
    def listaComissoes(self, value):
        if not isinstance(value, list):
            raise TypeError("listaComissoes deve ser uma lista de Comissão")
        for item in value:
            if not isinstance(item, Comissao):
                raise TypeError("Cada item em listaComissoes deve ser do tipo Comissao")
        self.__listaComissoes = value

    @property
    def pagamento_DAO(self):
        return self.__pagamento_DAO

    @pagamento_DAO.setter
    def pagamento_DAO(self, pagamento_DAO):
        if not isinstance(pagamento_DAO, PagamentoDAO):
            raise TypeError("listaPagamentos deve ser uma lista de Pagamento")
        for item in pagamento_DAO:
            if not isinstance(item, Pagamento):
                raise TypeError("Cada item em listaPagamentos deve ser do tipo Pagamento")
        self.__pagamento_DAO = pagamento_DAO

    def executar(self):
        self.__tela.init_components()
        while True:
            botao, opc = self.__tela.mostrar_menu()
            if botao == 'Confirmar':
                self.__tela.close()
                if opc['1'] == True:
                    self.__gerar_comissoes()
                elif opc['2'] == True:
                    self.__listar_comissoes()
                elif opc['3'] == True:
                    self.__processar_pagamentos()
                elif opc['4'] == True:
                    self.__listar_pagamentos()
                else:
                    self.__tela.opcao_invalida()
                self.__tela.init_components()
            elif botao == 'Cancelar':
                self.__tela.close()
                break

    def __gerar_comissoes(self):
        self.__listaComissoes.clear()
        venda_dao = self.__controller_venda.venda_DAO
        
        for venda in venda_dao.get_all():
            if venda.pagamento_afiliado == 'realizado':
                continue

            total = venda.total
            afiliado = venda.afiliado
            afiliado_parent = afiliado.parent

            comissao_direta = total * 0.05
            comissao_indireta = total * 0.01 if afiliado_parent is not None else 0

            if afiliado_parent:
                comissao_parent = Comissao(afiliado, afiliado_parent,
                                           venda, 'indireto', comissao_indireta)
                self.__listaComissoes.append(comissao_parent)
            
            comissao = Comissao(afiliado, afiliado, venda, 'direto', comissao_direta)
            self.__listaComissoes.append(comissao)

        for c in self.__listaComissoes:
            c.venda.pagamento_afiliado = 'aguardando confirmação'
            venda_dao.update(c.venda)
        self.__tela.popup("Comissões geradas com sucesso!")

    def __listar_comissoes(self):
        if not self.__listaComissoes:
            self.__tela.popup("Nenhuma comissão gerada.")
            return
        lista_comissoes = []
        for c in self.__listaComissoes:
            info = {
                'vendedor': f'{c.vendedor.nome} - {c.vendedor.id}',
                'recebedor': f'{c.recebedor.nome} - {c.recebedor.id}',
                'venda': c.venda.id,
                'tipo': c.tipo,
                'valor': c.valor
            }
            lista_comissoes.append(info)
        self.__tela.mostrar_comissao(lista_comissoes)

    def __processar_pagamentos(self):
        venda_dao = self.__controller_venda.venda_DAO
        next_id = max((p.id for p in self.__pagamento_DAO.get_all()), default=0) + 1
        
        for com in list(self.__listaComissoes):
            pag = Pagamento(
                next_id,
                date.today(),
                com.recebedor,
                com.valor
            )
            self.__pagamento_DAO.add(pag)
            com.venda.pagamento_afiliado = 'realizado'
            venda_dao.update(com.venda)
            next_id += 1

        self.__listaComissoes.clear()
        self.__tela.popup("Pagamentos processados com sucesso!")

    def __listar_pagamentos(self):
        pagamentos = self.__pagamento_DAO.get_all()
        if not pagamentos:
            self.__tela.popup("Nenhum pagamento efetuado.")
            return
        lista_pagamentos = []
        for p in pagamentos:
            info = {
                'id': p.id,
                'data': p.data,
                'afiliado': f"{p.afiliado.nome} (ID: {p.afiliado.id})",
                'valorPago': p.valorPago
            }
            lista_pagamentos.append(info)
        self.__tela.mostrar_pagamento(lista_pagamentos)

class Relatorio:
    def __init__(self, periodo, afiliado=None):
        if not (isinstance(periodo, tuple) and len(periodo) == 2 and all(isinstance(d, date) for d in periodo)):
            raise TypeError("periodo deve ser uma tupla (data_inicial, data_final) do tipo date")
        if afiliado is not None and not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado ou None")
        self.__periodo = periodo
        self.__afiliado = afiliado

    @property
    def periodo(self):
        return self.__periodo

    @periodo.setter
    def periodo(self, value):
        if not (isinstance(value, tuple) and len(value) == 2 and all(isinstance(d, date) for d in value)):
            raise TypeError("periodo deve ser uma tupla (data_inicial, data_final) do tipo date")
        self.__periodo = value

    @property
    def afiliado(self):
        return self.__afiliado

    @afiliado.setter
    def afiliado(self, value):
        if value is not None and not isinstance(value, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado ou None")
        self.__afiliado = value

    def gerarRelatorioVendas(self, vendas):
        data_inicio, data_fim = self.periodo
        vendas_filtradas = []
        for venda in vendas:
            if data_inicio <= venda.data <= data_fim:
                if self.afiliado is None or venda.afiliado == self.afiliado:
                    vendas_filtradas.append(venda)
        return vendas_filtradas

    def gerarRelatorioFinanceiro(self, pagamentos):
        data_inicio, data_fim = self.periodo
        pagamentos_filtrados = []
        for pagamento in pagamentos:
            if data_inicio <= pagamento.data <= data_fim:
                if self.afiliado is None or pagamento.afiliado == self.afiliado:
                    pagamentos_filtrados.append(pagamento)
        return pagamentos_filtrados

class TelaRelatorio:
    def __init__(self):
        self.__window = None

    def init_components(self):
        sg.theme('DarkBlue14')
        layout = [
            [sg.Text('Escolha uma opção', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Gerar Relatório de Vendas', "RD1", default=False, key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Gerar Relatório de Pagamentos', "RD1", default=False, key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')),
            sg.Button('Voltar', size=(10,1), button_color=('white', 'firebrick3')), sg.Push()]
        ]
        self.__window = sg.Window('Menu de Relatórios').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):
        botao, opc = self.__window.Read()
        return botao, opc

    def ler_dados(self):
        layout = [
            [sg.Text('Gerar Relatório', font=('Helvetica', 16), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Text('Data Inicial (AAAA-MM-DD)', size=(22, 1), font=('Helvetica', 11)), sg.InputText(key='data_inicial', size=(35, 1))],
            [sg.Text('Data Final (AAAA-MM-DD)', size=(22, 1), font=('Helvetica', 11)), sg.InputText(key='data_final', size=(35, 1))],
            [sg.Text('ID do Afiliado (opcional)', size=(22, 1), font=('Helvetica', 11)), sg.InputText(key='afiliado_id', size=(35, 1))],
            [sg.HorizontalSeparator(pad=(5, 15))],
            [sg.Push(), 
            sg.Button('Confirmar', size=(12, 1), button_color=('white', 'green')), 
            sg.Button('Cancelar', size=(12, 1), button_color=('white', 'firebrick3')), 
            sg.Push()]
        ]

        window = sg.Window('Parâmetros do Relatório', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def mostrar_relatorio_vendas(self, vendas):
        texto = "=== Relatório de Vendas ===\n\n"
        if not vendas:
            texto += "Nenhuma venda no período.\n"
        else:
            for venda in vendas:
                texto += (f"ID: {venda['id']} | Data: {venda['data']} | Afiliado: {venda['afiliado']} | "
                         f"Produto: {venda['produto']} | Quantidade: {venda['quantidade']} | "
                         f"Total: R${venda['total']:.2f}\n")

        layout = [
            [sg.Multiline(texto, size=(100, min(25, len(vendas)+6)), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Relatório de Vendas", layout)
        window.read()
        window.close()

    def mostrar_relatorio_financeiro(self, pagamentos):
        texto = "=== Relatório Financeiro ===\n\n"
        if not pagamentos:
            texto += "Nenhum pagamento no período.\n"
        else:
            for pagamento in pagamentos:
                texto += (f"ID: {pagamento['id']} | Data: {pagamento['data']} | "
                         f"Afiliado: {pagamento['afiliado']} | "
                         f"Valor Pago: R${pagamento['valorPago']:.2f}\n")

        layout = [
            [sg.Multiline(texto, size=(100, min(25, len(pagamentos)+6)), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Relatório Financeiro", layout)
        window.read()
        window.close()

    def mostrar_mensagem_popup(self, mensagem):
        sg.popup(mensagem)


class ControllerRelatorio:
    def __init__(self, tela, controller_venda, controller_pagamento, controller_afiliado):
        self.__tela = tela
        self.__controller_venda = controller_venda
        self.__controller_pagamento = controller_pagamento
        self.__controller_afiliado = controller_afiliado

    def executar(self):
        self.__tela.init_components()
        while True:
            botao, opc = self.__tela.mostrar_menu()
            if botao == 'Confirmar':
                self.__tela.close()
                if opc['1'] == True:
                    self.gerar_relatorio_vendas()
                elif opc['2'] == True:
                    self.gerar_relatorio_financeiro()
                else:
                    self.__tela.mostrar_mensagem_popup("Opção inválida!")
                self.__tela.init_components()
            elif botao == 'Voltar' or botao is None:
                self.__tela.close()
                break

    def gerar_relatorio_vendas(self):
        try:
            dados = self.__tela.ler_dados()
            if dados is None:
                return

            data_inicial_str = dados['data_inicial']
            data_final_str = dados['data_final']
            afiliado_id_str = dados['afiliado_id']

            if not data_inicial_str or not data_final_str:
                raise CampoObrigatorioException("Data inicial e final")

            try:
                data_inicial = date.fromisoformat(data_inicial_str)
                data_final = date.fromisoformat(data_final_str)
            except ValueError:
                raise DadoInvalidoException("Data", "formato inválido", "Use AAAA-MM-DD")

            if data_inicial > data_final:
                raise DadoInvalidoException("Datas", "inicial maior que final")

            afiliado_id = None
            afiliado = None
            if afiliado_id_str:
                try:
                    afiliado_id = int(afiliado_id_str)
                except ValueError:
                    raise DadoInvalidoException("ID Afiliado", afiliado_id_str, "Deve ser um número inteiro")

                afiliado = self.__controller_afiliado.afiliado_DAO.get(afiliado_id)
                if not afiliado:
                    raise EntidadeNaoEncontradaException("Afiliado", afiliado_id)

            vendas_filtradas = []
            for venda in self.__controller_venda.venda_DAO.get_all():
                if data_inicial <= venda.data <= data_final:
                    if afiliado is None or venda.afiliado.id == afiliado.id:
                        vendas_filtradas.append({
                            'id': venda.id,
                            'data': str(venda.data),
                            'afiliado': venda.afiliado.nome,
                            'produto': venda.produto.detalhes.nome,
                            'quantidade': venda.quantidade,
                            'total': venda.total
                        })

            self.__tela.mostrar_relatorio_vendas(vendas_filtradas)

        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao gerar relatório de vendas: {e}")

    def gerar_relatorio_financeiro(self):
        try:
            dados = self.__tela.ler_dados()
            if dados is None:
                return

            data_inicial_str = dados['data_inicial']
            data_final_str = dados['data_final']
            afiliado_id_str = dados['afiliado_id']

            if not data_inicial_str or not data_final_str:
                raise CampoObrigatorioException("Data inicial e final")

            try:
                data_inicial = date.fromisoformat(data_inicial_str)
                data_final = date.fromisoformat(data_final_str)
            except ValueError:
                raise DadoInvalidoException("Data", "formato inválido", "Use AAAA-MM-DD")

            if data_inicial > data_final:
                raise DadoInvalidoException("Datas", "inicial maior que final")

            afiliado_id = None
            afiliado = None
            if afiliado_id_str:
                try:
                    afiliado_id = int(afiliado_id_str)
                except ValueError:
                    raise DadoInvalidoException("ID Afiliado", afiliado_id_str, "Deve ser um número inteiro")

                afiliado = self.__controller_afiliado.afiliado_DAO.get(afiliado_id)
                if not afiliado:
                    raise EntidadeNaoEncontradaException("Afiliado", afiliado_id)

            pagamentos_filtrados = []
            for pagamento in self.__controller_pagamento.pagamento_DAO.get_all():
                if data_inicial <= pagamento.data <= data_final:
                    if afiliado is None or pagamento.afiliado.id == afiliado.id:
                        pagamentos_filtrados.append({
                            'id': pagamento.id,
                            'data': str(pagamento.data),
                            'afiliado': f"{pagamento.afiliado.nome} (ID: {pagamento.afiliado.id})",
                            'valorPago': pagamento.valorPago
                        })

            self.__tela.mostrar_relatorio_financeiro(pagamentos_filtrados)

        except Exception as e:
            self.__tela.mostrar_mensagem_popup(f"Erro ao gerar relatório financeiro: {e}")

class ControllerSistema:
    def __init__(self):
        self.__window = None
        self.init_components()
        tela__produto = TelaProduto()
        tela__afiliado = TelaAfiliado()
        tela__venda = TelaVenda()
        tela__pagamento = TelaPagamento()
        tela__relatorio = TelaRelatorio()
        
        self.__controller_produto = ControllerProduto(tela__produto)
        self.__controller_afiliado = ControllerAfiliado(tela__afiliado)
        
        self.__controller_venda = ControllerVenda(
            tela__venda, 
            self.__controller_afiliado,
            self.__controller_produto
        )
        
        self.__controller_pagamento = ControllerPagamento(
            tela__pagamento,
            self.__controller_venda
        )
        
        self.__controller_relatorio = ControllerRelatorio(
            tela__relatorio,
            self.__controller_venda,
            self.__controller_pagamento,
            self.__controller_afiliado
        )
        
        # Configurar dependência adicional para o ControllerProduto
        self.__controller_produto.set_controller_venda(self.__controller_venda)

    @property
    def controller_produto(self):
        return self.__controller_produto
    
    @property
    def controller_afiliado(self):
        return self.__controller_afiliado
    
    @property
    def controller_venda(self):
        return self.__controller_venda
    
    @property
    def controller_pagamento(self):
        return self.__controller_pagamento
    
    @property
    def controller_relatorio(self):
        return self.__controller_relatorio
    
    def init_components(self):
        sg.theme('DarkBlue14')
        
        layout = [
            [sg.Text('Sistema Financeiro de Afiliados', font=('Helvetica', 14), expand_x=True, justification='center', pad=(5, 10))],
            [sg.Radio('Gerenciar Produtos', "RD1", key='1', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Gerenciar Afiliados', "RD1", key='2', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Gerenciar Vendas', "RD1", key='3', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Gerenciar Pagamentos', "RD1", key='4', font=('Helvetica', 12), pad=(10, 5))],
            [sg.Radio('Gerenciar Relatório', "RD1", key='5', font=('Helvetica', 12), pad=(10, 5))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button('Confirmar', size=(10,1), button_color=('white', 'green')),
            sg.Button('Cancelar', size=(10,1), button_color=('white', 'firebrick3')), sg.Push()]
        ]

        self.__window = sg.Window('Sistema Financeiro de Afiliados', layout, size=(500, 320), finalize=True)

    def executar(self):
        while True:
            button, key = self.__window.Read()
            if button == 'Confirmar':
                if key['1'] == True:
                    self.__controller_produto.executar()
                elif key['2'] == True:
                    self.__controller_afiliado.executar()
                elif key['3'] == True:
                    self.__controller_venda.executar()
                elif key['4'] == True:
                    self.__controller_pagamento.executar()
                elif key['5'] == True:
                    self.__controller_relatorio.executar()
            elif button == 'Cancelar':
                break
            else:
                sg.popup("opção invalida!")

sistema = ControllerSistema()
sistema.executar()