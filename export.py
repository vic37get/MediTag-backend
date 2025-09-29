import requests
import pandas as pd
from PIL import Image
import io
import base64


def get_dataframe(estudo_id: int, base_url: str = "http://localhost:8000"):
    """
    Exemplo de como chamar a API de exportação de estudos.
    """
    url = f"{base_url}/estudos/{estudo_id}/export"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"Estudo ID: {data['estudo_id']}")
        print(f"Total de registros: {data['total_registros']}")
        print(f"Colunas disponíveis: {data['colunas']}")
        
        # Converter de volta para DataFrame
        df = pd.DataFrame(data['dados'])
        return df
        
    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None


def get_pil_images(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reconstrói as imagens PIL a partir dos dados base64 no DataFrame.
    """
    def base64_to_pil(base64_string):
        if pd.isna(base64_string) or base64_string == "":
            return None
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            print(f"Erro ao reconstruir imagem: {e}")
            return None
    
    df['imagem_pil_reconstruida'] = df['imagem_pil_b64'].apply(base64_to_pil)
    return df


def save_data(df: pd.DataFrame, nome_arquivo: str = "estudo_exportado"):
    """
    Exemplo de como salvar os dados em diferentes formatos.
    """
    df.to_csv(f"{nome_arquivo}.csv", index=False)
    print(f"Dados salvos em {nome_arquivo}.csv")
    
    # import os
    # os.makedirs(f"{nome_arquivo}_imagens", exist_ok=True)
    
    # for idx, row in df.iterrows():
    #     if 'imagem_pil_reconstruida' in row and row['imagem_pil_reconstruida'] is not None:
    #         img_filename = f"{nome_arquivo}_imagens/amostra_{row['amostra_id']}_{idx}.jpg"
    #         row['imagem_pil_reconstruida'].save(img_filename)
    
    # print(f"Imagens salvas em {nome_arquivo}_imagens/")


if __name__ == "__main__":    
    df = get_dataframe(1)
    if df is not None:
        df = get_pil_images(df)
        save_data(df, "estudo_1_exportado")