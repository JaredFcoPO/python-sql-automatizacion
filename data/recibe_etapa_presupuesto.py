def recibe_etapa_presupuesto():
    etapas_validas = ["Iniciativa","Aprobado"]
    while True:
        etapa = input("Ingresa la etapa del archivo PDF (Iniciativa o Aprobado): ").strip()
        if etapa in etapas_validas:
            print(f"Elegiste la etapa {etapa} de Ley")
            return etapa
        else:
            print(f"No coincide con los valores esperados: {etapas_validas}, favor de verificar.")

