"""Exemplo de execução sem Tkinter (opcional para testar o back-end)."""

from sistema import SistemaSenhas


if __name__ == "__main__":
    sistema = SistemaSenhas()
    print("Cadastro:", sistema.cadastrar_especialidade("Clínica Geral"))
    print("Cadastro:", sistema.cadastrar_especialidade("Pediatria"))

    a = sistema.emitir_senha("C1", "N")
    b = sistema.emitir_senha("C1", "P", 2)
    c = sistema.emitir_senha("C1", "P", 1)
    sistema.emitir_senha("C2", "N")
    print("Senhas emitidas:", a["senha"], b["senha"], c["senha"])
    print("Ordem em Clínica Geral:",
          [s["senha"] for s in sistema.consultar_fila("C1")["ordem_atendimento"]])
    print("Espera da senha normal:", sistema.consultar_tempo_espera("C1", a["senha"]))
    print("Chamada:", sistema.chamar_proximo("C1"))
    print("Painel:", sistema.obter_painel())
