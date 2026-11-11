PY ?= python3
IN ?= data/tickets_valid.jsonl
OUT ?= out/pred.jsonl
PORT ?= 8000

.PHONY: install train predict eval serve test suggest all

install:
	$(PY) -m pip install -r requirements.txt

# Слабая разметка train + классификатор + база знаний (~4-6 минут на CPU)
train:
	$(PY) scripts/train.py --train data/tickets_train.jsonl.gz --out models

models/classifier.pkl:
	$(PY) scripts/train.py --train data/tickets_train.jsonl.gz --out models

# make predict IN=tickets.jsonl OUT=pred.jsonl (если моделей нет, сначала обучит их автоматически)
predict: models/classifier.pkl
	$(PY) scripts/predict.py --in $(IN) --out $(OUT)

# Метрики на валидации и ручной разметке -> reports/
eval:
	$(PY) scripts/eval_gold.py reports/gold_manual_120.json
	$(PY) scripts/eval_gold.py reports/gold_holdout_70.json
	$(PY) scripts/predict.py --in data/tickets_valid.jsonl --out out/pred_valid.jsonl
	$(PY) scripts/evaluate.py --pred out/pred_valid.jsonl --data data/tickets_valid.jsonl

serve: models/classifier.pkl
	uvicorn app:app --host 0.0.0.0 --port $(PORT)

test:
	$(PY) -m pytest -q tests

# Бонус: кандидаты в новые шаблоны по кластерам похожих обращений -> reports/template_suggestions.md
suggest: models/classifier.pkl
	$(PY) scripts/suggest_templates.py --kind report

all: train eval
