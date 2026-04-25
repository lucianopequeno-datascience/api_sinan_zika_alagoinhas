import os
from pysus.online_data import SINAN
import pandas as pd
from google.cloud import storage
from datetime import datetime

def run_oda_zika_pipeline():
    # 1. Configurações - Alterado para a pasta e identificação da Zika
    BUCKET_NAME = "dados_alagoinhas_bronze"
    DESTINATION_FOLDER = "saude/zika"  
    COD_ALAGOINHAS = "290070"
    
    print("Conectando ao SINAN para Zika Vírus...")
    sinan = SINAN.SINAN().load()
    
    # 2. Busca apenas 2026 - dis_code alterado para ZIKA
    print("Buscando dados de Zika 2026...")
    arquivos = sinan.get_files(dis_code="ZIKA", year=2026) 
    
    if not arquivos:
        print("Nenhum arquivo de Zika encontrado no servidor.")
        return

    # 3. Download e Filtro
    print(f"Baixando {arquivos[0].name}...")
    arquivo_baixado = arquivos[0].download()
    df = arquivo_baixado.to_dataframe()
    
    # Filtro Alagoinhas
    df_alagoinhas = df[df['ID_MN_RESI'] == COD_ALAGOINHAS]
    
    if df_alagoinhas.empty:
        print("Nenhum dado novo de Zika para Alagoinhas nesta carga.")
        return

    # 4. Preparação do arquivo local
    local_filename = "zika_alagoinhas_2026.csv"
    df_alagoinhas.to_csv(local_filename, index=False, sep=';', encoding='utf-8')
    
    # 5. Upload para o Cloud Storage
    print(f"Subindo para {BUCKET_NAME}/{DESTINATION_FOLDER}...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{DESTINATION_FOLDER}/{local_filename}")
    
    blob.upload_from_filename(local_filename)
    print(f"Sucesso! Zika disponível em {DESTINATION_FOLDER}/{local_filename}")

if __name__ == "__main__":
    run_oda_zika_pipeline()