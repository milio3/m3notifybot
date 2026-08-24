"""Tests para los endpoints de salud (/health y /ready)."""


def test_health_retorna_200(client):
    """GET /health debe devolver 200 y status ok."""
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["status"] == "ok"
    assert "version" in datos


def test_ready_retorna_200(client):
    """GET /ready debe devolver 200 cuando la BD está disponible."""
    respuesta = client.get("/ready")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["status"] == "ready"
    assert datos["database"] == "connected"
