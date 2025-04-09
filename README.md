# API de Gestão de Participantes - Desafio de Estágio

Este projeto é uma API desenvolvida em Python utilizando o framework FastAPI. O objetivo é atender às etapas descritas em um desafio técnico de estágio, oferecendo um sistema para importação, listagem, atualização e exclusão de dados de participantes.

A API também implementa um endpoint que simula o funcionamento de um webhook, realizando o cálculo de idade com base em uma data de nascimento recebida automaticamente.

---

## Estrutura do Projeto

```
Processo-Seletivo-Wayv/
├── Teste/
│   ├── __pycache__/
│   ├── dados.db
│   ├── database.py
│   ├── main.py
│   └── models.py
├── Cadastros.xlsx
├── .gitattributes
└── README.md
```

---

## Tecnologias utilizadas

- Python 3.9
- FastAPI
- SQLite
- SQLAlchemy
- Pandas

---

## Como executar o projeto

1. Navegue até a pasta onde está o projeto:
```bash
cd Wayv-Processo-Seletivo/Teste
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o servidor FastAPI:
```bash
uvicorn main:app --reload
```

4. Acesse a documentação interativa:
```
http://127.0.0.1:8000/docs
```

---

## Arquivo Cadastros.xlsx

O arquivo `Cadastros.xlsx`, localizado na raiz do projeto, contém os dados dos participantes fornecidos pelo próprio PDF do processo seletivo. Ele pode ser utilizado para testar o endpoint de importação da planilha.

---

## Endpoints disponíveis

### POST `/upload-excel/`

Importa os dados da planilha Excel enviada. A planilha deve conter as seguintes colunas:

- Nome completo
- Data de Nascimento
- Sexo
- E-mail
- Celular (opcional)

O arquivo esperado deve ser do tipo `.xlsx`.

---

### GET `/participantes/`

Retorna todos os participantes cadastrados no banco.

Parâmetro opcional:
- `sexo` → Filtra por sexo. Exemplo: `/participantes?sexo=Feminino`

---

### PUT `/participantes/{id}`

Atualiza a data de nascimento de um participante com base no ID.

Exemplo de corpo JSON:

```json
{
  "nova_data": "2000-01-01"
}
```

---

### DELETE `/participantes/`

Remove todos os participantes da base de dados.

---

### POST `/webhook/`

Simula o funcionamento de um webhook, recebendo dados automaticamente de um formulário externo. Calcula a idade com base na data de nascimento fornecida.

Exemplo de entrada:
```json
{
  "form_id": "form123",
  "data_nascimento": "1999-05-10"
}
```

Resposta:
```json
{
  "form_id": "form123",
  "idade": 25
}
```

---

## Observações

- O banco de dados `dados.db` será criado automaticamente na primeira execução da API.
- O campo "Celular" pode estar ausente na planilha, mas é tratado de forma segura no código.
- O projeto está organizado em uma pasta chamada `Teste` dentro do diretório principal.