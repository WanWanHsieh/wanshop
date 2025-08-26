# Use bash shell on Git Bash
SHELL := /usr/bin/bash

# ===== OS-aware venv paths =====
ifeq ($(OS),Windows_NT)
	PY_ROOT := backend/.venv/Scripts/python.exe
	PIP_ROOT := backend/.venv/Scripts/pip.exe
	PY_IN_BACKEND := .venv/Scripts/python.exe
	PIP_IN_BACKEND := .venv/Scripts/pip.exe
else
	PY_ROOT := backend/.venv/bin/python
	PIP_ROOT := backend/.venv/bin/pip
	PY_IN_BACKEND := .venv/bin/python
	PIP_IN_BACKEND := .venv/bin/pip
endif

# ===== Backend =====
backend-install:
	@echo "==> Creating Python venv and installing deps"
	python -m venv backend/.venv
	$(PY_ROOT) -m pip install --upgrade pip
	$(PIP_ROOT) install -r backend/requirements.txt

backend-run:
	@echo "==> Running FastAPI (http://127.0.0.1:8000)"
	cd backend && $(PY_IN_BACKEND) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

backend-shell:
	cd backend && $(PY_IN_BACKEND)

backend-clean-venv:
	@echo "==> Removing backend venv"
	@if [ -d "backend/.venv" ]; then rm -rf backend/.venv; fi

# ===== Frontend =====
frontend-install:
	cd frontend && yarn

frontend-run:
	cd frontend && yarn dev

# ===== Dev (run backend + frontend together) =====
dev:
	@echo "==> Starting backend (background) and frontend..."
	# backend to background (works in Git Bash / Linux / macOS)
	cd backend && ($(PY_IN_BACKEND) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > ../.backend.log 2>&1 &)
	# then run frontend in current terminal
	cd frontend && npm run dev

.PHONY: backend-install backend-run backend-shell backend-clean-venv frontend-install frontend-run dev

# mkdir -p backend/app/static/uploads
static:
	mkdir -p backend/app/static/uploads


# venv被佔線無法刪除
# taskkill /F /IM python.exe 2>NUL
# taskkill /F /IM uvicorn.exe 2>NUL

# port佔用查詢
# netstat -ano | findstr :$port
# taskkill //F //PID 13636

