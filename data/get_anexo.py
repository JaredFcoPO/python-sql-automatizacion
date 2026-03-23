import fitz
import re


# Lista de elementos fijos
limpiar = ["Miércoles 18 de diciembre de 2024", "Periódico Oficial del Estado de Puebla", "(Vigésima Séptima Sección)"]
seccion = ["APARTADO", "APÉNDICE"]

# Archivos pdf
titulo_indice = "ÍNDICE DEL ANEXO DE TRANSPARENCIA"


def elimina_encabezado(encabezado: str):
    busca = limpiar
    for b in busca:
        encabezado = encabezado.replace(b, "")
    encabezado = re.sub(r"^\s*\d+\s*|\s*\d+\s*$","",encabezado)
    encabezado = re.sub(r"\s+","",encabezado).strip()
    return encabezado

def limpia_pagina (pagina: str, elimina_numeros: bool = True):
    pagina = pagina.strip()
    eliminar = ["\n"," "]
    for e in eliminar:
        pagina = pagina.replace(e, "")

    if elimina_numeros:
        pagina = re.sub(r"\[\d+\]", "", pagina)

    return pagina


def limpia_texto(texto: str):
    texto = texto.strip()
    texto = re.sub(r"[\s]+", " ", texto)
    texto = re.sub(r"\.{3,}", " ", texto)
    texto = re.sub(r"\s*\d+\s*$", " ", texto).strip()

    return texto

def extraer_indice_iniciativa(pdf: str):
    datos = []
    datos_rango = []
    for n in range(len(pdf)):
        pag = pdf[n]
        links = pag.get_links()
        if not links:
            continue
        palabras = pag.get_text("words")
        for link in links:
            if link["kind"] == 1:
                area = link.get("from")
                destino = link.get("page")
                if not area:
                    continue
                    # Palabras dentro del área del link
                palabras_dentro =[w[4]
                                  for w in palabras
                                  if (w[0] >= area.x0 - 1 and w[2] <= area.x1 + 1 and
                                      w[1] >= area.y0 - 1 and w[3] <= area.y1 + 1)
                                  ]
                texto_link = " ".join(palabras_dentro).strip()
                texto_link = limpia_texto(texto_link)
                datos.append([texto_link, destino - 1])
    for i in range(len(datos)):
            texto, inicio = datos[i]
            if i < len(datos) - 1:
                _, siguiente_inicio = datos[i + 1]
                contenido = pdf[siguiente_inicio + 1].get_text()
                contenido = limpia_pagina(contenido)
                contenido_vacio = pdf[siguiente_inicio - 1].get_text()
                contenido_vacio = limpia_pagina(contenido_vacio)
                apartado = pdf[siguiente_inicio+1].get_text()
                apartado = limpia_pagina(apartado)
                apartado = apartado[0:8]
                if contenido and inicio != siguiente_inicio:
                    pattern_inicio = r'^(?:[A-Za-z]\.|[IVXLCDM]+\.|\d+\.)\s?'
                    match_result = bool(re.match(pattern_inicio, contenido.strip(), flags=re.IGNORECASE))
                    if contenido[0].isdigit() or match_result:
                        siguiente_inicio -= 1
                if contenido_vacio == "" and apartado in seccion and inicio != siguiente_inicio:
                    bandera = False
                    indice_cierre = inicio
                    while not bandera:
                        indice_cierre += 1

                        paginaBlanco = pdf[indice_cierre].get_text()
                        paginaBlanco = limpia_pagina(paginaBlanco)

                        if paginaBlanco == "":
                            bandera = True
                            siguiente_inicio = indice_cierre - 2
                fin = siguiente_inicio
            else:
                fin = len(pdf) - 3
            datos_rango.append([texto, inicio, fin])

    return datos_rango


def extraer_indice_ley(pdf: str):
    datos = []
    for n in range(len(pdf)):
        pag = pdf[n]
        links = pag.get_links()
        if not links:
            continue
        palabras = pag.get_text("words")
        for link in links:
            if link["kind"] == 1:
                area = link.get("from", None)
                destino = link.get("page", None)
                if not area:
                    continue
                    # Palabras dentro del área del link
                palabras_dentro = [w[4]
                                   for w in palabras
                                   if (w[0] >= area.x0 - 1 and w[2] <= area.x1 + 1 and
                                       w[1] >= area.y0 - 1 and w[3] <= area.y1 + 1)
                                   ]
                texto_link = " ".join(palabras_dentro).strip()
                texto_link = limpia_texto(texto_link)
                #print(f"->{texto_link}| Página destino: {destino}")
                datos.append([texto_link, destino - 1])
    datos_rango = []
    for d in range(len(datos)):
        texto, inicio = datos[d]
        if d < len(datos) - 1:
            _, siguiente_inicio = datos[d + 1]
            contenido_pag = pdf[siguiente_inicio + 1].get_text()
            contenido_pag = elimina_encabezado(contenido_pag)
            contenido_pag = limpia_pagina(contenido_pag)
            apartado = pdf[siguiente_inicio + 1].get_text()
            apartado = elimina_encabezado(apartado)
            apartado = limpia_pagina(apartado)
            apartado = apartado[0:8]
            if contenido_pag and contenido_pag[0].isdigit() and inicio != siguiente_inicio:
                #print(f"ENTRO")
                siguiente_inicio -= 1
            if apartado in seccion:
                siguiente_inicio -= 1
            fin = siguiente_inicio
        else:
            fin = len(pdf) - 3
        datos_rango.append([texto, inicio, fin])
    return datos_rango

def extraer_indices(archivo_pdf: str, etapa_presupuesto: str = "Iniciativa"):
    pdf = fitz.open(archivo_pdf)
    if etapa_presupuesto == "Iniciativa":
        return extraer_indice_iniciativa(pdf)
    else:
        return extraer_indice_ley(pdf)


