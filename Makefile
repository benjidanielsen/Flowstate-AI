.PHONY: up down logs rebuild pause resume status seed

up:
	docker compose up -d
	@echo "Dashboard: http://localhost:3333"
	@echo "Orchestrator: http://localhost:8088"
	@echo "Memory: http://localhost:8080"
	@echo "SWE-agent: http://localhost:8086"

rebuild:
	docker compose up -d --build
	docker compose logs -f orchestrator

down:
	docker compose down

logs:
	docker compose logs -f

pause:
	touch ops/PAUSE || true

resume:
	rm -f ops/PAUSE || true

status:
	@ls -l ops/PAUSE 2>/dev/null || echo "Not paused"

seed:
	curl -s -X POST http://localhost:8088/seed || true
