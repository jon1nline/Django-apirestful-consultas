from django.core.exceptions import ValidationError
import re

def validar_cpf(value):

    # Remove caracteres não numéricos
    cpf = ''.join(re.findall(r'\d', str(value)))

    if len(cpf) != 11:
        raise ValidationError('O CPF deve ter 11 dígitos.', code='invalid_length')

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.', code='all_digits_equal')

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        raise ValidationError('CPF inválido.', code='invalid_digit')

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        raise ValidationError('CPF inválido.', code='invalid_digit')

    return value