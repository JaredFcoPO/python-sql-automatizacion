import pandas as pd
import oracledb
import get_anexo as get_an
import recibe_etapa_presupuesto as recibe_etapa
import re
import math
import get_cvs as get_cvs
from config import *



def es_indice_valido(indice):
    # Cadenas que coinciden con: 1. 10. A. a. I. o III.
    patron = r"^(?:\d+|[IVXLCDM]+|[A-Za-z])\.?$"
    return bool(re.match(patron, indice.strip()))

def get_nivel(indice):
    nivel_1 = r"\d+"
    nivel_2 = r"[A-Za-z]"
    nivel_3 = r"[IVXLCDM]"
    if re.match(nivel_1, indice):
        return 1
    elif re.match(nivel_2, indice):
        if re.match(nivel_3, indice):
            return 3
        return 2


def es_numero(cadena):
    try:
        float(cadena)
        return True
    except ValueError:
        return False

# Se recibe la etapa del presupuesto
def obtener_etapa_archivo():
    etapa_presupuesto = recibe_etapa.recibe_etapa_presupuesto()
    archivo_pdf = f"{etapa_presupuesto}_Ley.pdf"
    return etapa_presupuesto, archivo_pdf

def normaliza_texto(col):
    return (
        col.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+',' ', regex=True)
    )

def limpiar_anexo(archivo_pdf, etapa_presupuesto):
    seccion = ['APARTADO','APÉNDICE']
    resultado = get_an.extraer_indices(archivo_pdf, etapa_presupuesto = etapa_presupuesto)

    tabla = []
    apartado_actual = ''

    for i in range(len(resultado)):
        fila = []
        r = resultado[i]
        if r[0][0:8] in seccion:
            if r[0][0:8] == "APÉNDICE":
                apartado_actual = "Apéndice"
            else:
                apartado_actual = r[0][10]
        else:
            indice = r[0].split(".",1)[0].replace(" ","")

            #Si el indice tiene más de un carácter, es un salto de línea

            if not es_indice_valido(indice) and len(tabla) > 0:
                tabla[-1][4] = r[2]
                tabla[-1][2] += " "+ r[0]
                continue
            fila.append(apartado_actual)
            fila.append(indice)
            fila.append(r[0])
            fila.append(r[1])
            fila.append(r[2])
            tabla.append(fila)

    df_anexo = pd.DataFrame(tabla, columns = ["Apartado","Seccion","Título","Página inicial", "Página final"])
    df_anexo['Título_limpio'] = df_anexo['Título'].str.replace(r'^(?:[IVXLCDM]+|[A-Za-z0-9]+)[\.\)]\s*', '',regex=True)
    df_anexo['Título_limpio'] = normaliza_texto(df_anexo['Título_limpio'])
    df_anexo['Llave'] = df_anexo['Apartado'] + df_anexo['Seccion'] + df_anexo['Título_limpio']
    return df_anexo


def obtener_anexo_bd(etapa_presupuesto, anio):
    if etapa_presupuesto == "Iniciativa":
        query = f"SELECT * FROM ANEXO WHERE ANIO ={anio}"
        update = f"UPDATE ANEXO"
        insert = f"INSERT INTO ANEXO"
    else:
        query = f"SELECT * FROM ANEXO_A  WHERE ANIO ={anio}"
        update = f"UPDATE ANEXO_A"
        insert = f"INSERT INTO ANEXO_A"

    conn = oracledb.connect(user=usuario, password=contrasena, dsn=dns)
    cur = conn.cursor()
    cur.execute(query)
    consulta = cur.fetchall()
    columnas = [desc[0] for desc in cur.description]
    conn.close()

    df_consulta_bd = pd.DataFrame(consulta, columns = columnas)
    df_consulta_bd["SECCION_DESCRIPTIVO_nt"] = normaliza_texto(df_consulta_bd["SECCION_DESCRIPTIVO"])
    df_consulta_bd["LLAVE"] = df_consulta_bd["APARTADO"] + df_consulta_bd["SECCION"] + df_consulta_bd["SECCION_DESCRIPTIVO_nt"]

    return df_consulta_bd, columnas, update, insert

def generar_updates(df_anexo, df_consulta_bd, update):
    union_df = pd.merge(df_consulta_bd, df_anexo, left_on="LLAVE", right_on="Llave", how="left")
    na_union_df = union_df[union_df['Título'].isnull()]
    union_df['Página inicial'] = union_df['Página inicial'].astype(str)
    union_df['Página final'] = union_df['Página final'].astype(str)
    union_df.loc[union_df['PAGINA_INICIO'] == 'na', ['Página inicial', 'Página final']] = ['na', 'na']
    updates = []
    for _, row in union_df.iterrows():
        inicio = int(float(row['Página inicial'])) if es_numero(row['Página inicial']) else row['Página inicial']
        final = int(float(row['Página final'])) if es_numero(row['Página final']) else row['Página final']
        seccion = row['SECCION']
        apartado = row['APARTADO']
        seccion_descriptivo = row['SECCION_DESCRIPTIVO']
        anio = row['ANIO']

        sentencia = f"""{update}
        SET PAGINA_INICIO = '{inicio}', PAGINA_FINAL = '{final}'
        WHERE SECCION = '{seccion}' AND APARTADO = '{apartado}' AND SECCION_DESCRIPTIVO = '{seccion_descriptivo}' AND ANIO = {anio};
        """
        updates.append(sentencia.strip())
    return updates

def generar_inserts(df_anexo, df_consulta_bd, insert, columnas):
    df_nuevo = pd.merge(df_anexo, df_consulta_bd, left_on = "Llave", right_on = "LLAVE", how = "left")
    df_na_nuevos = df_nuevo[df_nuevo['APARTADO'].isnull()]
    df_na_nuevos = df_na_nuevos[["Apartado", "Seccion", "Título", "Página inicial", "Página final"]]

    if df_nuevo.empty:
        return []
    df_apartado = df_consulta_bd[["ANIO", "APARTADO", "APARTADO_DESCRIPTIVO"]]
    df_apartado = df_apartado.drop_duplicates()
    df_nuevos_union = pd.merge(df_na_nuevos, df_apartado, left_on = "Apartado", right_on = "APARTADO", how = "inner")
    df_nuevos_union['Título_limpio'] = df_nuevos_union['Título'].str.replace(r'^(?:[IVXLCDM]+|[A-Za-z0-9]+)[\.\)]\s*','',regex=True)

    inserts = []
    for _, row in df_nuevos_union.iterrows():
        anio = row['ANIO']
        apartado = row['APARTADO']
        apartado_descriptivo = row['APARTADO_DESCRIPTIVO']
        seccion = row['Seccion']
        seccion_descriptivo = row['Título_limpio']
        inicio = int(float(row['Página inicial'])) if es_numero(row['Página inicial']) and not math.isnan(float(row['Página inicial'])) else row['Página inicial']
        final = int(float(row['Página final'])) if es_numero(row['Página final']) and not math.isnan(float(row['Página final'])) else row['Página final']
        nivel = get_nivel(row['Seccion'])

        sentencia = f"""
        {insert} ({",".join(columnas)}) VALUES ( 
        {anio}, '{apartado}', '{apartado_descriptivo}', '{seccion}', '{seccion_descriptivo}', {inicio}, {final}, {nivel});
        """
        inserts.append(sentencia.strip())
    return inserts

def guardar_sql(nombre_archivo, lista_sentencias):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(lista_sentencias))


# ================= MAIN ==========================
def main():
    etapa_presupuesto, archivo = obtener_etapa_archivo()
    df_anexo = limpiar_anexo(archivo, etapa_presupuesto)
    df_consulta_bd, columnas, update, insert = obtener_anexo_bd(etapa_presupuesto, 2026)
    updates = generar_updates(df_anexo, df_consulta_bd, update)
    guardar_sql("updates.sql", updates)
    inserts = generar_inserts(df_anexo, df_consulta_bd, insert, columnas)
    guardar_sql("inserts.sql", inserts)
    archivo_csv = get_cvs.exporta_csv(archivo, etapa_presupuesto)

    print(f"Archivos generados para la etapa {etapa_presupuesto}")

if __name__ == "__main__":
    main()