"""Listas de especialidades e categorias exigidas pelo trabalho acadêmico."""

ESPECIALIDADES_PERMITIDAS = (
    "Clínica Geral",
    "Pediatria",
    "Ginecologia",
    "Cardiologia",
    "Psiquiatria",
)

# A posição (de 1 a 6) indica a ordem de prioridade do enunciado.
CATEGORIAS_PRIORIDADE = (
    "Pacientes com 80 anos ou mais",
    "Pacientes idosos de 60 a 79 anos",
    "Pessoas com deficiência (PCD)",
    "Gestantes",
    "Pessoas com obesidade",
    "Pessoas acompanhadas de criança de colo",
)


def identificar_prioridade(categoria: str | int) -> tuple[int, str]:
    """Retorna (nível, descrição) da prioridade. Nível 1 é o mais urgente.

    A interface pode enviar o texto da categoria ou seu número de 1 a 6.
    """
    if isinstance(categoria, int) and not isinstance(categoria, bool):
        if 1 <= categoria <= len(CATEGORIAS_PRIORIDADE):
            return categoria, CATEGORIAS_PRIORIDADE[categoria - 1]
    elif isinstance(categoria, str):
        for indice, descricao in enumerate(CATEGORIAS_PRIORIDADE, start=1):
            if categoria.strip().casefold() == descricao.casefold():
                return indice, descricao
    raise ValueError("Categoria de prioridade inválida. Use uma das seis categorias permitidas.")
