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
        sg.ChangeLookAndFeel('Reddit')
        layout = [
            [sg.Text('Escolha uma opção')],
            [sg.Radio('Cadastrar afiliado', "RD1", default=False, key='1')],
            [sg.Radio('Listar afiliados', "RD1", default=False, key='2')],
            [sg.Radio('Modificar afiliado', "RD1", default=False, key='3')],
            [sg.Radio('Excluir afiliado', "RD1", default=False, key='4')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]
        self.__window = sg.Window('Sistema Financeiro de Afiliados').Layout(layout)

    def close(self):
        if self.__window:
            self.__window.Close()
        self.__window = None

    def mostrar_menu(self):
        botao, opc = self.__window.Read()
        return botao, opc

    def ler_dados(self):
        layout = [
            [sg.Text('Incluir Novo Afiliado')],
            [sg.Text('Id', size=(15, 1)), sg.InputText(key='id')],
            [sg.Text('Nome', size=(15, 1)), sg.InputText(key='nome')],
            [sg.Text('Contato', size=(15, 1)), sg.InputText(key='contato')],
            [sg.Text('Parent ID', size=(15, 1)), sg.InputText(key='parent')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
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

        layout = [
            [sg.Multiline(texto, size=(60, len(lista_afiliados) + 6), disabled=True)],
            [sg.Button("Fechar")]
        ]

        window = sg.Window("Afiliados Cadastrados", layout)
        window.read()
        window.close()

    def selecionar_afiliado(self, titulo: str):
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
        layout = [
            [sg.Text('Modificar Afiliado')],
            [sg.Text('ID Atual:'), sg.Text(str(afiliado_data['id']), key='id_atual')],
            [sg.Text('Novo ID:'), sg.InputText(str(afiliado_data['id']), key='id')],
            [sg.Text('Nome:'), sg.InputText(afiliado_data['nome'], key='nome')],
            [sg.Text('Contato:'), sg.InputText(afiliado_data['contato'], key='contato')],
            [sg.Text('Parent ID:'), sg.InputText(str(afiliado_data['parent']) if afiliado_data['parent'] else '', key='parent')],
            [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
        ]

        window = sg.Window('Modificar Afiliado', layout)
        botao, values = window.read()
        window.close()
        return None if botao == 'Cancelar' else values

    def confirmar_exclusao(self, afiliado_data):
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

    @afiliado_DAO.setter
    def afiliado_DAO (self, value):
        if not isinstance(value, list):
            raise TypeError("listaAfiliados deve ser uma lista de Afiliado")
        for item in value:
            if not isinstance(item, Afiliado):
                raise TypeError("Cada item em listaAfiliados deve ser do tipo Afiliado")
        self.__afiliado_DAO = value

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

                id = int(dados['id'])
                nome = dados['nome']
                contato = dados['contato']
                parent_id = dados['parent']

                parent = None
                for a in self.__afiliado_DAO.get_all():
                    if a.id == id:
                        raise DadoInvalidoException("Id", id, "ID já existe")
                    if parent_id and a.id == int(parent_id):
                        parent = a

                if parent_id and not parent:
                    raise EntidadeNaoEncontradaException("Afiliado", parent_id)

                afiliado = Afiliado(id, nome, contato, parent)
                self.__afiliado_DAO.add(afiliado)

                self.__tela.mostrar_mensagem_popup("Afiliado cadastrado com sucesso!")

                break
            except Exception as e:
                self.__tela.mostrar_mensagem_popup(f"Erro ao cadastrar afiliado: {e}")
            

    def __listar(self):
        afiliados = self.__afiliado_DAO.get_all()
        if not afiliados:
            raise EntidadeNaoEncontradaException("Afiliado")
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

            novo_id = int(dados['id'])
            nome = dados['nome']
            contato = dados['contato']
            parent_id = dados['parent']

            if novo_id != id and self.__afiliado_DAO.get(novo_id):
                raise DadoInvalidoException("ID", novo_id, "ID já existe")

            afiliado.id = novo_id
            afiliado.nome = nome
            afiliado.contato = contato

            if parent_id:
                parent = self.__afiliado_DAO.get(int(parent_id))
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
        self.__nome = nome
        self.__descricao = descricao
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
    def mostrar_menu(self):
        print("\n=== Menu Produtos ===")
        print("1. Cadastrar produto")
        print("2. Listar produtos")
        print("3. Modificar produto")
        print("4. Excluir produto")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def ler_dados(self):
        codigo = input("Código: ").strip()
        if not codigo:
            raise CampoObrigatorioException("Código")
            
        nome = input("Nome: ").strip()
        if not nome:
            raise CampoObrigatorioException("Nome")
            
        descricao = input("Descrição: ").strip()
        if not descricao:
            raise CampoObrigatorioException("Descrição")
            
        preco_str = input("Preço: ")
        try:
            preco = float(preco_str)
        except ValueError:
            raise DadoInvalidoException("Preço", preco_str, "Preço deve ser um valor numérico")
            
        return codigo, nome, descricao, preco

    def mostrar_produto(self, info):
        print(f"Código: {info['codigo']} | Nome: {info['nome']} | Descrição: {info['descricao']} | Preço: {info['preco']}")

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
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__listar()
            elif opc == '3':
                self.__modificar()
            elif opc == '4':
                self.__excluir()
            elif opc == '0':
                break
            else:
                print("Opção inválida!") # Fazer exception

    def __cadastrar(self):
        try:
            dados = self.__tela.ler_dados()
            
            for item in self.__produto_DAO.get_all():
                if item.codigo == dados[0]:
                    raise DadoInvalidoException("Código", dados[0], "Código já existe")

            produto = Produto(*dados)
            self.__produto_DAO.add(produto)
            print("Produto cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")

    def __listar(self):
        produtos = self.__produto_DAO.get_all()
        print("\n=== Lista de Produtos ===")
        if not produtos:
            print("Nenhum produto cadastrado.")
        else:
            for p in produtos:
                info = {'codigo': p.codigo, 'nome': p.nome, 'descricao': p.descricao, 'preco': p.preco}
                self.__tela.mostrar_produto(info)

    def __modificar(self):
        try:
            codigo = input("Digite o código do produto: ").strip()
            produto = None

            for p in self.__produto_DAO.get_all():
                if p.codigo == codigo:
                    produto = p
                    break
            
            if not produto:
                raise EntidadeNaoEncontradaException("Produto", codigo)

            print("\nDeixe em branco para manter o valor atual")

            novo_codigo = input(f"Código atual ({produto.codigo}): ").strip()
            if novo_codigo:
                for p in self.__produto_DAO.get_all():
                    if p != produto and p.codigo == novo_codigo:
                        raise DadoInvalidoException("Código", novo_codigo, "Código já está em uso")
                produto.codigo = novo_codigo

            novo_nome = input(f"Nome atual ({produto.nome}): ").strip()
            if novo_nome:
                produto.nome = novo_nome
                
            nova_desc = input(f"Descrição atual ({produto.descricao}): ").strip()
            if nova_desc:
                produto.descricao = nova_desc
                
            novo_preco = input(f"Preço atual ({produto.preco}): ").strip()
            if novo_preco:
                try:
                    produto.preco = float(novo_preco)
                except ValueError:
                    raise DadoInvalidoException("Preço", novo_preco, "Preço deve ser numérico")
            
            print("Produto atualizado com sucesso!")
            
        except Exception as e:
            print(f"Erro: {e}")

    def __excluir(self):
        try:
            codigo = input("Digite o código do produto: ").strip()
            produto = None
            
            for p in self.__produto_DAO.get_all():
                if p.codigo == codigo:
                    produto = p
                    break
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
                
            self.__produto_DAO.remove(produto.codigo)
            print("Produto excluído com sucesso!")
            
        except Exception as e:
            print(f"Erro: {e}") 

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
    def mostrar_menu(self):
        print("\n=== Menu vendas ===")
        print("1. Registrar venda")
        print("2. Listar vendas")
        print("3. Modificar venda") 
        print("4. Excluir venda") 
        print("0. Voltar")
        return input("Escolha uma opção: ")

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

        produto_codigo = input("Código do Produto: ").strip()
        if not produto_codigo:
            raise CampoObrigatorioException("Código do Produto")

        quantidade_str = input("Quantidade: ").strip()
        try:
            quantidade = int(quantidade_str)
        except ValueError:
            raise DadoInvalidoException("Quantidade", quantidade_str, "Quantidade deve ser um número inteiro")

        return id, data, afiliado_id, produto_codigo, quantidade

    def mostrar_venda(self, info):
        print(f"Id: {info['id']} | Data: {info['data']} | Afiliado: {info['afiliado']} | Produto: {info['produto']} | Quantidade: {info['quantidade']} | Total: R${info['total']} | Status Pagamento: {info.get('pagamento_afiliado', '')}")

class ControllerVenda:
    def __init__(self, tela, controller_afiliado, controller_produto):
        self.__tela = tela
        self.__controller_afiliado = controller_afiliado
        self.__controller_produto = controller_produto
        self.__venda_DAO = VendaDAO()

    @property
    def venda_DAO(self):
        return self.__venda_DAO

    @venda_DAO.setter
    def venda_DAO(self, venda_DAO):
        if not isinstance(venda_DAO, VendaDAO):
            raise TypeError("lista Vendas deve ser uma lista de Venda")
        for item in venda_DAO:
            if not isinstance(item, Venda):
                raise TypeError("Cada item em lista Vendas deve ser do tipo Venda")
        self.__venda_DAO = venda_DAO

    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__listar()
            elif opc == '3':
                self.__modificar()
            elif opc == '4':
                self.__excluir()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

    def __cadastrar(self):
        try:
            dados = self.__tela.ler_dados()

            for item in self.__venda_DAO.get_all():
                if item.id == dados[0]:
                    raise DadoInvalidoException("Id", dados[0], "ID já existe")
                    
            id, data, afiliado_id, produto_codigo, quantidade = dados

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
            venda.afiliado.vendas.append(venda)
            self.__venda_DAO.add(venda)
            print("Venda registrada com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")

    def __listar(self):
        vendas = self.__venda_DAO.get_all()
        print("\n=== Lista de Vendas ===")
        if not vendas:
            print("Nenhuma venda registrada.")
        else:
            for v in vendas:
                info = {
                    'id': v.id,
                    'data': v.data,
                    'afiliado': v.afiliado.nome,
                    'produto': v.produto.nome,
                    'quantidade': v.quantidade,
                    'total': v.total,
                    'pagamento_afiliado': v.pagamento_afiliado
                }
                self.__tela.mostrar_venda(info)

    def __modificar(self):
        try:
            venda_id = int(input("ID da venda: "))
            venda = None

            for v in self.__venda_DAO.get_all():
                if v.id == venda_id:
                    venda = v
                    break
            
            if not venda:
                raise EntidadeNaoEncontradaException("Venda", venda_id)

            if venda.pagamento_afiliado == 'realizado':
                raise ViolacaoRegraNegocioException(
                    "Não é permitido modificar venda com status pagamento realizado"
                )
                
            print("\nDeixe em branco para manter o valor atual")

            nova_data = input(f"Data atual ({venda.data}): ").strip()
            if nova_data:
                try:
                    venda.data = date.fromisoformat(nova_data)
                except ValueError:
                    raise DadoInvalidoException("Data", nova_data, "Formato de data inválido. Use AAAA-MM-DD")

            novo_afiliado_id = input(f"ID Afiliado atual ({venda.afiliado.id}): ").strip()
            if novo_afiliado_id:
                try:
                    novo_afiliado_id = int(novo_afiliado_id)
                except ValueError:
                    raise DadoInvalidoException("Afiliado", novo_afiliado_id, "ID do Afiliado deve ser numérico")
                    
                afiliado = None
                for a in self.__controller_afiliado.afiliado_DAO.get_all():
                    if a.id == novo_afiliado_id:
                        afiliado = a
                        break
                if not afiliado:
                    raise EntidadeNaoEncontradaException("Afiliado", novo_afiliado_id)
                venda.afiliado = afiliado

            novo_produto_cod = input(f"Código Produto atual ({venda.produto.codigo}): ").strip()
            if novo_produto_cod:
                produto = None
                for p in self.__controller_produto.produto_DAO.get_all():
                    if p.codigo == novo_produto_cod:
                        produto = p
                        break
                if not produto:
                    raise EntidadeNaoEncontradaException("Produto", novo_produto_cod)
                venda.produto = produto

            nova_qtde = input(f"Quantidade atual ({venda.quantidade}): ").strip()
            if nova_qtde:
                try:
                    venda.quantidade = int(nova_qtde)
                except ValueError:
                    raise DadoInvalidoException("Quantidade", nova_qtde, "Quantidade deve ser um número inteiro")

            venda.calcularTotal()
            venda.pagamento_afiliado = 'não realizado'
            print("Venda atualizada com sucesso!")
            
        except Exception as e:
            print(f"Erro: {e}")

    def __excluir(self):
        try:
            venda_id = int(input("ID da venda: "))
            venda = None
            # exclui pela key
            v = self.__venda_DAO.get(venda_id)
            if not v:
                raise EntidadeNaoEncontradaException("Venda", venda_id)
                
            venda = v
            venda.afiliado.vendas.remove(venda)
            self.__venda_DAO.remove(venda_id)
            print("Venda excluída com sucesso!")

        except Exception as e:
            print(f"Erro: {e}")

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
    def mostrar_menu(self):
        print("\n=== Menu Pagamento ===")
        print("1. Gerar Comissões")
        print("2. Listar Comissões")
        print("3. Processar Pagamento das Comissões")
        print("4. Listar Pagamentos Efetuados")
        print("0. Voltar")
        return input("Escolha uma opção: ")

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

    def mostrar_comissao(self, info):
        print(f"Recebedor: {info['recebedor']} | Valor: R${info['valor']:.2f} | "
              f"Venda: {info['venda']} | Tipo: {info['tipo']} | Vendedor: {info['vendedor']}")

    def mostrar_pagamento(self, info):
        print(f"ID Pagamento: {info['id']} | Data: {info['data']} | Afiliado: {info['afiliado']} | Valor Pago: R${info['valorPago']:.2f}")

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
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__gerar_comissoes()
            elif opc == '2':
                self.__listar_comissoes()
            elif opc == '3':
                self.__processar_pagamentos()
            elif opc == '4':
                self.__listar_pagamentos()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

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
        print("Comissões geradas com sucesso!")

    def __listar_comissoes(self):
        if not self.__listaComissoes:
            print("Nenhuma comissão gerada.")
            return
        for c in self.__listaComissoes:
            info = {
                'vendedor': f'{c.vendedor.nome} - {c.vendedor.id}',
                'recebedor': f'{c.recebedor.nome} - {c.recebedor.id}',
                'venda': c.venda.id,
                'tipo': c.tipo,
                'valor': c.valor
            }
            self.__tela.mostrar_comissao(info)

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
        print("Pagamentos processados com sucesso!")

    def __listar_pagamentos(self):
        pagamentos = self.__pagamento_DAO.get_all()
        if not pagamentos:
            print("Nenhum pagamento efetuado.")
            return
        for p in pagamentos:
            info = {
                'id': p.id,
                'data': p.data,
                'afiliado': f"{p.afiliado.nome} (ID: {p.afiliado.id})",
                'valorPago': p.valorPago
            }
            self.__tela.mostrar_pagamento(info)

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
    def mostrar_menu(self):
        print("\n=== Menu Relatórios ===")
        print("1. Gerar Relatório de Vendas")
        print("2. Gerar Relatório de Pagamentos")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def ler_dados(self):
        data_inicial_str = input("Data inicial (YYYY-MM-DD): ").strip()
        if not data_inicial_str:
            raise CampoObrigatorioException("Data inicial")
        try:
            data_inicial = date.fromisoformat(data_inicial_str)
        except ValueError:
            raise DadoInvalidoException("Data inicial", data_inicial_str, "Formato de data inválido. Use AAAA-MM-DD")

        data_final_str = input("Data final (YYYY-MM-DD): ").strip()
        if not data_final_str:
            raise CampoObrigatorioException("Data final")
        try:
            data_final = date.fromisoformat(data_final_str)
        except ValueError:
            raise DadoInvalidoException("Data final", data_final_str, "Formato de data inválido. Use AAAA-MM-DD")

        afiliado_id_str = input("Id do Afiliado (opcional, deixe em branco para todos): ").strip()
        afiliado_id = None
        if afiliado_id_str:
            try:
                afiliado_id = int(afiliado_id_str)
            except ValueError:
                raise DadoInvalidoException("Id do Afiliado", afiliado_id_str, "Id do Afiliado deve ser um número inteiro")

        return data_inicial, data_final, afiliado_id

    def mostrar_relatorio_vendas(self, vendas):
        print("\n=== Relatório de Vendas ===")
        if not vendas:
            print("Nenhuma venda no período.")
            return
        for venda in vendas:
            print(f"ID: {venda.id} | Data: {venda.data} | Afiliado: {venda.afiliado.nome} | Produto: {venda.produto.nome} | Quantidade: {venda.quantidade} | Total: R${venda.total:.2f}")

    def mostrar_relatorio_financeiro(self, pagamentos):
        print("\n=== Relatório Financeiro ===")
        if not pagamentos:
            print("Nenhum pagamento no período.")
            return
        for pagamento in pagamentos:
            print(f"ID: {pagamento.id} | Data: {pagamento.data} | Afiliado: {pagamento.afiliado.nome} | Valor Pago: R${pagamento.valorPago:.2f}")

class ControllerRelatorio:
    def __init__(self, tela, controller_venda, controller_pagamento, controller_afiliado):
        self.__tela = tela
        self.__controller_venda = controller_venda
        self.__controller_pagamento = controller_pagamento
        self.__controller_afiliado = controller_afiliado

    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.gerar_relatorio_vendas()
            elif opc == '2':
                self.gerar_relatorio_financeiro()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

    def gerar_relatorio_vendas(self):
        try:
            dados = self.__tela.ler_dados()
            data_inicial, data_final, afiliado_id = dados

            afiliado = None
            if afiliado_id is not None:
                for a in self.__controller_afiliado.afiliado_DAO.get_all():
                    if a.id == afiliado_id:
                        afiliado = a
                        break
                if afiliado is None and afiliado_id is not None:
                    raise EntidadeNaoEncontradaException("Afiliado", afiliado_id)
            
            relatorio = Relatorio((data_inicial, data_final), afiliado)
            vendas_filtradas = relatorio.gerarRelatorioVendas(self.__controller_venda.venda_DAO.get_all())
            self.__tela.mostrar_relatorio_vendas(vendas_filtradas)
        except Exception as e:
            print(f"Erro ao gerar relatório de vendas: {e}")

    def gerar_relatorio_financeiro(self):
        try:
            dados = self.__tela.ler_dados()
            data_inicial, data_final, afiliado_id = dados

            afiliado = None
            if afiliado_id is not None:
                for a in self.__controller_afiliado.afiliado_DAO.get_all():
                    if a.id == afiliado_id:
                        afiliado = a
                        break
                if afiliado is None and afiliado_id is not None:
                    raise EntidadeNaoEncontradaException("Afiliado", afiliado_id)
            
            relatorio = Relatorio((data_inicial, data_final), afiliado)
            pagamentos_filtrados = relatorio.gerarRelatorioFinanceiro(self.__controller_pagamento.pagamento_DAO.get_all())
            self.__tela.mostrar_relatorio_financeiro(pagamentos_filtrados)
        except Exception as e:
            print(f"Erro ao gerar relatório financeiro: {e}")

class ControllerSistema:
    __instance = None
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
        sg.ChangeLookAndFeel('Reddit')
        layout = [
                        [sg.Text('Escolha uma opção')],
                        [sg.Radio('Gerenciar Produtos', "RD1", default = False, key='1')],
                        [sg.Radio('Gerenciar Afiliados', "RD1", default = False, key='2')],
                        [sg.Radio('Gerenciar Vendas', "RD1", default = False, key='3')],
                        [sg.Radio('Gerenciar Pagamentos', "RD1", default = False, key='4')],
                        [sg.Radio('Gerenciar Relatório', "RD1", default = False, key='5')],
                        [sg.Submit('Confirmar'), sg.Cancel('Cancelar')]
            ]
        
        self.__window = sg.Window('Sistema Financeiro de Afiliados').Layout(layout)
    def executar(self):
        while True:
            button, key = self.__window.Read()
            if button == 'Confirmar':
                if key['1'] == True:
                    self.__window.Close()
                    self.__controller_produto.executar()
                elif key['2'] == True:
                    self.__controller_afiliado.executar()
                elif key['3'] == True:
                    self.__window.Close()
                    self.__controller_venda.executar()
                elif key['4'] == True:
                    self.__window.Close()
                    self.__controller_pagamento.executar()
                elif key['5'] == True:
                    self.__window.Close()
                    self.__controller_relatorio.executar()
            elif button == 'Cancelar':
                print("Encerrando...")
                break
            else:
                sg.popup("opção invalida!")

sistema = ControllerSistema()
sistema.executar()