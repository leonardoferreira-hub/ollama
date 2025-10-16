"""
Sistema de Roteamento Inteligente
Decide quando usar Tier-1 (local) vs Tier-2 (frontier)
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ClauseRouter:
    """Roteador de cláusulas entre Tier-1 e Tier-2"""

    def __init__(self,
                 tier2_threshold: float = 0.7,
                 force_tier2_for_mandatory: bool = True):
        """
        Inicializa roteador

        Args:
            tier2_threshold: Threshold para acionar Tier-2
            force_tier2_for_mandatory: Se True, sempre usa Tier-2 para cláusulas obrigatórias
        """
        self.tier2_threshold = tier2_threshold
        self.force_tier2_for_mandatory = force_tier2_for_mandatory

    def should_use_tier2(self, classification: Dict) -> bool:
        """
        Decide se deve usar Tier-2 (frontier model)

        Critérios:
        - PRESENTE com alta confiança: NÃO (Tier-1 suficiente)
        - PARCIAL: SIM (precisa sugestão)
        - AUSENTE: SIM (precisa gerar cláusula)
        - Obrigatória + baixa confiança: SIM
        - Erro na classificação: SIM

        Args:
            classification: Resultado do Tier-1

        Returns:
            True se deve usar Tier-2
        """
        status = classification.get('classificacao')
        confianca = classification.get('confianca', 0.0)
        obrigatoria = classification.get('obrigatoria', False)
        error = classification.get('error', False)

        # Casos que sempre vão para Tier-2
        if error:
            logger.info("Roteando para Tier-2: erro na classificação")
            return True

        if status == 'AUSENTE':
            logger.info("Roteando para Tier-2: cláusula ausente")
            return True

        if status == 'PARCIAL':
            logger.info("Roteando para Tier-2: cláusula parcial")
            return True

        # PRESENTE mas obrigatória e baixa confiança
        if status == 'PRESENTE' and obrigatoria and confianca < self.tier2_threshold:
            logger.info(f"Roteando para Tier-2: obrigatória com confiança {confianca:.2f}")
            return True

        # PRESENTE com alta confiança: OK, não precisa Tier-2
        logger.info(f"Mantendo Tier-1: {status} com confiança {confianca:.2f}")
        return False

    def route_classifications(self, classifications: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Roteia múltiplas classificações

        Args:
            classifications: Lista de classificações do Tier-1

        Returns:
            Dict com 'tier1_only' e 'needs_tier2'
        """
        tier1_only = []
        needs_tier2 = []

        for item in classifications:
            classification = item.get('classification', {})

            if self.should_use_tier2(classification):
                needs_tier2.append(item)
            else:
                tier1_only.append(item)

        logger.info(f"Roteamento: {len(tier1_only)} OK no Tier-1, "
                   f"{len(needs_tier2)} precisam Tier-2")

        return {
            'tier1_only': tier1_only,
            'needs_tier2': needs_tier2
        }

    def get_routing_summary(self, routing_result: Dict) -> str:
        """
        Gera sumário do roteamento

        Args:
            routing_result: Resultado do route_classifications

        Returns:
            String com sumário
        """
        tier1 = routing_result['tier1_only']
        tier2 = routing_result['needs_tier2']

        total = len(tier1) + len(tier2)

        summary = f"""
SUMÁRIO DE ROTEAMENTO
{'=' * 50}
Total de cláusulas analisadas: {total}

✓ Aprovadas no Tier-1 (local): {len(tier1)}
  - Cláusulas PRESENTES com alta confiança
  - Não requerem intervenção

⚠ Encaminhadas para Tier-2 (frontier): {len(tier2)}
"""

        # Breakdown do Tier-2
        if tier2:
            ausentes = sum(1 for x in tier2 if x['classification'].get('classificacao') == 'AUSENTE')
            parciais = sum(1 for x in tier2 if x['classification'].get('classificacao') == 'PARCIAL')
            outros = len(tier2) - ausentes - parciais

            summary += f"  - AUSENTES: {ausentes}\n"
            summary += f"  - PARCIAIS: {parciais}\n"
            if outros > 0:
                summary += f"  - Outros (baixa confiança/obrigatórias): {outros}\n"

        return summary


def create_routing_report(routing_result: Dict) -> List[Dict]:
    """
    Cria relatório detalhado de roteamento para auditoria

    Args:
        routing_result: Resultado do roteamento

    Returns:
        Lista de eventos de roteamento
    """
    events = []

    for item in routing_result['tier1_only']:
        events.append({
            'clause_id': item['clause'].get('title'),
            'decision': 'TIER1_ONLY',
            'classification': item['classification'].get('classificacao'),
            'confidence': item['classification'].get('confianca'),
            'mandatory': item['classification'].get('obrigatoria'),
            'catalog_id': item['classification'].get('catalog_id')
        })

    for item in routing_result['needs_tier2']:
        events.append({
            'clause_id': item['clause'].get('title'),
            'decision': 'NEEDS_TIER2',
            'classification': item['classification'].get('classificacao'),
            'confidence': item['classification'].get('confianca'),
            'mandatory': item['classification'].get('obrigatoria'),
            'catalog_id': item['classification'].get('catalog_id')
        })

    return events
