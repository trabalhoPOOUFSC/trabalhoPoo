from datetime import date

class Pessoa:
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
    def __init__(self, id, nome, contato):
        super().__init__(id, nome, contato)
        self.__vendas = []
        self.__referrals = []

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

    @property
    def referrals(self):
        return self.__referrals

    @referrals.setter
    def referrals(self, value):
        if not isinstance(value, list):
            raise TypeError("referrals deve ser uma lista de Afiliado")
        for item in value:
            if not isinstance(item, Afiliado):
                raise TypeError("Cada item em referrals deve ser do tipo Afiliado")
        self.__referrals = value

    def calcularComissao(self):
        pass

    def adicionarReferral(self, referral):
        if not isinstance(referral, Afiliado):
            raise TypeError("referral deve ser do tipo Afiliado")
        self.__referrals.append(referral)

class TelaAfiliado:
    def mostrar_menu(self):
        print("\n=== Menu Afiliados ===")
        print("1. Cadastrar afiliado")
        print("2. Adicionar afiliado referral")
        print("3. Listar afiliado")
        print("0. Voltar")
        return input("Escolha uma opção: ")
    
    def ler_dados(self, is_referral):
        id = int(input("Id: ").strip())
        if not id:
            raise ValueError("Id é obrigatório e não pode ser vazio")
        nome = input("Nome: ").strip()
        if not nome:
            raise ValueError("Nome é obrigatório e nao pode ser vazio")
        contato = input("Contato: ").strip()
        if not contato:
            raise ValueError("Contato é obrigatório e não pode ser vazio")
        parent_id = None
        if is_referral:
            parent_id = int(input("parent_id: ").strip())
            if not parent_id:
                raise ValueError("ID do afiliado 'pai' é obrigatório e não pode ser vazio")

        return id, nome, contato, parent_id

    def mostrar_afiliado(self, info):
        referrals = ', '.join(map(str, info['referrals']))
        print(f"Id: {info['id']} | Nome: {info['nome']} | contato: {info['contato']} | Referrals: {referrals}")

class ControllerAfiliado:
    def __init__(self, sistema, tela):
        self.__sistema = sistema
        self.__tela = tela

    @property
    def sistema(self):
        return self.__sistema
    
    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__cadastrar(referral=True)
            elif opc == '3':
                self.__listar()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")
            
    def __cadastrar(self, referral = False):
        try:
            dados = self.__tela.ler_dados(referral)
            id, nome, contato, parent_id = dados
            parent = None

            for a in self.__sistema.listaAfiliados:
                if a.id == id:
                    raise Exception("ID repetido")
                if referral and parent_id == a.id:
                    parent = a

            if referral and not parent:
                raise Exception("ID do afiliado 'pai' não encontrado")
            
            afiliado = Afiliado(id, nome, contato)
            if parent:
                parent.adicionarReferral(afiliado)
            self.__sistema.cadastrarAfiliado(afiliado)
            print("Afiliado cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")
    
    def __listar(self):
        afiliados = self.__sistema.listaAfiliados
        print("\n=== Lista de afiliado ===")
        if not afiliados:
            print("Nenhum afiliado cadastrado.")
        else:
            for a in afiliados:
                referrals = []
                for r in a.referrals:
                    referrals.append(r.id)
                info = {'id': a.id, 'nome': a.nome, 'contato': a.contato, 'referrals': referrals}
                self.__tela.mostrar_afiliado(info)

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

class TelaProduto:
    def mostrar_menu(self):
        print("\n=== Menu Produtos ===")
        print("1. Cadastrar produto")
        print("2. Listar produtos")
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
    def __init__(self, sistema, tela):
        self.__sistema = sistema
        self.__tela = tela

    @property
    def sistema(self):
        return self.__sistema

    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__listar()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

    def __cadastrar(self):
        try:
            dados = self.__tela.ler_dados()
            
            for item in self.__sistema.listaProdutos:
                if item.codigo == dados[0]:
                    raise Exception("Código repetido")

            produto = Produto(*dados)
            self.__sistema.cadastrarProduto(produto)
            print("Produto cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")

    def __listar(self):
        produtos = self.__sistema.listaProdutos
        print("\n=== Lista de Produtos ===")
        if not produtos:
            print("Nenhum produto cadastrado.")
        else:
            for p in produtos:
                info = {'codigo': p.codigo, 'nome': p.nome, 'descricao': p.descricao, 'preco': p.preco}
                self.__tela.mostrar_produto(info)

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

    def calcularTotal(self):
        self.__total = self.quantidade * self.produto.preco
        return self.__total

class TelaVenda:
    def mostrar_menu(self):
        print("\n=== Menu vendas ===")
        print("1. Registrar venda")
        print("2. Listar vendas")
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
        print(f"Id: {info['id']} | Data: {info['data']} | Afiliado: {info['afiliado']} | Produto: {info['produto']} | Quantidade: {info['quantidade']} | Total: R${info['total']}")
  
class ControllerVenda:
    def __init__(self, sistema, tela):
        self.__sistema = sistema
        self.__tela = tela

    @property
    def sistema(self):
        return self.__sistema

    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.__cadastrar()
            elif opc == '2':
                self.__listar()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

    def __cadastrar(self):
        try:
            dados = self.__tela.ler_dados()
            
            for item in self.__sistema.listaVendas:
                if item.id == dados[0]:
                    raise Exception("Id repetido")
            id, data, afiliado_id, produto_codigo, quantidade = dados

            afiliado = None
            for a in self.__sistema.listaAfiliados:
                if a.id == afiliado_id:
                    afiliado = a
                    break
            if afiliado is None:
                raise Exception("Afiliado não encontrado")

            produto = None
            for p in self.__sistema.listaProdutos:
                if p.codigo == produto_codigo:
                    produto = p
                    break
            if produto is None:
                raise Exception("Produto não encontrado")
            
            venda = Venda(id, data, a, p, quantidade)
            self.__sistema.registrarVenda(venda)
            print("Venda registrada com sucesso!")

        except Exception as e:
            print(f"Erro ao cadastrar: {e}")

    def __listar(self):
        vendas = self.__sistema.listaVendas
        print("\n=== Lista de Vendas ===")
        if not vendas:
            print("Nenhuma venda registrada.")
        else:
            for v in vendas:
                info = {'id': v.id, 'data': v.data, 'afiliado': v.afiliado.nome,
                        'produto': v.produto.nome, 'quantidade': v.quantidade,
                        'total': v.total}
                self.__tela.mostrar_venda(info)

class Comissao:
    def __init__(self, afiliado, venda, valorDireto, valorIndireto):
        if not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        if not isinstance(venda, Venda):
            raise TypeError("venda deve ser do tipo Venda")
        if not isinstance(valorDireto, (int, float)):
            raise TypeError("valorDireto deve ser numérico")
        if not isinstance(valorIndireto, (int, float)):
            raise TypeError("valorIndireto deve ser numérico")
        self.__afiliado = afiliado
        self.__venda = venda
        self.__valorDireto = float(valorDireto)
        self.__valorIndireto = float(valorIndireto)

    @property
    def afiliado(self):
        return self.__afiliado

    @afiliado.setter
    def afiliado(self, value):
        if not isinstance(value, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        self.__afiliado = value

    @property
    def venda(self):
        return self.__venda

    @venda.setter
    def venda(self, value):
        if not isinstance(value, Venda):
            raise TypeError("venda deve ser do tipo Venda")
        self.__venda = value

    @property
    def valorDireto(self):
        return self.__valorDireto

    @valorDireto.setter
    def valorDireto(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("valorDireto deve ser numérico")
        self.__valorDireto = float(value)

    @property
    def valorIndireto(self):
        return self.__valorIndireto

    @valorIndireto.setter
    def valorIndireto(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("valorIndireto deve ser numérico")
        self.__valorIndireto = float(value)

    def calcular(self):
        return self.valorDireto + self.valorIndireto

class Pagamento:
    def __init__(self, id, data, afiliado, valorPago, status):
        if not isinstance(id, int):
            raise TypeError("id deve ser int")
        if not isinstance(data, date):
            raise TypeError("data deve ser do tipo date")
        if not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        if not isinstance(valorPago, (int, float)):
            raise TypeError("valorPago deve ser numérico")
        if not isinstance(status, str):
            raise TypeError("status deve ser str")
        self.__id = id
        self.__data = data
        self.__afiliado = afiliado
        self.__valorPago = float(valorPago)
        self.__status = status

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

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if not isinstance(value, str):
            raise TypeError("status deve ser str")
        self.__status = value

    def processar(self):
        pass

class TelaPagamento:
    def mostrar_menu(self):
        print("\n=== Menu Pagamento ===")
        print("1. Pagar Afiliado")
        print("2. Pagar Todos Os Afiliados")
        print("3. Processar Pagamento")
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
        
        status = input("Status: ").strip()
        if not status:
            raise ValueError("Status é obrigatório e não pode ser vazio")
        return id, data, afiliado_id, valorPago, status
    
    def mostrar_pagamento(self, info):
        print(f"Id: {info['id']} | Data: {info['data']} | Valor Pago: {info['valorPago']} | status: {info['status']}")
    
class ControllerPagamento:
    def __init__(self, sistema, tela):
        self.__sistema = sistema
        self.__tela = tela
    
    @property
    def sistema(self):
        return self.__sistema
    
    def executar(self):
        while True:
            opc = self.__tela.mostrar_menu()
            if opc == '1':
                self.adicionar_pagamento()
            elif opc == '2':
                self.__listar()
            elif opc == '3':
                self.processar_pagamento()
            elif opc == '0':
                break
            else:
                print("Opção inválida!")

    def adicionar_pagamento(self):
        try:
            dados = self.__tela.ler_dados()
            
            for item in self.__sistema.listaPagamentos:
                    if item.id == dados[0]:
                        raise Exception("Id repetido")
            id, data, afiliado_id, valorPago, status = dados

            afiliado = None
            for a in self.__sistema.listaAfiliados:
                if a.id == afiliado_id:
                    afiliado = a
                    break
            if afiliado is None:
                raise Exception("Afiliado não encontrado")
            
            pagamento = Pagamento(id, data, afiliado, valorPago, status)
            self.__sistema.listaPagamentos.append(pagamento)
            print("Venda registrada com sucesso!")

        except Exception as e:
            print(f"Erro ao cadastrar: {e}")
    
    def __listar(self):
        pagamentos = self.__sistema.listaPagamentos
        print("\n=== Lista de Vendas ===")
        if not pagamentos:
            print("Nenhuma venda registrada.")
        else:
            for p in pagamentos:
                info = {'id': p.id, 'data': p.data, 'afiliado': p.afiliado.nome,
                         'valorPago': p.valorPago, 'status': p.status}
                self.__tela.mostrar_pagamento(info)

    # fazer
    def processar_pagamento(self):
        valorTotalPagamentos = 0
        for pagamento in self.__sistema.listaPagamentos:
            pagamento.processar()
            valorTotalPagamentos += pagamento.valorPago
            print("Pagamento processado com sucesso!")
            return

class SistemaFinanceiroAfiliados:
    def __init__(self):
        self.__listaAfiliados = []
        self.__listaProdutos = []
        self.__listaVendas = []
        self.__listaPagamentos = []

    @property
    def listaAfiliados(self):
        return self.__listaAfiliados

    @listaAfiliados.setter
    def listaAfiliados(self, value):
        if not isinstance(value, list):
            raise TypeError("listaAfiliados deve ser uma lista de Afiliado")
        for item in value:
            if not isinstance(item, Afiliado):
                raise TypeError("Cada item em listaAfiliados deve ser do tipo Afiliado")
        self.__listaAfiliados = value

    @property
    def listaProdutos(self):
        return self.__listaProdutos

    @listaProdutos.setter
    def listaProdutos(self, value):
        if not isinstance(value, list):
            raise TypeError("listaProdutos deve ser uma lista de Produto")
        for item in value:
            if not isinstance(item, Produto):
                raise TypeError("Cada item em listaProdutos deve ser do tipo Produto")
        self.__listaProdutos = value

    @property
    def listaVendas(self):
        return self.__listaVendas

    @listaVendas.setter
    def listaVendas(self, value):
        if not isinstance(value, list):
            raise TypeError("listaVendas deve ser uma lista de Venda")
        for item in value:
            if not isinstance(item, Venda):
                raise TypeError("Cada item em listaVendas deve ser do tipo Venda")
        self.__listaVendas = value

    @property
    def listaPagamentos(self):
        return self.__listaPagamentos

    @listaPagamentos.setter
    def listaPagamentos(self, value):
        if not isinstance(value, list):
            raise TypeError("listaPagamentos deve ser uma lista de Pagamento")
        for item in value:
            if not isinstance(item, Pagamento):
                raise TypeError("Cada item em listaPagamentos deve ser do tipo Pagamento")
        self.__listaPagamentos = value

    def cadastrarAfiliado(self, afiliado):
        if not isinstance(afiliado, Afiliado):
            raise TypeError("afiliado deve ser do tipo Afiliado")
        self.__listaAfiliados.append(afiliado)

    def cadastrarProduto(self, produto):
        if not isinstance(produto, Produto):
            raise TypeError("produto deve ser do tipo Produto")
        self.__listaProdutos.append(produto)

    def registrarVenda(self, venda):
        if not isinstance(venda, Venda):
            raise TypeError("venda deve ser do tipo Venda")
        self.__listaVendas.append(venda)
        venda.afiliado.vendas.append(venda)

    def calcularComissoes(self):
        pass

    def processarPagamentos(self):
        pass

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

    def gerarRelatorioVendas(self):
        pass

    def gerarRelatorioFinanceiro(self):
        pass

class TelaRelatorio:
    def mostrar_menu(self):
        print("\n=== Menu Relatórios ===")
        print("1. Gerar Relatório de Vendas")
        print("2. Gerar Relatório Financeiro")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def ler_dados(self):
        data_inicial_str = input("Data inicial (YYYY-MM-DD): ").strip()
        if not data_inicial_str:
            raise ValueError("Data inicial é obrigatório e não pode ser vazio")
        data_inicial = date.fromisoformat(data_inicial_str)

        data_final_str = input("Data final (YYYY-MM-DD): ").strip()
        if not data_final_str:
            raise ValueError("Data final é obrigatório e não pode ser vazio")
        data_final = date.fromisoformat(data_final_str)

        afiliado_id = int(input("Id do Afiliado: ").strip())
        if not afiliado_id:
            raise ValueError("Id do Afiliado é obrigatório e não pode ser vazio")

        return data_inicial, data_final, afiliado_id
    
    def mostrar_relatorio_vendas(self, vendas):
        print("\n=== Relatório de Vendas ===")
        if not vendas:
            print("Nenhuma venda no período.")
            return
        for venda in vendas:
            print(f"Venda ID: {venda.id} | Data: {venda.data} | Afiliado: {venda.afiliado.nome} | Valor: {venda.valor}")

    def mostrar_relatorio_financeiro(self, pagamentos):
        print("\n=== Relatório Financeiro ===")
        if not pagamentos:
            print("Nenhum pagamento no período.")
            return
        for pagamento in pagamentos:
            print(f"Pagamento ID: {pagamento.id} | Data: {pagamento.data} | Afiliado: {pagamento.afiliado.nome} | "
                  f"Valor: {pagamento.valorPago} | Status: {pagamento.status}")
    
class ControllerRelatorio:
    def __init__(self, sistema, tela):
        self.__sistema = sistema
        self.__tela = tela

    @property
    def sistema(self):
        return self.__sistema
    
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
            for a in self.__sistema.listaAfiliados:
                if a.id == afiliado_id:
                    afiliado = a
                    break
            if afiliado is None:
                raise Exception("Afiliado não encontrado")
            
            relatorio = Relatorio((data_inicial, data_final), afiliado)
            vendas = relatorio.gerarRelatorioVendas()
            self.__tela.mostrar_relatorio_vendas(vendas)
        except Exception as e:
            print(f"Erro ao gerar relatório de vendas: {e}")

    def gerar_relatorio_financeiro(self):
        try:
            dados = self.__tela.ler_dados()
            data_inicial, data_final, afiliado_id = dados

            afiliado = None
            for a in self.__sistema.listaAfiliados:
                if a.id == afiliado_id:
                    afiliado = a
                    break
            if afiliado is None:
                raise Exception("Afiliado não encontrado")
            
            relatorio = Relatorio((data_inicial, data_final), afiliado)
            pagamentos = relatorio.gerarRelatorioFinanceiro()
            self.__tela.mostrar_relatorio_financeiro(pagamentos)
        except Exception as e:
            print(f"Erro ao gerar relatório financeiro: {e}")

class ControladorSistema:
    """Controlador Geral: Gerencia todos os controllers do sistema."""
    def __init__(self):
        self.__sistema = SistemaFinanceiroAfiliados()
        self.__controller_produto = ControllerProduto(self.__sistema, TelaProduto())
        self.__controller_afiliado = ControllerAfiliado(self.__sistema, TelaAfiliado())
        self.__controller_venda = ControllerVenda(self.__sistema, TelaVenda())
        self.__controller_pagamento = ControllerPagamento(self.__sistema, TelaPagamento())
        self.__controller_relatorio = ControllerRelatorio(self.__sistema, TelaRelatorio())

    @property
    def sistema(self):
        return self.__sistema
    
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

'''
def testar__sistema():
    print("\n=== Teste Afiliado ===")
    afiliado_pai = Afiliado(1, "Carlos", "carlos@email.com")
    afiliado_filho = Afiliado(2, "Ana", "ana@email.com", afiliado_pai)
    afiliado_pai.adicionarReferral(afiliado_filho)
    if afiliado_filho.parent.id == 1:
        print("Passou: Afiliado filho tem parent correto")
    else:
        print("Falhou: Parent incorreto")
    if len(afiliado_pai.referrals) == 1:
        print("Passou: Referral adicionado")
    else:
        print("Falhou: Erro ao adicionar referral")

    print("\n=== Teste Produto ===")
    produto = Produto("P1", "Livro", "Livro Python", 50.0)
    if produto.preco == 50.0:
        print("Passou: Preço inicial correto")
    else:
        print("Falhou: Preço inicial errado")
    produto.preco = 60.0
    if produto.preco == 60.0:
        print("Passou: Atualização de preço")
    else:
        print("Falhou: Preço não atualizou")

    print("\n=== Teste Venda ===")
    venda = Venda(1, date(2024, 1, 1), afiliado_pai, produto, 2)
    if venda.total == 120.0:
        print("Passou: Cálculo inicial correto")
    else:
        print(f"Falhou: Total esperado 120.0, obtido {venda.total}")
    venda.quantidade = 3
    if venda.total == 180.0:
        print("Passou: Atualização de quantidade")
    else:
        print(f"Falhou: Total esperado 180.0, obtido {venda.total}")

    print("\n=== Teste Comissão ===")
    comissao = Comissao(afiliado_pai, venda, 5.0, 2.0)
    if comissao.calcular() == 7.0:
        print("Passou: Cálculo de comissão")
    else:
        print(f"Falhou: Comissão esperada 7.0, obtida {comissao.calcular()}")

    print("\n=== Teste Pagamento ===")
    pagamento = Pagamento(1, date(2024, 1, 1), afiliado_pai, 100.0, "pendente")
    pagamento.processar()
    if pagamento.status == "pendente":
        print("Passou: Pagamento não foi processado (método com pass)")
    else:
        print(f"Falhou: Status obtido {pagamento.status}")

    print("\n=== Teste Sistema ===")
    sistema = SistemaFinanceiroAfiliados()
    sistema.cadastrarAfiliado(afiliado_pai)
    sistema.cadastrarProduto(produto)
    sistema.registrarVenda(venda)
    if len(sistema.listaAfiliados) == 1:
        print("Passou: Afiliado cadastrado")
    else:
        print(f"Falhou: {len(sistema.listaAfiliados)} afiliados")
    if len(sistema.listaProdutos) == 1:
        print("Passou: Produto cadastrado")
    else:
        print(f"Falhou: {len(sistema.listaProdutos)} produtos")
    if len(sistema.listaVendas) == 1:
        print("Passou: Venda registrada")
    else:
        print(f"Falhou: {len(sistema.listaVendas)} vendas")
    comissoes = sistema.calcularComissoes()
    if comissoes is None:
        print("Passou: Método calcularComissoes sem lógica (pass)")
    else:
        print("Falhou: Método calcularComissoes não deveria retornar valor")
    sistema.processarPagamentos()
    if len(sistema.listaPagamentos) == 0:
        print("Passou: Método processarPagamentos sem lógica (pass)")
    else:
        print("Falhou: Pagamentos processados inesperadamente")

    print("\n=== Teste Relatorio ===")
    periodo = (date(2023, 1, 1), date(2025, 1, 1))
    relatorio = Relatorio(periodo, afiliado_pai)
    vendas_relatorio = relatorio.gerarRelatorioVendas()
    rel_financeiro = relatorio.gerarRelatorioFinanceiro()
    if vendas_relatorio is None:
        print("Passou: Método gerarRelatorioVendas sem lógica (pass)")
    else:
        print("Falhou: Método gerarRelatorioVendas não deveria retornar valor")
    if rel_financeiro is None:
        print("Passou: Método gerarRelatorioFinanceiro sem lógica (pass)")
    else:
        print("Falhou: Método gerarRelatorioFinanceiro não deveria retornar valor")

    print("\n=== Teste MVC Produto ===")
    sistema2 = SistemaFinanceiroAfiliados()
    controller2 = ControllerProduto(sistema2, TelaProduto())
    # simula opção 0 para sair imediatamente
    orig_input = __builtins__.input
    __builtins__.input = lambda prompt='': '0'
    try:
        controller2.executar()
        print("Passou: ControllerProduto.executar com opção '0' encerra sem erro")
    except Exception as e:
        print(f"Falhou: ControllerProduto.executar levantou exceção {e}")
    __builtins__.input = orig_input

    # === Teste ControladorSistema ===
    print("\n=== Teste ControladorSistema ===")
    cs = ControladorSistema()
    if isinstance(cs.sistema, SistemaFinanceiroAfiliados):
        print("Passou: ControladorSistema inicializa SistemaFinanceiroAfiliados")
    else:
        print("Falhou: Sistema não inicializado corretamente")
    if cs.controller_produto.sistema is cs.sistema:
        print("Passou: ControllerProduto está vinculado ao mesmo sistema")
    else:
        print("Falhou: ControllerProduto não vinculado ao sistema")

if __name__ == "__main__":
    testar__sistema()
'''


aa = ControladorSistema()
aa.executar()