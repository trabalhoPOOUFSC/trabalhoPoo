from datetime import date
import pickle
from abc import ABC, abstractmethod


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
    def mostrar_menu(self):
        print("\n=== Menu Afiliados ===")
        print("1. Cadastrar afiliado")
        print("2. Listar afiliado")
        print("3. Modificar afiliado")
        print("4. Excluir afiliado")
        print("0. Voltar")
        return input("Escolha uma opção: ")
    
    def ler_dados(self):
        id = int(input("Id: ").strip())
        if not id:
            raise ValueError("Id é obrigatório e não pode ser vazio")
        nome = input("Nome: ").strip()
        if not nome:
            raise ValueError("Nome é obrigatório e nao pode ser vazio")
        contato = input("Contato: ").strip()
        if not contato:
            raise ValueError("Contato é obrigatório e não pode ser vazio")
        parent_id = input("Parent Id: ").strip()
        if not parent_id:
            parent_id = None

        return id, nome, contato, parent_id

    def mostrar_afiliado(self, info):
        print(f"Id: {info['id']} | Nome: {info['nome']} | contato: {info['contato']} | Parent Id: {info['parent']}")

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
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__listar()
            elif opc =='3':
                self.__modificar()
            elif opc == '4':
                self.__excluir()
            elif opc == '0':
                break
            else:
                print("Opção inválida!") # Fazer Exception
            
    def __cadastrar(self):
        try:
            dados = self.__tela.ler_dados()
            
            id, nome, contato, parent_id = dados
            parent = None

            for a in self.__afiliado_DAO.get_all():
                if a.id == id:
                    raise Exception("ID repetido")
                if parent_id and a.id == int(parent_id):
                    parent = a

            if parent_id and not parent:
                raise Exception("Afiliado não encontrado")

            afiliado = Afiliado(id, nome, contato, parent)

            self.__afiliado_DAO.add(afiliado)
            print("Afiliado cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")
    
    def __listar(self):
        afiliados = self.__afiliado_DAO.get_all()
        print("\n=== Lista de afiliado ===")
        if not afiliados:
            raise Exception("Afiliado não encontrado")
        else:
            for a in afiliados:
                if a.parent is None:
                    info = {'id': a.id, 'nome': a.nome, 'contato': a.contato, 'parent': None}
                else:
                    info = {'id': a.id, 'nome': a.nome, 'contato': a.contato, 'parent': a.parent.id}
                self.__tela.mostrar_afiliado(info)

    def __modificar(self):
        try:
            id = int(input("Digite o ID do afiliado que deseja modificar: ").strip())
            afiliado = None

            for a in self.__afiliado_DAO.get_all():
                if a.id == id:
                    afiliado = a
                    break
            if not afiliado:
                print("Afiliado não encontrado.")
                return

            print("Digite os novos dados do afiliado:")

            novo_nome = input("Nome: ").strip()
            if novo_nome:
                afiliado.nome = novo_nome

            novo_id = int(input("ID: ").strip())
            if novo_id:
                afiliado.id = novo_id
            novo_contato = input("Contato: ").strip()
            if novo_contato:
                afiliado.contato = novo_contato

            novo_parent_id = input("Parent atual: ").strip()

            if novo_parent_id:
                parent = None
                for a in self.__afiliado_DAO.get_all():
                    if a.id == int(novo_parent_id):
                        parent = a
                        break
                if not parent:
                    print("Afiliado parent não encontrado. Mantendo o atual.")
                else:
                    afiliado.parent = parent
            else:
                afiliado.parent = None
            print("Afiliado modificado com sucesso!")
        except Exception as e:
            print(f"Erro ao modificar afiliado: {e}")

    def __excluir(self):
        try:
            id = int(input("Digite o ID do afiliado que deseja excluir: ").strip())
            afiliado = None

            for a in self.__afiliado_DAO.get_all():
                if a.id == id:
                    afiliado = a
                    break

            if not afiliado:
                print("Afiliado não encontrado.")
                return

            for a in self.__afiliado_DAO.get_all():
                if a.parent == afiliado:
                    print(f"Não é possível excluir o afiliado {afiliado.nome} pois ele é parent de outro afiliado.")
                    return
            self.__afiliado_DAO.remove(afiliado.id)
            print("Afiliado excluído com sucesso!")

        except Exception as e:
            print(f"Erro ao excluir afiliado: {e}")

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
            raise ValueError("Código é obrigatório e não pode ser vazio")
        nome = input("Nome: ").strip()
        if not nome:
            raise ValueError("Nome é obrigatório e não pode ser vazio")
        descricao = input("Descrição: ").strip()
        if not descricao:
            raise ValueError("Descrição é obrigatória e não pode ser vazia")
        preco_str = input("Preço: ")
        try:
            preco = float(preco_str)
        except ValueError:
            raise ValueError("Preço deve ser numérico")
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
                    raise Exception("Código repetido")

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
                raise Exception("Produto não encontrado!")

            print("\nDeixe em branco para manter o valor atual")

            novo_codigo = input(f"Código atual ({produto.codigo}): ").strip()
            if novo_codigo:
                for p in self.__produto_DAO.get_all():
                    if p != produto and p.codigo == novo_codigo:
                        raise ValueError("Código já está em uso!")
                produto.codigo = novo_codigo

            novo_nome = input(f"Nome atual ({produto.nome}): ").strip()
            if novo_nome:
                produto.nome = novo_nome
                
            nova_desc = input(f"Descrição atual ({produto.descricao}): ").strip()
            if nova_desc:
                produto.descricao = nova_desc
                
            novo_preco = input(f"Preço atual ({produto.preco}): ").strip()
            if novo_preco:
                produto.preco = float(novo_preco)
            
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
                raise Exception("Produto não encontrado!")

            tem_venda = False
            if self.__controller_venda:
                for venda in self.__controller_venda.listaVendas:
                    if venda.produto == produto:
                        tem_venda = True
                        break
            
            if tem_venda:
                raise ValueError("Produto está vinculado a vendas!")
                
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
        id = int(input("Id: ").strip())
        if not id:
            raise ValueError("Id é obrigatório e não pode ser vazio")

        data_str = input("Data no formato AAAA-MM-DD: ").strip()
        data = date.fromisoformat(data_str)
        if not data:
            raise ValueError("Data é obrigatória e não pode ser vazia")

        afiliado_id = int(input("Id do Afiliado: ").strip())
        if not afiliado_id:
            raise ValueError("Afiliado é obrigatório e não pode ser vazio")

        produto_codigo = input("Código do Produto: ").strip()
        if not produto_codigo:
            raise ValueError("Produto é obrigatório e não pode ser vazio")

        quantidade_str = input("Quantidade: ").strip()
        if not quantidade_str:
            raise ValueError("Quantidade é obrigatória e não pode ser vazia")
        quantidade = int(quantidade_str)

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
                    raise Exception("Id repetido")
            id, data, afiliado_id, produto_codigo, quantidade = dados

            afiliado = None
            for a in self.__controller_afiliado.afiliado_DAO.get_all():
                if a.id == afiliado_id:
                    afiliado = a
                    break
            if afiliado is None:
                raise Exception("Afiliado não encontrado")

            produto = None
            for p in self.__controller_produto.produto_DAO.get_all():
                if p.codigo == produto_codigo:
                    produto = p
                    break
            if produto is None:
                raise Exception("Produto não encontrado")

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
                raise Exception("Venda não encontrada!")

            if venda.pagamento_afiliado == 'realizado':
                raise Exception('Não é permitido modificar venda com status pagamento realizado!')
                
            print("\nDeixe em branco para manter o valor atual")

            nova_data = input(f"Data atual ({venda.data}): ").strip()
            if nova_data:
                venda.data = date.fromisoformat(nova_data)

            novo_afiliado_id = input(f"ID Afiliado atual ({venda.afiliado.id}): ").strip()
            if novo_afiliado_id:
                afiliado = None
                for a in self.__controller_afiliado.afiliado_DAO.get_all():
                    if a.id == int(novo_afiliado_id):
                        afiliado = a
                        break
                if not afiliado:
                    raise ValueError("Afiliado não encontrado!")
                venda.afiliado = afiliado

            novo_produto_cod = input(f"Código Produto atual ({venda.produto.codigo}): ").strip()
            if novo_produto_cod:
                produto = None
                for p in self.__controller_produto.produto_DAO.get_all():
                    if p.codigo == novo_produto_cod:
                        produto = p
                        break
                if not produto:
                    raise ValueError("Produto não encontrado!")
                venda.produto = produto

            nova_qtde = input(f"Quantidade atual ({venda.quantidade}): ").strip()
            if nova_qtde:
                venda.quantidade = int(nova_qtde)

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
                raise Exception("Venda não encontrada!")
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
        id = int(input("Id: ").strip())
        if not id:
            raise ValueError("Id é obrigatório e não pode ser vazio")
        
        data_str = input("Data no formato AAAA-MM-DD: ").strip()
        data = date.fromisoformat(data_str)
        if not data:
            raise ValueError("Data é obrigatória e não pode ser vazia")

        afiliado_id = int(input("Id do Afiliado: ").strip())
        if not afiliado_id:
            raise ValueError("Afiliado é obrigatório e não pode ser vazio")
        
        valorPago = float(input("Valor Pago: ").strip())
        if not valorPago:
            raise ValueError("Valor pago é obrigatório e não pode ser vazio")
        
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
            raise ValueError("Data inicial é obrigatória e não pode ser vazia")
        data_inicial = date.fromisoformat(data_inicial_str)

        data_final_str = input("Data final (YYYY-MM-DD): ").strip()
        if not data_final_str:
            raise ValueError("Data final é obrigatória e não pode ser vazia")
        data_final = date.fromisoformat(data_final_str)

        afiliado_id_str = input("Id do Afiliado (opcional, deixe em branco para todos): ").strip()
        afiliado_id = None
        if afiliado_id_str:
            try:
                afiliado_id = int(afiliado_id_str)
            except ValueError:
                raise ValueError("Id do Afiliado deve ser um número inteiro")

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
                    raise Exception("Afiliado não encontrado")
            
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
                    raise Exception("Afiliado não encontrado")
            
            relatorio = Relatorio((data_inicial, data_final), afiliado)
            pagamentos_filtrados = relatorio.gerarRelatorioFinanceiro(self.__controller_pagamento.pagamento_DAO.get_all())
            self.__tela.mostrar_relatorio_financeiro(pagamentos_filtrados)
        except Exception as e:
            print(f"Erro ao gerar relatório financeiro: {e}")

class ControllerSistema:
    def __init__(self):
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
    
    def executar(self):
        while True:
            print("\n=== Sistema Financeiro de Afiliados ===")
            print("1. Gerenciar Produtos")
            print("2. Gerenciar Afiliados")
            print("3. Gerenciar Vendas")
            print("4. Gerenciar Pagamentos")
            print("5. Gerenciar Relatórios")
            print("0. Sair")
            opc = input("Escolha uma opção: ")
            if opc == '1':
                self.__controller_produto.executar()
            elif opc == '2':
                self.__controller_afiliado.executar()
            elif opc =='3':
                self.__controller_venda.executar()
            elif opc == '4':
                self.__controller_pagamento.executar()
            elif opc == '5':
                self.__controller_relatorio.executar()
            elif opc == '0':
                print("Encerrando...")
                break
            else:
                print("Opção inválida!")

sistema = ControllerSistema()
sistema.executar()