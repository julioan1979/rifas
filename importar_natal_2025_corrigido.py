"""
Script para importar dados do Excel para a campanha Natal 2025
Com tratamento correto de escuteiros únicos e irmãos
"""

from utils.supabase_client import get_supabase_client
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    """Converte string de data DD/MM/YYYY para formato ISO"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        parts = date_str.strip().split('/')
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
        return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        return None

def importar_dados():
    """Importa dados do Excel para o Supabase"""
    
    supabase = get_supabase_client()
    
    print("=" * 70)
    print("📦 IMPORTAÇÃO DE DADOS - NATAL 2025")
    print("=" * 70)
    print()
    
    # Dados extraídos do Excel
    blocos_data = [
        {'inicio': 0, 'fim': 10, 'seccao': 'CPP', 'escuteiro': 'Ilda Melo', 'irmaos': '', 'data_entrega': '19/11/2025', 'data_pagamento': '21/11/2025', 'valor_pago': 11, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 11, 'fim': 20, 'seccao': 'Pioneiros', 'escuteiro': 'Vasco Marmelo', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 21, 'fim': 30, 'seccao': 'Pioneiros', 'escuteiro': 'Renata', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 31, 'fim': 40, 'seccao': 'Pioneiros', 'escuteiro': 'Gustavo', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 41, 'fim': 50, 'seccao': 'Pioneiros', 'escuteiro': 'Inês R.', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 51, 'fim': 60, 'seccao': 'Pioneiros', 'escuteiro': 'Matias', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 61, 'fim': 70, 'seccao': 'Pioneiros', 'escuteiro': 'Matilde', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 71, 'fim': 80, 'seccao': 'Pioneiros', 'escuteiro': 'Inês Domingues', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 81, 'fim': 90, 'seccao': 'Pioneiros', 'escuteiro': 'Francisca Costa', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 91, 'fim': 100, 'seccao': 'Pioneiros', 'escuteiro': 'Lucena', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 101, 'fim': 110, 'seccao': 'CPP', 'escuteiro': 'Filipe Pereira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 111, 'fim': 120, 'seccao': 'CPP', 'escuteiro': 'Constança Festas', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 121, 'fim': 130, 'seccao': 'Pioneiros', 'escuteiro': 'Constança', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 131, 'fim': 140, 'seccao': 'Pioneiros', 'escuteiro': 'Zé Maria', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 141, 'fim': 150, 'seccao': 'Pioneiros', 'escuteiro': 'Rafael', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 151, 'fim': 160, 'seccao': 'Pioneiros', 'escuteiro': 'Helena', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 161, 'fim': 170, 'seccao': 'Pioneiros', 'escuteiro': 'Bianca', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 171, 'fim': 180, 'seccao': 'Pioneiros', 'escuteiro': 'Diogo', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 181, 'fim': 190, 'seccao': 'Lobitos', 'escuteiro': 'Lara Granja', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 191, 'fim': 200, 'seccao': 'Exploradores', 'escuteiro': 'Beatriz', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 201, 'fim': 210, 'seccao': 'Exploradores', 'escuteiro': 'Emília', 'irmaos': 'Júlio (Pioneiro)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 211, 'fim': 220, 'seccao': 'Lobitos', 'escuteiro': 'Leonardo', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 221, 'fim': 230, 'seccao': 'Lobitos', 'escuteiro': 'Benedita Norte Cunha', 'irmaos': 'Tomás Cunha (pioneiro)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 231, 'fim': 240, 'seccao': 'Lobitos', 'escuteiro': 'Pedro Monteiro', 'irmaos': 'André Monteiro (pioneiro)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 241, 'fim': 250, 'seccao': 'Lobitos', 'escuteiro': 'Pedro Nova', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 251, 'fim': 260, 'seccao': 'Lobitos', 'escuteiro': 'Miguel Rocha', 'irmaos': 'Margarida (exploradora)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 261, 'fim': 270, 'seccao': 'Exploradores', 'escuteiro': 'Ariana Semedo', 'irmaos': 'Rodrigo Semedo (pioneiro)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 271, 'fim': 280, 'seccao': 'Lobitos', 'escuteiro': 'Maria Clara', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 281, 'fim': 290, 'seccao': 'Lobitos', 'escuteiro': 'Mariana Cunha', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 291, 'fim': 300, 'seccao': 'Exploradores', 'escuteiro': 'Eduardo Silva', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '22/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 301, 'fim': 310, 'seccao': 'Exploradores', 'escuteiro': 'Matias', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 311, 'fim': 320, 'seccao': 'Caminheiros', 'escuteiro': 'Pedro Vila Pouca', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 321, 'fim': 330, 'seccao': 'Caminheiros', 'escuteiro': 'Gustavo', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 331, 'fim': 340, 'seccao': 'Caminheiros', 'escuteiro': 'Leonor', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 341, 'fim': 350, 'seccao': 'Exploradores', 'escuteiro': 'Matilde Bernardes', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 351, 'fim': 360, 'seccao': 'Exploradores', 'escuteiro': 'Carolina Areias', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 361, 'fim': 370, 'seccao': 'Caminheiros', 'escuteiro': 'André Areias', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 371, 'fim': 380, 'seccao': 'Exploradores', 'escuteiro': 'Inês Silva', 'irmaos': 'Francisco Silva (caminheiro)', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 381, 'fim': 390, 'seccao': 'Exploradores', 'escuteiro': 'Sara Leite', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 391, 'fim': 400, 'seccao': 'Caminheiros', 'escuteiro': 'Inês Pereira', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 401, 'fim': 410, 'seccao': 'Exploradores', 'escuteiro': 'Rodrigo Ribeiro', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '18/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 411, 'fim': 420, 'seccao': 'Lobitos', 'escuteiro': 'Alice Silva', 'irmaos': 'Francisco Silva (pioneiro)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 421, 'fim': 430, 'seccao': 'Lobitos', 'escuteiro': 'Beatriz Mouteira', 'irmaos': 'Benedita Mouteira (lobita)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 431, 'fim': 440, 'seccao': 'Lobitos', 'escuteiro': 'Benedita Sousa', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 441, 'fim': 450, 'seccao': 'Lobitos', 'escuteiro': 'Bernardo Oliveira', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 451, 'fim': 460, 'seccao': 'Lobitos', 'escuteiro': 'Bianca Rocha', 'irmaos': 'Gabriel Rocha (Lobito)', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 461, 'fim': 470, 'seccao': 'Exploradores', 'escuteiro': 'Rodrigo Ribeiro', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '18/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 471, 'fim': 480, 'seccao': 'Lobitos', 'escuteiro': 'Dago Gerber', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 481, 'fim': 490, 'seccao': 'Lobitos', 'escuteiro': 'Gabriel Cunha', 'irmaos': 'Gustavo Cunha (Explorador)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 491, 'fim': 500, 'seccao': 'Lobitos', 'escuteiro': 'Inês Peixoto', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 501, 'fim': 510, 'seccao': 'Lobitos', 'escuteiro': 'Inês Dias', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 511, 'fim': 520, 'seccao': 'Lobitos', 'escuteiro': 'José lobo', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 521, 'fim': 530, 'seccao': 'Lobitos', 'escuteiro': 'Letícia Pereira', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 531, 'fim': 540, 'seccao': 'Lobitos', 'escuteiro': 'Lua Monteiro', 'irmaos': 'Maria Monteiro (exploradora)', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 541, 'fim': 550, 'seccao': 'Lobitos', 'escuteiro': 'Luísa Duarte', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 551, 'fim': 560, 'seccao': 'Lobitos', 'escuteiro': 'Luiza Santos', 'irmaos': 'Mariana Santos (exploradora)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 561, 'fim': 570, 'seccao': 'Exploradores', 'escuteiro': 'Noa Valente', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '16/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 571, 'fim': 580, 'seccao': 'Lobitos', 'escuteiro': 'Maria Francisca Barroso', 'irmaos': 'Rodrigo Barroso (explorador)', 'data_entrega': '20/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 581, 'fim': 590, 'seccao': 'Lobitos', 'escuteiro': 'Maria Luísa Silva', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 591, 'fim': 600, 'seccao': 'Lobitos', 'escuteiro': 'Maria Rita Manaia', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 601, 'fim': 610, 'seccao': 'Lobitos', 'escuteiro': 'Marta Teixeira', 'irmaos': 'Tiago Teixeira (explorador)', 'data_entrega': '22/11/2025', 'data_pagamento': '22/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Não'},
        {'inicio': 611, 'fim': 620, 'seccao': 'Lobitos', 'escuteiro': 'Sofia Mota', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 621, 'fim': 630, 'seccao': 'Lobitos', 'escuteiro': 'Sofia Pereira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 631, 'fim': 640, 'seccao': 'Lobitos', 'escuteiro': 'Sofia Reuss', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 641, 'fim': 650, 'seccao': 'Lobitos', 'escuteiro': 'Vitória Costa', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 651, 'fim': 660, 'seccao': 'Lobitos', 'escuteiro': 'Miguel Fernandes', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 661, 'fim': 670, 'seccao': 'Exploradores', 'escuteiro': 'Gabriel Kenji Yamashita Quinta', 'irmaos': '', 'data_entrega': '19/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 671, 'fim': 680, 'seccao': 'Exploradores', 'escuteiro': 'Vasco Natividade da Silva', 'irmaos': '', 'data_entrega': '18/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 681, 'fim': 690, 'seccao': 'Exploradores', 'escuteiro': 'Bruno Brandão Moreira', 'irmaos': 'Rúben Moreira (Pioneiro)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 691, 'fim': 700, 'seccao': 'Exploradores', 'escuteiro': 'Dinis Araújo Alentejano', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 701, 'fim': 710, 'seccao': 'Exploradores', 'escuteiro': 'Gabriel Macedo da Silva Pereira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 711, 'fim': 720, 'seccao': 'Exploradores', 'escuteiro': 'Pedro Almeida Oliveira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 721, 'fim': 730, 'seccao': 'Exploradores', 'escuteiro': 'Isabel Soares Magalhães', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 731, 'fim': 740, 'seccao': 'Exploradores', 'escuteiro': 'Manuel Ramalhão Amorim', 'irmaos': '', 'data_entrega': '19/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 741, 'fim': 750, 'seccao': 'Exploradores', 'escuteiro': 'Rodrigo Ribeiro', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '18/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 751, 'fim': 760, 'seccao': 'Exploradores', 'escuteiro': 'Mariana Almeida Quintino', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 761, 'fim': 770, 'seccao': 'Exploradores', 'escuteiro': 'Guilherme Miguel Santos de Oliveira', 'irmaos': 'Francisco Oliveira (Pioneiro)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 771, 'fim': 780, 'seccao': 'Exploradores', 'escuteiro': 'Sara Raquel Martins Machado', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 781, 'fim': 790, 'seccao': 'Exploradores', 'escuteiro': 'Patrick Sousa Simmler', 'irmaos': 'Mayza (Pioneira)', 'data_entrega': '19/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 791, 'fim': 800, 'seccao': 'Exploradores', 'escuteiro': 'Serena Valente', 'irmaos': '', 'data_entrega': '15/11/2025', 'data_pagamento': '17/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 801, 'fim': 810, 'seccao': 'Lobitos', 'escuteiro': 'Rita Tavares', 'irmaos': '', 'data_entrega': '17/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 811, 'fim': 820, 'seccao': 'Exploradores', 'escuteiro': 'Márcio Silva Sousa', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 821, 'fim': 830, 'seccao': 'Exploradores', 'escuteiro': 'Maria Malheiro Cadilhe', 'irmaos': 'Joana Cadilhe (Pioneira)', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 831, 'fim': 840, 'seccao': 'Exploradores', 'escuteiro': 'António Costa', 'irmaos': 'Beatriz Costa', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 841, 'fim': 850, 'seccao': 'Exploradores', 'escuteiro': 'Leonor Ramos dos Santos', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 851, 'fim': 860, 'seccao': 'Exploradores', 'escuteiro': 'Francisco Oliveira', 'irmaos': 'Filipe Oliveira', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 861, 'fim': 870, 'seccao': 'Exploradores', 'escuteiro': 'Mafalda Lage', 'irmaos': 'Maria Filipa Sousa Lage', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 871, 'fim': 880, 'seccao': 'Exploradores', 'escuteiro': 'Mafalda Guedes Rodrigues', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 881, 'fim': 890, 'seccao': 'Exploradores', 'escuteiro': 'M.Rita Moreira Barbosa', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 891, 'fim': 900, 'seccao': 'Caminheiros', 'escuteiro': 'Maria camelo', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 901, 'fim': 910, 'seccao': 'Caminheiros', 'escuteiro': 'Inês Soares', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 911, 'fim': 920, 'seccao': 'Caminheiros', 'escuteiro': 'Leonor Nogueira', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 921, 'fim': 930, 'seccao': 'Caminheiros', 'escuteiro': 'Pedro Marques', 'irmaos': '', 'data_entrega': '', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 931, 'fim': 940, 'seccao': 'Exploradores', 'escuteiro': 'Rodrigo Ribeiro', 'irmaos': '', 'data_entrega': '18/11/2025', 'data_pagamento': '18/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 941, 'fim': 950, 'seccao': 'Exploradores', 'escuteiro': 'Tiago Teixeira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '22/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Não'},
        {'inicio': 951, 'fim': 960, 'seccao': 'Exploradores', 'escuteiro': 'Márcio Silva Sousa', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 961, 'fim': 970, 'seccao': 'Lobitos', 'escuteiro': 'Benedita Mouteira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 971, 'fim': 980, 'seccao': 'Exploradores', 'escuteiro': 'Noa Valente', 'irmaos': '', 'data_entrega': '18/11/2025', 'data_pagamento': '19/11/2025', 'valor_pago': 10, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
        {'inicio': 981, 'fim': 990, 'seccao': 'CPP', 'escuteiro': 'Filipe Pereira', 'irmaos': '', 'data_entrega': '22/11/2025', 'data_pagamento': '', 'valor_pago': '', 'rifas_devolvidas': '', 'canhoto': ''},
        {'inicio': 991, 'fim': 999, 'seccao': 'Exploradores', 'escuteiro': 'Serena Valente', 'irmaos': '', 'data_entrega': '17/11/2025', 'data_pagamento': '18/11/2025', 'valor_pago': 9, 'rifas_devolvidas': 0, 'canhoto': 'Sim'},
    ]
    
    # 1. Criar campanha Natal 2025
    print("📅 Criando campanha Natal 2025...")
    try:
        campanha_response = supabase.table('campanhas').insert({
            'nome': 'Natal 2025',
            'descricao': 'Campanha de rifas de Natal 2025',
            'data_inicio': '2025-11-01',
            'data_fim': '2025-12-31',
            'ativa': True
        }).execute()
        
        campanha_id = campanha_response.data[0]['id']
        print(f"   ✅ Campanha criada (ID: {campanha_id})")
    except Exception as e:
        print(f"   ❌ Erro ao criar campanha: {e}")
        return
    
    # 2. Extrair lista ÚNICA de escuteiros
    print()
    print("👥 Identificando escuteiros únicos...")
    
    escuteiros_unicos = set()
    irmaos_info = {}  # Para registar relações de irmãos
    
    for bloco in blocos_data:
        if bloco['escuteiro']:
            escuteiros_unicos.add(bloco['escuteiro'].strip())
        
        # Extrair irmãos mencionados
        if bloco['irmaos']:
            # Parse irmãos (formato: "Nome (seccao)")
            irmao_text = bloco['irmaos'].strip()
            if '(' in irmao_text:
                irmao_nome = irmao_text.split('(')[0].strip()
                escuteiros_unicos.add(irmao_nome)
                
                # Registar relação
                if bloco['escuteiro'] not in irmaos_info:
                    irmaos_info[bloco['escuteiro']] = []
                irmaos_info[bloco['escuteiro']].append(irmao_nome)
    
    print(f"   🔍 Encontrados {len(escuteiros_unicos)} escuteiros únicos")
    
    # 3. Criar escuteiros
    print()
    print(f"👥 Criando {len(escuteiros_unicos)} escuteiros...")
    escuteiros_map = {}  # nome -> id
    escuteiros_criados = 0
    
    for nome in sorted(escuteiros_unicos):
        try:
            esc_response = supabase.table('escuteiros').insert({
                'nome': nome,
                'ativo': True
            }).execute()
            
            escuteiro_id = esc_response.data[0]['id']
            escuteiros_map[nome] = escuteiro_id
            escuteiros_criados += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao criar {nome}: {e}")
    
    print(f"   ✅ {escuteiros_criados} escuteiros criados")
    
    # 4. Criar blocos de rifas e atribuir
    print()
    print(f"🎟️  Criando {len(blocos_data)} blocos de rifas...")
    blocos_criados = 0
    blocos_atribuidos = 0
    pagamentos_criados = 0
    
    for bloco in blocos_data:
        try:
            # Dados do bloco
            numero_inicial = bloco['inicio']
            numero_final = bloco['fim']
            seccao = bloco['seccao']
            escuteiro_nome = bloco['escuteiro'].strip() if bloco['escuteiro'] else None
            data_entrega = parse_date(bloco['data_entrega'])
            
            # Criar bloco
            bloco_data = {
                'campanha_id': campanha_id,
                'nome': f'Rifas {numero_inicial}-{numero_final}',
                'numero_inicial': numero_inicial,
                'numero_final': numero_final,
                'preco_unitario': 1.0,
                'seccao': seccao,
                'estado': 'atribuido' if escuteiro_nome and data_entrega else 'disponivel'
            }
            
            # Atribuir escuteiro se houver
            if escuteiro_nome and escuteiro_nome in escuteiros_map:
                bloco_data['escuteiro_id'] = escuteiros_map[escuteiro_nome]
                bloco_data['data_atribuicao'] = data_entrega if data_entrega else datetime.now().isoformat()
                blocos_atribuidos += 1
            
            bloco_response = supabase.table('blocos_rifas').insert(bloco_data).execute()
            bloco_id = bloco_response.data[0]['id']
            blocos_criados += 1
            
            # Criar venda e pagamento se houver
            data_pagamento = parse_date(bloco['data_pagamento'])
            valor_pago = bloco['valor_pago']
            
            if escuteiro_nome and data_pagamento and valor_pago and str(valor_pago).strip():
                try:
                    valor = float(valor_pago)
                    
                    # Criar venda
                    venda_response = supabase.table('vendas').insert({
                        'escuteiro_id': escuteiros_map[escuteiro_nome],
                        'bloco_id': bloco_id,
                        'quantidade': int(valor),  # Assumindo 1€ por rifa
                        'valor_total': valor,
                        'data_venda': data_pagamento,
                        'observacoes': f"Canhotos: {bloco['canhoto']}" if bloco['canhoto'] else None
                    }).execute()
                    
                    venda_id = venda_response.data[0]['id']
                    
                    # Criar pagamento
                    supabase.table('pagamentos').insert({
                        'venda_id': venda_id,
                        'valor_pago': valor,
                        'data_pagamento': data_pagamento,
                        'metodo_pagamento': 'Dinheiro',
                        'observacoes': f"Canhotos entregues: {bloco['canhoto']}" if bloco['canhoto'] else None
                    }).execute()
                    
                    pagamentos_criados += 1
                    
                except Exception as e:
                    print(f"   ⚠️  Erro ao criar pagamento para {escuteiro_nome}: {e}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar bloco {numero_inicial}-{numero_final}: {e}")
    
    print(f"   ✅ {blocos_criados} blocos criados")
    print(f"   ✅ {blocos_atribuidos} blocos atribuídos")
    print(f"   ✅ {pagamentos_criados} pagamentos registados")
    
    # Resumo de irmãos
    if irmaos_info:
        print()
        print("👨‍👩‍👧‍👦 Relações de irmãos identificadas:")
        for escuteiro, irmaos in sorted(irmaos_info.items())[:10]:  # Mostrar apenas 10
            print(f"   - {escuteiro} ↔ {', '.join(irmaos)}")
        if len(irmaos_info) > 10:
            print(f"   ... e mais {len(irmaos_info) - 10} relações")
    
    # Resumo final
    print()
    print("=" * 70)
    print("✅ IMPORTAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"  📅 Campanha: Natal 2025")
    print(f"  👥 Escuteiros únicos: {escuteiros_criados}")
    print(f"  🎟️  Blocos criados: {blocos_criados}")
    print(f"  ✅ Blocos atribuídos: {blocos_atribuidos}")
    print(f"  💰 Pagamentos registados: {pagamentos_criados}")
    print(f"  👨‍👩‍👧‍👦 Relações de irmãos: {len(irmaos_info)}")
    print("=" * 70)

if __name__ == "__main__":
    importar_dados()
