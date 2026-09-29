# Encante Pratas

Sistema web de loja de acessórios em prata, desenvolvido em Django (Python), com CRUDs completos, autenticação, controle de permissões por grupo e fluxo de compra (carrinho → checkout → pagamento simulado).

## Tecnologias

- Python 3.14
- Django 5.2.13
- Pillow (upload de imagens de produto)
- Bootstrap 5 (via CDN)
- Banco de dados: SQLite (padrão de desenvolvimento)

## Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/) instalado
- Git instalado

## Como clonar e rodar o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/<usuario>/Encante-Pratas.git
cd Encante-Pratas/encantepratas
```

### 2. Criar e ativar o ambiente virtual (venv)

**Windows (PowerShell):**
```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você vai saber que a venv está ativa quando aparecer `(venv)` no início da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar as migrations (criar o banco de dados)

```bash
python manage.py migrate
```

### 5. Criar o superusuário inicial

```bash
python manage.py createsuperuser
```

Preencha usuário, e-mail (pode deixar em branco) e senha quando solicitado.

### 6. Rodar o servidor

```bash
python manage.py runserver
```

Acesse: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Configuração inicial de permissões (obrigatória para testar o sistema completo)

O sistema usa dois grupos de acesso, que precisam ser criados manualmente uma vez, pelo admin (`http://127.0.0.1:8000/admin/`, logando com o superusuário criado no passo 5):

### Grupo "Gestão" (equipe da loja)

Em **Authentication and Authorization → Groups → Add group**, crie o grupo `Gestão` e marque as permissões de **Can add / change / delete / view** para os models: `Categoria`, `Produto`, `Usuario`, `Pedido`, `Pagamento` (20 permissões no total).

Depois, edite o usuário que vai representar a loja (pode ser o próprio superusuário ou outro), e adicione ele ao grupo `Gestão`.

### Grupo "Clientes" (compradores)

Crie o grupo `Clientes` e marque apenas:
- Can view Categoria
- Can view Produto
- Can add Pedido
- Can add Pagamento

> Esse grupo é atribuído **automaticamente** a qualquer pessoa que se cadastrar pelo formulário público (`/usuarios/novo/`) — não precisa adicionar manualmente.

## Testando o sistema

- **Catálogo público** (sem login): `/produtos/`, `/categorias/`
- **Cadastro de cliente**: `/usuarios/novo/`
- **Login**: `/usuarios/login/`
- **Carrinho e compra** (como cliente logado): navegue até um produto → "Adicionar ao carrinho" ou "Comprar agora" → `/pedidos/carrinho/` → "Finalizar compra"
- **Gestão de catálogo/pedidos** (como usuário do grupo Gestão): `/categorias/nova/`, `/produtos/novo/`, `/pedidos/`, `/pagamentos/`
- **Django Admin**: `/admin/`

## Estrutura do projeto
