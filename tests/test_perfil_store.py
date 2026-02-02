import unittest
import tempfile
from pathlib import Path

from help_app.app.perfil_store import PerfilStoreJSON
from help_app.app.perfil import PerfilUtilizador


class TestPerfilStoreJSON(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.store = PerfilStoreJSON(self.dir)

    def tearDown(self):
        self.tmp.cleanup()

    def test_carregar_inexistente_cria_perfil(self):
        p = self.store.carregar("Micael")
        self.assertEqual(p.nome, "Micael")
        self.assertEqual(p.total_sessoes, 0)

    def test_guardar_e_recarregar(self):
        p = PerfilUtilizador(nome="Micael")
        p.registar_sessao("ansioso", 4)
        p.registar_sessao("ansioso", 2)

        self.store.guardar(p)
        p2 = self.store.carregar("Micael")

        self.assertEqual(p2.nome, "Micael")
        self.assertEqual(p2.total_sessoes, 2)
        self.assertEqual(p2.contagem_estados.get("ansioso"), 2)
        self.assertAlmostEqual(p2.media_intensidade("ansioso"), 3.0, places=5)


if __name__ == "__main__":
    unittest.main()
