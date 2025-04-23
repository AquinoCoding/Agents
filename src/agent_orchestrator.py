"""
Orquestrador para executar os agentes de coleta de dados.
"""

import logging
import json
from typing import List, Dict, Any
import os
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.agents.g1_agent import G1Agent
from src.agents.twitter_agent import TwitterAgent
from src.agents.instagram_agent import InstagramAgent
from src.config.config import AGENT_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orquestrador para executar os agentes de coleta de dados."""
    
    def __init__(self):
        """Inicializa o orquestrador."""
        self.agents = {
            "g1": G1Agent(AGENT_CONFIG.get("g1", {})),
            "twitter": TwitterAgent(AGENT_CONFIG.get("twitter", {})),
            "instagram": InstagramAgent(AGENT_CONFIG.get("instagram", {}))
        }
        
        # Criar diretório para dados processados
        os.makedirs("data/processed", exist_ok=True)
        
        logger.info(f"Orquestrador inicializado com {len(self.agents)} agentes")
    
    def run_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Executa um agente específico.
        
        Args:
            agent_name: Nome do agente a ser executado
            
        Returns:
            Resultado da execução do agente
        """
        if agent_name not in self.agents:
            logger.error(f"Agente {agent_name} não encontrado")
            return {
                "source": agent_name,
                "success": False,
                "message": "Agente não encontrado",
                "data": [],
                "file_path": ""
            }
        
        logger.info(f"Executando agente: {agent_name}")
        return self.agents[agent_name].run()
    
    def run_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Executa todos os agentes.
        
        Returns:
            Resultados da execução de todos os agentes
        """
        results = {}
        
        for agent_name in self.agents:
            results[agent_name] = self.run_agent(agent_name)
        
        # Salvar resultados consolidados
        self._save_consolidated_results(results)
        
        return results
    
    def _save_consolidated_results(self, results: Dict[str, Dict[str, Any]]) -> str:
        """
        Salva os resultados consolidados de todos os agentes.
        
        Args:
            results: Resultados da execução de todos os agentes
            
        Returns:
            Caminho do arquivo salvo
        """
        consolidated_data = []
        
        for agent_name, result in results.items():
            if result.get("success", False):
                consolidated_data.extend(result.get("data", []))
        
        file_path = "data/processed/all_data.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados consolidados salvos em {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Erro ao salvar dados consolidados: {e}")
            return ""

if __name__ == "__main__":
    logger.info("Iniciando orquestrador de agentes...")
    orchestrator = AgentOrchestrator()
    results = orchestrator.run_all_agents()
    
    # Exibir resumo dos resultados
    for agent_name, result in results.items():
        status = "Sucesso" if result.get("success", False) else "Falha"
        message = result.get("message", "")
        logger.info(f"Agente {agent_name}: {status} - {message}")
