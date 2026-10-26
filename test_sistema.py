"""Testes do enunciado e verificações complementares. Executar com unittest."""

import unittest

from sistema import SistemaSenhas
from especialidades import CATEGORIAS_PRIORIDADE


class TesteSistemaSenhas(unittest.TestCase):
    def setUp(self):
        self.s = SistemaSenhas()
        self.s.cadastrar_especialidade("Clínica Geral")
        self.s.cadastrar_especialidade("Pediatria")
        self.s.cadastrar_especialidade("Cardiologia")

    def test_01_cadastro_maximo_tres_e_sem_duplicidade(self):
        self.assertEqual([x["codigo"] for x in self.s.listar_especialidades()],
                         ["C1", "C2", "C3"])
        with self.assertRaisesRegex(ValueError, "três"):
            self.s.cadastrar_especialidade("Ginecologia")
        with self.assertRaisesRegex(ValueError, "já foi"):
            self.s.cadastrar_especialidade("Clínica Geral")

    def test_02_emissao_cinco_normais_quatro_prioritarias(self):
        for i in range(5):
            codigo = ("C1", "C2", "C3")[i % 3]
            self.s.emitir_senha(codigo, "N")
        for i in range(4):
            codigo = ("C1", "C2", "C3")[i % 3]
            self.s.emitir_senha(codigo, "P", (i % 6) + 1)
        filas = self.s.consultar_todas_filas()
        self.assertEqual(sum(f["quantidade_normais"] for f in filas), 5)
        self.assertEqual(sum(f["quantidade_prioritarias"] for f in filas), 4)

    def test_03_prioritaria_antes_da_normal_anterior(self):
        normal = self.s.emitir_senha("C1", "N")
        prioritario = self.s.emitir_senha("C1", "P", 6)
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], prioritario["senha"])
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], normal["senha"])

    def test_04_fifo_na_mesma_categoria_prioritaria(self):
        primeira = self.s.emitir_senha("C1", "P", 3)
        segunda = self.s.emitir_senha("C1", "P", 3)
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], primeira["senha"])
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], segunda["senha"])

    def test_05_tempo_de_espera_calculado_pela_ordem(self):
        alvo = self.s.emitir_senha("C1", "N")
        for prioridade in (6, 4, 2, 1):
            self.s.emitir_senha("C1", "P", prioridade)
        espera = self.s.consultar_tempo_espera("C1", alvo["senha"])
        self.assertEqual(espera["pacientes_a_frente"], 4)
        self.assertEqual(espera["tempo_estimado_minutos"], 120)
        self.s.chamar_proximo("C1")
        self.assertEqual(self.s.consultar_tempo_espera("C1", alvo["senha"])["tempo_estimado_minutos"], 90)

    def test_06_fila_vazia(self):
        self.assertIsNone(self.s.chamar_proximo("C2"))
        self.assertEqual(self.s.consultar_fila("C2")["quantidade_aguardando"], 0)
        self.assertIsNone(self.s.obter_painel()["ultima_senha_chamada"])

    def test_07_ordem_prioridade_completa(self):
        for nivel in (6, 2, 5, 1, 4, 3):
            self.s.emitir_senha("C1", "P", nivel)
        niveis = [s["nivel_prioridade"] for s in self.s.consultar_fila("C1")["ordem_atendimento"]]
        self.assertEqual(niveis, [1, 2, 3, 4, 5, 6])

    def test_08_fifo_normais_e_sequencia_por_especialidade(self):
        a = self.s.emitir_senha("C1", "N")
        b = self.s.emitir_senha("C1", "P", 1)
        c = self.s.emitir_senha("C1", "N")
        d = self.s.emitir_senha("C2", "N")
        self.assertEqual([a["senha"], b["senha"], c["senha"], d["senha"]],
                         ["C1-N001", "C1-P002", "C1-N003", "C2-N001"])
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], b["senha"])
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], a["senha"])
        self.assertEqual(self.s.chamar_proximo("C1")["senha"], c["senha"])

    def test_09_entradas_invalidas_nao_consumem_numeracao(self):
        with self.assertRaises(ValueError):
            self.s.emitir_senha("C1", "P")
        with self.assertRaises(ValueError):
            self.s.emitir_senha("C1", "N", 2)
        with self.assertRaises(ValueError):
            self.s.emitir_senha("C1", "P", 9)
        with self.assertRaises(ValueError):
            self.s.emitir_senha("C1", "X")
        self.assertEqual(self.s.emitir_senha("C1", "N")["senha"], "C1-N001")
        with self.assertRaises(KeyError):
            self.s.emitir_senha("C4", "N")

    def test_10_consulta_nao_remove_e_senha_chamada_sai_da_espera(self):
        codigo = self.s.emitir_senha("C1", "P", CATEGORIAS_PRIORIDADE[0])["senha"]
        self.s.consultar_fila("C1")
        self.s.consultar_fila("C1")
        self.assertEqual(self.s.consultar_fila("C1")["quantidade_aguardando"], 1)
        self.s.chamar_proximo("C1")
        with self.assertRaises(LookupError):
            self.s.consultar_tempo_espera("C1", codigo)
        self.assertEqual(self.s.obter_painel()["ultima_senha_chamada"]["senha"], codigo)

    def test_11_especialidades_independentes(self):
        self.s.emitir_senha("C1", "P", 1)
        self.s.emitir_senha("C2", "N")
        self.s.chamar_proximo("C1")
        self.assertEqual(self.s.consultar_fila("C1")["quantidade_aguardando"], 0)
        self.assertEqual(self.s.consultar_fila("C2")["quantidade_aguardando"], 1)


if __name__ == "__main__":
    unittest.main()
