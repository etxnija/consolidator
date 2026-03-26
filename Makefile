# North Star Consolidator — developer convenience targets
# Usage: make demo
#
# Requires: docker compose (or podman with docker-compose shim)

.PHONY: demo up down seed logs

# One-click demo: bring up a fresh stack and seed it with the 3-entity group.
demo:
	@echo "=== North Star Consolidator: one-click demo ==="
	@$(MAKE) up
	@echo ""
	@echo "=== Seeding demo data ==="
	@bash demo/seed.sh
	@echo ""
	@echo "=== Done ==="
	@echo "  Dashboard: http://localhost:8501"
	@echo "  API docs:  http://localhost:8000/docs"

# Bring the full stack up (fresh volumes).
up:
	docker compose down -v 2>/dev/null || true
	docker compose up -d
	@echo "Waiting for services to become healthy..."
	@timeout 90 bash -c 'until docker compose ps | grep -E "healthy.*backend"; do sleep 2; done' \
		|| (echo "ERROR: services did not become healthy in 90s" && docker compose ps && exit 1)

down:
	docker compose down -v

seed:
	bash demo/seed.sh

logs:
	docker compose logs -f
