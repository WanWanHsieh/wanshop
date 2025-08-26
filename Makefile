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

# ===== Common settings =====
BACKEND_HOST := 127.0.0.1
BACKEND_PORT := 8000
BACKEND_LOG  := backend.log
BACKEND_PID  := backend.pid

# ===== Backend =====
backend-install:
	@echo "==> Creating Python venv and installing deps"
	python -m venv backend/.venv
	$(PY_ROOT) -m pip install --upgrade pip
	$(PIP_ROOT) install -r backend/requirements.txt

backend-run:
	@echo "==> Running FastAPI (http://$(BACKEND_HOST):$(BACKEND_PORT))"
	cd backend && $(PY_IN_BACKEND) -m uvicorn app.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

backend-start:
	@echo "==> Starting backend (detached)..."
	@mkdir -p backend
	cd backend && nohup $(PY_IN_BACKEND) -m uvicorn app.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT) \
		> $(BACKEND_LOG) 2>&1 & echo $$! > $(BACKEND_PID)
	@echo "   Backend log: backend/$(BACKEND_LOG)"
	@echo "   Backend pid: backend/$(BACKEND_PID)"

backend-stop:
	@echo "==> Stopping backend..."
	@if [ -f backend/$(BACKEND_PID) ]; then \
		PID=$$(cat backend/$(BACKEND_PID)); \
		echo "   kill $$PID"; \
		kill $$PID || true; \
		rm -f backend/$(BACKEND_PID); \
	else \
		echo "   No pid file: backend/$(BACKEND_PID)"; \
	fi

backend-shell:
	cd backend && $(PY_IN_BACKEND)

backend-clean-venv:
	@echo "==> Removing backend venv"
	@if [ -d "backend/.venv" ]; then rm -rf backend/.venv; fi

backend-log:
	@echo "==> Tailing backend log (Ctrl+C 離開)"
	@cd backend && ( touch $(BACKEND_LOG) && tail -f $(BACKEND_LOG) )

# ===== Frontend =====
frontend-install:
	cd frontend && yarn

frontend-run:
	cd frontend && yarn dev

# ===== Dev (run backend + frontend together) =====
dev: backend-start
	@echo "==> Starting backend (detached) and frontend..."
	cd frontend && npm run dev

.PHONY: backend-install backend-run backend-start backend-stop backend-shell backend-clean-venv backend-log frontend-install frontend-run dev

# Windows 專用：強殺 8000 連線的 python（用不到可刪）
kill-backend:
	@echo "==> Kill backend on 8000 (Windows)"
	-@tasklist | grep -i python.exe > NUL 2>&1 || true
	-@for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a

# *nix 環境
kill-backend-nix:
	-@fuser -k 8000/tcp || true

static:
	mkdir -p backend/app/static/uploads
# venv被佔線無法刪除
# taskkill /F /IM python.exe 2>NUL
# taskkill /F /IM uvicorn.exe 2>NUL

# port佔用查詢
# netstat -ano | findstr :$port
# taskkill //F //PID 13636