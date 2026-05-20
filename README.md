# Android Lint — Analisador de Acessibilidade

Ferramenta para análise de acessibilidade em layouts Android XML usando o Android Lint. Desenvolvida para a aula prática do estágio de docência.

---

## Pré-requisitos

Antes de começar, instale:

- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

Após instalar o Docker Desktop, abra o programa e deixe ele rodando antes de continuar.

---

## Passo a passo

### 1. Clonar o repositório

Abra o terminal (PowerShell no Windows, Terminal no Mac/Linux) e execute:

```bash
git clone https://github.com/leonardoquezado/aula_pratica_lint.git
```

### 2. Entrar na pasta do projeto

```bash
cd aula_pratica_lint
```

### 3. Construir o projeto

Na primeira vez, o Docker vai baixar o Android SDK e preparar o ambiente. Isso leva cerca de **10 minutos** dependendo da sua conexão.

```bash
docker compose build
```

### 4. Iniciar o servidor

```bash
docker compose up
```

Aguarde até aparecer no terminal:

```
* Running on http://0.0.0.0:8080
```

### 5. Acessar no navegador

Abra o navegador e acesse:

```
http://localhost:8080
```

---

## Como usar

1. Cole o código XML de um layout Android no campo de texto
2. Clique em **Analisar com Lint**
3. Aguarde cerca de 1 a 3 minutos
4. O relatório aparece automaticamente com os problemas de acessibilidade encontrados

---

## Parar o servidor

Para encerrar, volte ao terminal e pressione `Ctrl + C`.

---

## Atualizar o projeto

Se o projeto for atualizado durante a aula, execute:

```bash
git pull
docker compose up --build
```

---

## Problemas comuns

**O Docker não inicia**
Verifique se o Docker Desktop está aberto e em execução antes de rodar os comandos.

**A página não carrega**
Verifique se o terminal mostra `Running on http://0.0.0.0:8080`. Se não aparecer, aguarde mais alguns segundos.

**Erro ao rodar `docker compose build`**
Verifique sua conexão com a internet. O build baixa o Android SDK e pode falhar em conexões instáveis.
