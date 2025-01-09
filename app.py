import streamlit as st
from io import BytesIO
import pandas as pd
import PyPDF2

def index_tamaños(pdf_file):
    try:
        # Leer el PDF desde el archivo subido
        reader = PyPDF2.PdfReader(pdf_file)
        paginas_A3 = []
        paginas_A4 = []
        
        for i, pagina in enumerate(reader.pages):
            ancho = pagina.mediabox.width
            alto = pagina.mediabox.height
            
            # Identificar tamaños
            if ancho >= 595 and alto >= 842:  # A3 (más grande que A4)
                paginas_A3.append(i + 1)
            else:  # Asumimos que el resto son A4
                paginas_A4.append(i + 1)
        
        # Crear el DataFrame con los tamaños
        df = pd.DataFrame({
            'N° página': range(1, len(reader.pages) + 1),
            'Tamaño': ['A3' if i + 1 in paginas_A3 else 'A4' for i in range(len(reader.pages))]
        })

        return df, paginas_A3, paginas_A4, len(reader.pages)
    
    except Exception as e:
        st.error(f"Error procesando el archivo PDF: {e}")
        return None, None, None, None

    
def simplificar_rangos(lista):
    lista.sort()
    rangos = []
    inicio = lista[0]
    
    for i in range(1, len(lista)):
        if lista[i] != lista[i - 1] + 1:
            if inicio == lista[i - 1]:
                rangos.append(str(inicio))
            else:
                rangos.append(f"{inicio}-{lista[i - 1]}")
            inicio = lista[i]
    
    if inicio == lista[-1]:
        rangos.append(str(inicio))
    else:
        rangos.append(f"{inicio}-{lista[-1]}")
    
    return ", ".join(rangos)


# Streamlit App
st.title("Identificar tamaños de páginas en un PDF")

uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

if uploaded_file:
    nombre_archivo = uploaded_file.name.rsplit('.', 1)[0]
    df, paginas_A3, paginas_A4, n_paginas = index_tamaños(uploaded_file)
    resumen = {
        'N° páginas': [n_paginas],
        'N° A4': [len(paginas_A4)],
        'N° A3': [len(paginas_A3)]
    }
    resumen_df = pd.DataFrame(resumen)

    st.write("**Resumen del PDF**")
    st.dataframe(resumen_df)

    st.write("**Páginas A4**")
    st.write(simplificar_rangos(paginas_A4))

    st.write("**Páginas A3**")
    st.write(simplificar_rangos(paginas_A3))

    # Descargar el listado
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tamaños')
    output.seek(0)

    st.download_button(
        label="Descargar resumen en Excel",
        data=output,
        file_name=f"{nombre_archivo}_Resumen_tamaños.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )