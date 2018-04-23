from roro.projects import Project

def test_server_url(monkeypatch):
    monkeypatch.setattr(Project, "SERVER_URL", "https://example.com")

    p = Project("test-project")
    assert p.client.server_url == "https://example.com"

    class ProjectSubClass(Project):
        SERVER_URL = "https://new.example.com"

    p = ProjectSubClass("test-project")
    assert p.client.server_url == "https://new.example.com"

