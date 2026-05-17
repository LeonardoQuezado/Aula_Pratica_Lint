.PHONY: build start stop

# Constrói a imagem (necessário apenas na primeira vez)
build:
	docker compose build

# Sobe a interface web em http://localhost:8080
start:
	docker compose up

# Para tudo
stop:
	docker compose down
