.PHONY: build lint serve lint-serve stop

# Constrói a imagem (necessário apenas na primeira vez)
build:
	docker compose build

# Executa o Lint e gera o relatório em reports/index.html
lint:
	docker compose run --rm lint

# Sobe o servidor web na porta 8080
serve:
	docker compose up -d web
	@echo "Acesse: http://localhost:8080"

# Executa Lint e já sobe o servidor em sequência
lint-serve: lint serve

# Para todos os containers
stop:
	docker compose down
