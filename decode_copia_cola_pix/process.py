from typing import Dict, Union

TLV = Dict[str, Union[str, "TLV"]]


def parse_tlv(data: str) -> TLV:
    index = 0
    parsed = {}

    while index < len(data):
        tag = data[index:index + 2]
        length = int(data[index + 2:index + 4])
        value = data[index + 4:index + 4 + length]

        if is_nested_template(tag):
            parsed[tag] = parse_tlv(value)
        else:
            parsed[tag] = value

        index += 4 + length

    return parsed


def is_nested_template(tag: str) -> bool:
    tag_int = int(tag)
    return (26 <= tag_int <= 51) or (80 <= tag_int <= 99)


def url_indicates_recurrence(url: str) -> bool:
    keywords = ["/rec/", "recurring", "assinatura", "automatico"]
    return any(keyword in url.lower() for keyword in keywords)


def classify_journey(tlv: TLV) -> str:
    id_01 = tlv.get("01")
    id_26 = tlv.get("26", {})
    id_54 = tlv.get("54")
    id_80 = tlv.get("80", {})

    gui_26 = id_26.get("00")
    chave_pix = id_26.get("01")
    url_dinamica = id_26.get("25")

    url_80 = id_80.get("25")
    has_recurrence_url = isinstance(url_80, str) and url_indicates_recurrence(url_80)

    if has_recurrence_url and gui_26 and not chave_pix and not url_dinamica and not id_54 and not id_01:
        return "journey_2"

    if has_recurrence_url and url_dinamica and id_01 and not id_54:
        return "journey_3"

    if has_recurrence_url and chave_pix and id_54 and not id_01:
        return "journey_4"

    if not has_recurrence_url and url_dinamica and id_01:
        return "journey_1"

    return "only_pix"


def process_pix(pix_string: str) -> str:
    try:
        tlv = parse_tlv(pix_string)
        return classify_journey(tlv)
    except Exception as e:
        return f"Erro no processamento: {e}"


# Strings Pix de exemplo
pix_strings = {
    "jornada_2": (
        "00020126180014br.gov.bcb.pix5204000053039865802BR5913Fulano de Tal6008BRASILIA"
        "62070503***80950014br.gov.bcb.pix2573qr-h.sandbox.pix.bcb.gov.br/rest/api/rec/c7dc3d94706d4901a72480e98fcd52e1"
        "6304BAEE"
    ),
    "jornada_3": (
        "00020101021226940014br.gov.bcb.pix2572qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/b1480b32f97f488997e523a6be0a07b8"
        "5204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***80950014br.gov.bcb.pix2573qr-h.sandbox.pix.bcb."
        "gov.br/rest/api/rec/375a594f208645db99dec722f7a1682863042AC3"
    ),
    "jornada_4": (
        "00020101021226990014br.gov.bcb.pix2577qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/cobv/21a7e8ad364d4f6185cdc46ac2dc0b97"
        "5204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***80950014br.gov.bcb.pix2573qr-h.sandbox.pix.bcb.gov.br"
        "/rest/api/rec/5df5719e11d842beb13cb12b0d45002f63049561"
    ),
    "jornada_4_com_rejeicao": (
        "00020126780014br.gov.bcb.pix0136f4c6089a-bfde-4c00-a2d9-9eaa584b02190216CobrancaEstatica5204000053039865406162.075802BR5903Pix6008BRASILIA62290525c6ef3f314123446a8e0cab39e80950014br.gov.bcb.pix2573qr-h.sandbox.pix.bcb.gov.br/rest/api/rec/1f7a74f715974d1982c70f0715fb851c63041837"
    ),
    "pix_normal": (
        "00020126360014BR.GOV.BCB.PIX0114+5534999916880520400005303986540550.005802BR5925Welligton Santos de Olive6009SAO PAULO62140510wScB5irIEG6304312F"
    ),
    "jornada_2_failed": (
        "00020101021226940014br.gov.bcb.pix2572qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/BcbBad7A21BD6EDADB6CCCE4128972A05204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***80980014br.gov.bcb.pix2576qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/rec/BcbBad7A21BD6EDADB6CCCE4128972A06304C16F"
    ),
    "jornada_3_failed": (
        "00020101021226940014br.gov.bcb.pix2572qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/BcbBad732CBF6BC695144965B1368EB45204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***80980014br.gov.bcb.pix2576qr-h.sandbox.pix.bcb.gov.br/rest/api/v2/rec/BcbBad732CBF6BC695144965B1368EB46304C040"
    ) 
}

# Execução
for nome, valor in pix_strings.items():
    resultado = process_pix(valor)
    print(f"{nome}: {resultado}")
    

"""
Evoluir serviço {{decode}} responsável pela validação copia_cola pix incluindo uma validação e condição no decode para identificar se o copia_cola pertence ao pix_automatico,
se pertence ao pix_automático precisa ser consumindo o serviço {{btg_parser_code}} para realizar o parser do copia_cola para identificar qual a jornada que pertence o copia_cola,
essa jornada deve ser retornada em uma alteração de contrato a ser combinado com o Vini para que nosso front entende tome uma decisão de jornada para o cliente.


vou incluir na thread um script python que fiz ontem com a I.A para auxiliar o Renato nessa validação e tomada de decisão consumir o serviço da Dock ou BTG, não ficou simples mas vai ajuda-lo ...
se o Renato precisar demais informações tem esse video https://www.youtube.com/watch?v=aG9eJ1wEZjo do minuto 3:07 até o minuto 8:40 fala sobre essa validação do EMV copia_cola.


decode: https://api.dotz.com.br/pix-code/api/default/v1/qrcode/decode
btg_parser_code: https://uat.developer.btgpactual.com/docpi#operation/pix-brcode-parse


Obs.: ainda preciso alinhar contigo porque podemos incluir essas integrações desses serviços da BTG nessa nova plataforma techfin-pix-automatic ...

https://api.dotz.com.br/pix-code/api/default/v1/qrcode/decode
regras:
    only_pix : consumir api dock
    if any(journey_2, journey_3, journey_4):
        consumir api https://uat.developer.btgpactual.com/docpi#operation/pix-brcode-parse
        devolver no contrato a combinar com o Vini a Jornada e as chaves {unreservedTemplates}(dados para recorrencia) e {merchantAccountInformation}(dados pix)
        
    
    API`s para buscar os dados do recebedor apos consumir o serviço /pix-brcode-parse da BTG passando o valor da chave {unreservedTemplates}
    journey_2: https://uat.developer.btgpactual.com/docpi#operation/pix-recurrnece-payload-validate
    journey_3: https://uat.developer.btgpactual.com/docpi#operation/pix-brcode-parse-json
    journey_4: https://uat.developer.btgpactual.com/docpi#operation/pix-brcode-parse-cobv-json
    
    

"""
