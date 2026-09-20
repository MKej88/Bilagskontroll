import pandas as pd

from gui import App


class DummyVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class FakeApp:
    def __init__(self):
        self.df = pd.DataFrame(
            {
                "Fakturanr": ["2024-A", "2025-B", "2025-C"],
                "Fakturadato": ["15.12.2024", "02.01.2025", "03.01.2025"],
            }
        )
        self.sample_size_var = DummyVar("3")
        self.year_var = DummyVar("2025")
        self._pdf_prompt_shown = True

    def _ensure_helpers(self):
        pass

    def render(self):
        pass


def test_make_sample_bare_inneholder_valgt_aar():
    app = FakeApp()

    App.make_sample(app)

    assert set(app.sample_df["Fakturadato"]) == {"02.01.2025", "03.01.2025"}


def test_make_sample_tillater_pdf_sporsmal_for_nytt_utvalg():
    app = FakeApp()

    App.make_sample(app)

    assert app._pdf_prompt_shown is False
