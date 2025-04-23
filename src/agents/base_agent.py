"""
Agente base que define a interface comum para todos os agentes de coleta.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
import json
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Classe base para todos os agentes de coleta de dados."""
    
    def __init__(self, config: Dict[str, Any], source_name: str):
        """
        Inicializa o agente base.
        
        Args:
            config: Configurações do agente
            source_name: Nome da fonte de dados
        """
        self.config = config
        self.source_name = source_name
        self.data_dir = Path("data/raw") / source_name
        
        # Criar diretório para armazenar os dados coletados
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"Agente {source_name} inicializado")
    
    @abstractmethod
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Coleta dados da fonte.
        
        Returns:
            Lista de itens coletados
        """
        pass
    
    @abstractmethod
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados coletados.
        
        Args:
            data: Dados coletados
            
        Returns:
            Dados processados
        """
        pass
    
    def save_data(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Salva os dados em um arquivo JSON.
        
        Args:
            data: Dados a serem salvos
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados salvos em {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            return ""
    
    def run(self) -> Dict[str, Any]:
        """
        Executa o fluxo completo do agente: coleta, processamento e salvamento.
        
        Returns:
            Resultado da execução
        """
        try:
            # Coletar dados
            logger.info(f"Coletando dados de {self.source_name}...")
            raw_data = self.collect_data()
            
            if not raw_data:
                logger.warning(f"Nenhum dado coletado de {self.source_name}")
                return {
                    "source": self.source_name,
                    "success": False,
                    "message": "Nenhum dado coletado",
                    "data": [],
                    "file_path": ""
                }
            
            # Salvar dados brutos
            raw_file = f"{self.source_name}_raw.json"
            self.save_data(raw_data, raw_file)
            
            # Processar dados
            logger.info(f"Processando dados de {self.source_name}...")
            processed_data = self.process_data(raw_data)
            
            # Salvar dados processados
            processed_file = f"{self.source_name}_processed.json"
            file_path = self.save_data(processed_data, processed_file)
            
            return {
                "source": self.source_name,
                "success": True,
                "message": f"Coletados {len(raw_data)} itens, processados {len(processed_data)} itens",
                "data": processed_data,
                "file_path": file_path
            }
        
        except Exception as e:
            logger.error(f"Erro na execução do agente {self.source_name}: {e}")
            return {
                "source": self.source_name,
                "success": False,
                "message": f"Erro: {str(e)}",
                "data": [],
                "file_path": ""
            }
