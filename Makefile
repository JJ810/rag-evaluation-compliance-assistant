.PHONY: setup format lint type test coverage ingest eval api ui docker-build docker-up clean

setup:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

format:
	python -m ruff format .

lint:
	python -m ruff check .
	python -m ruff format --check .

type:
	python -m mypy src scripts tests

test:
	python -m pytest

coverage:
	python -m pytest --cov=rag_compliance_assistant --cov-report=term-missing --cov-report=html

ingest:
	python scripts/ingest.py

eval:
	python scripts/run_eval.py

api:
	python -m uvicorn rag_compliance_assistant.api.main:app --host 0.0.0.0 --port 8000 --reload

ui:
	python -m streamlit run src/rag_compliance_assistant/ui/app.py

docker-build:
	docker build -t enterprise-rag-compliance-assistant:local .

docker-up:
	docker compose up --build

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(path, ignore_errors=True) for path in ['.pytest_cache','.mypy_cache','.ruff_cache','htmlcov']]; [path.unlink(missing_ok=True) for path in pathlib.Path('data/vector_store').glob('*.json')]; [path.unlink(missing_ok=True) for path in pathlib.Path('reports/eval').glob('*.json')]"
