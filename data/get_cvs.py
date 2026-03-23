import get_anexo as get_an
import recibe_etapa_presupuesto as recibe_etapa
import csv
import os


def exporta_csv(archivo_pdf = None, etapa_presupuesto = None):
    if not etapa_presupuesto:
        etapa_presupuesto = recibe_etapa.recibe_etapa_presupuesto()
    if not archivo_pdf:
        archivo_pdf = f"{etapa_presupuesto}_Ley.pdf"

    if not os.path.exists(archivo_pdf):
        print(f"Error: No se encontró el archivo PDF {archivo_pdf}")
        return
    resultado = get_an.extraer_indices(archivo_pdf, etapa_presupuesto=etapa_presupuesto)

    if resultado:
        archivo_csv = f"Anexo_{etapa_presupuesto}_Ley.csv"
        with open(archivo_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Sección","Página inicial","Página final"])
            writer.writerows(resultado)
        print(f"Se ha generado {archivo_csv}")
        return archivo_csv
    else:
        print(f"No se generó el CSV")
        return None
