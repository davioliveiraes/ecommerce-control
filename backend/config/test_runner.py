from pathlib import Path

from django.test.runner import DiscoverRunner

APPS_DIR = Path(__file__).resolve().parent.parent / "apps"


class AppsTestRunner(DiscoverRunner):
    """Discovery default em `apps/` para evitar import duplicado dos models.

    Sem isso, `manage.py test` (sem args) caminha a partir de `backend/` e
    importa cada `apps/<app>/models/__init__.py` como `apps.<app>.models`,
    que não bate com `<app>` em INSTALLED_APPS e gera RuntimeError.
    """

    def __init__(self, *args, top_level=None, **kwargs):
        if top_level is None:
            top_level = str(APPS_DIR)
        super().__init__(*args, top_level=top_level, **kwargs)

    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = [str(APPS_DIR)]
        return super().build_suite(test_labels, **kwargs)
