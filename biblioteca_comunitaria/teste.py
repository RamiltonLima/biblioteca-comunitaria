
class MinhaString(str):
    def __init__(self, valor, atributo_adicional):
        super().__init__(valor)
        self.atributo_adicional = atributo_adicional

# Exemplo de uso
minha_str = MinhaString("Olá", "Atributo Extra")

# Agora você pode usar a string como se fosse uma string normal, e também acessar o atributo adicional
print(minha_str)  # Isso imprimirá "Olá"
print(minha_str.atributo_adicional)  # Isso imprimirá "Atributo Extra"