<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:4e9f3d,100:1e5128&height=140&section=header&text=Square%20Cloud%20Manager&fontSize=35&fontColor=ffffff&animation=fadeIn" />
</p>

<p align="center">
  <b>Gerencie suas aplicações da Square Cloud direto pelo Discord!</b>
</p>

---

## 📌 Sobre o Projeto

O **Square Cloud Manager** é um bot em **Python** que permite gerenciar suas aplicações hospedadas na [Square Cloud](https://squarecloud.app/pt-br) diretamente pelo Discord.
**Este projeto não É OFICIAL da Square Cloud. Este projeto é desenvolvido da comunidade para a comunidade.**

Com ele você pode:

- 📦 Gerenciar **Aplicações** (Bots, Sites, Databases, etc.)
- 🗂️ Gerenciar **Blob** *(em desenvolvimento)*
- 🧠 Gerenciar **Área de Trabalho** *(em desenvolvimento)*
- 👤 Visualizar seu **Perfil**

> ⚠️ Atualmente, **Blob** e **Área de Trabalho** ainda estão em desenvolvimento.

---

## ⚙️ Instalação

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/GussApenass/SquareCloud-Manager
cd SquareCloud-Manager
````

### 2️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure o `.env`

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SQUARE_CLOUD_TOKEN= # Seu token da square cloud obtido em: https://squarecloud.app/pt-br/account/security
BOT_TOKEN= # Token do seu bot
APPLICATION_ID= # ID de seu bot
```

---

## 🤖 Configuração do Bot (IMPORTANTE)

Este bot **deve ser instalado como User Install**, e não como Guild Install.
Em outras palavras, mesmo adicionando ele em um servidor, ele **não irá carregar os comandos**. Para que os comandos sejam carregados, é necessário ele ser instalado como **User Install**.

Siga os passos abaixo:

### 1️⃣ Mude de Guild Install para User Install

![Passo 1](https://i.postimg.cc/GtP9QP3K/1.png)

### 2️⃣ Coloque Install Link como None

![Passo 2](https://i.postimg.cc/sxP1cPfc/2.png)

### 3️⃣ Desative Public Bot

![Passo 3](https://i.postimg.cc/5y5j359S/3.png)

### 4️⃣ Gere o link com `application.commands` ativado

![Passo 4](https://i.postimg.cc/nrKMkKV1/4.png)

### 5️⃣ Mude o Integration Type para User Install e copie o link

![Passo 5](https://i.postimg.cc/QCgVbgN0/5.png)

---

## 🚀 Executando o Projeto

```bash
python main.py
```

---

## 🤝 Contribuição

Contribuições são muito bem-vindas!

Para contribuir:

- Siga boas práticas de desenvolvimento
- Mantenha o padrão de código já existente
- Escreva código limpo e organizado
- Evite quebrar funcionalidades existentes
- Documente alterações relevantes

Se for abrir um Pull Request, explique claramente o que foi alterado.

---

## 📜 Licença

Este projeto está sob a licença **GNU General Public License v3.0**.

---

## 💡 Créditos

A ideia deste projeto foi inspirada na série de manager do canal:

**Rincko Dev**
Canal: [youtube.com/@rinckodev](https://youtube.com/@rinckodev)
Série:
[youtube.com/watch?v=aW4mwveHyjw&list=PL9tY_tDo_Q0AmNx52XD8O2gpEuNtiaxC6](https://www.youtube.com/watch?v=aW4mwveHyjw&list=PL9tY_tDo_Q0AmNx52XD8O2gpEuNtiaxC6)

---

***Made with ❤️ by GussApenass***

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e5128,100:4e9f3d&height=140&section=footer" />
</p>
