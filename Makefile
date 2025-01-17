#export DOCKER_DEFAULT_PLATFORM=linux/amd64
up:
	docker compose -f docker-compose.yml up -d
up_re:
	docker compose -f docker-compose.yml up --build -d

down:
	docker compose -f docker-compose.yml down --remove-orphans

up_local:
	docker compose -f docker-compose.yml up -d postgres zookeeper kafka kafka-ui redis


mypy:
	@echo mypy .
	mypy . --exclude 'venv|migrations'

pytest:
	pytest -v -W ignore
	#pytest -s -vv app/tests/ --junitxml tests-unit-results.xml --cov=app --cov-report='xml:coverage-tests-unit.xml'

pre-commit:
	pre-commit run --all-files

docker_test:
	docker compose -f docker-compose-test.yml run --rm test
	#docker compose -f docker-compose-test.yml up  # если не удалят контейнер
