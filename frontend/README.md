# Sistema de Triagem - Frontend Next.js

Este é o frontend do Sistema de Triagem baseado no Protocolo de Manchester, desenvolvido com Next.js.

## Requisitos

- Node.js 14+
- npm ou yarn

## Instalação

1. Instale as dependências:
```bash
# Com npm
npm install

# Com yarn
yarn install
```

## Executando o servidor de desenvolvimento

```bash
# Com npm
npm run dev

# Com yarn
yarn dev
```

O servidor estará disponível em `http://localhost:3000`.

## Construindo para produção

```bash
# Com npm
npm run build
npm start

# Com yarn
yarn build
yarn start
```

## Estrutura do projeto

- `pages/`: Páginas da aplicação
  - `index.js`: Página principal de triagem
  - `admin/`: Área administrativa
    - `index.js`: Página de login
    - `dashboard/`: Dashboard administrativo
- `components/`: Componentes reutilizáveis
- `styles/`: Arquivos de estilo
- `public/`: Arquivos estáticos

## Funcionalidades

- **Página principal**: Interface para inserção de sintomas e visualização da classificação de triagem
- **Área administrativa**: 
  - Login seguro
  - Dashboard com estatísticas
  - Visualização de triagens pendentes e validadas
  - Validação de triagens por especialistas
  - Exportação de dados