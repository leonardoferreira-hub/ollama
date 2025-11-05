"""
Sistema de Auditoria e Rastreabilidade
Registra: hash do documento, versão do catálogo, modelos usados, prompts
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AuditTrail:
    """Trilha de auditoria para revisão de documentos"""

    def __init__(self, output_dir: Path):
        """
        Inicializa auditoria

        Args:
            output_dir: Diretório para salvar logs de auditoria
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.events = []
        self.metadata = {
            'session_id': self.session_id,
            'timestamp_inicio': datetime.now().isoformat(),
            'versao_sistema': '2.0.0'
        }

    def compute_file_hash(self, filepath: str) -> str:
        """
        Calcula hash SHA-256 do arquivo

        Args:
            filepath: Caminho do arquivo

        Returns:
            Hash hexadecimal
        """
        sha256 = hashlib.sha256()

        try:
            with open(filepath, 'rb') as f:
                # Lê em chunks para arquivos grandes
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)

            return sha256.hexdigest()

        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return "ERROR_HASH"

    def log_document_info(self, filepath: str, document_type: str = None):
        """
        Registra informações do documento de entrada

        Args:
            filepath: Caminho do documento
            document_type: Tipo do documento (CRI, CRA, Debênture)
        """
        file_path = Path(filepath)

        self.metadata['documento'] = {
            'nome': file_path.name,
            'hash_sha256': self.compute_file_hash(filepath),
            'tamanho_bytes': file_path.stat().st_size,
            'tipo': document_type,
            'data_modificacao': datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat()
        }

        self.log_event('DOCUMENT_LOADED', {
            'file': file_path.name,
            'hash': self.metadata['documento']['hash_sha256']
        })

    def log_catalog_info(self, catalog: Dict, catalog_path: str):
        """
        Registra informações do catálogo usado

        Args:
            catalog: Catálogo carregado
            catalog_path: Caminho do arquivo do catálogo
        """
        metadata_cat = catalog.get('metadata', {})

        self.metadata['catalogo'] = {
            'nome': metadata_cat.get('nome'),
            'versao': metadata_cat.get('versao'),
            'hash': metadata_cat.get('hash'),
            'arquivo': Path(catalog_path).name,
            'hash_arquivo': self.compute_file_hash(catalog_path),
            'total_clausulas': len(catalog.get('clausulas', []))
        }

        self.log_event('CATALOG_LOADED', {
            'catalog': metadata_cat.get('nome'),
            'version': metadata_cat.get('versao')
        })

    def log_parsing(self, num_clausulas: int, parsing_time: float):
        """Registra parsing do documento"""
        self.log_event('PARSING_COMPLETED', {
            'num_clausulas_encontradas': num_clausulas,
            'tempo_segundos': parsing_time
        })

    def log_ranking(self, num_clausulas: int, ranking_time: float):
        """Registra ranking"""
        self.log_event('RANKING_COMPLETED', {
            'num_clausulas_rankeadas': num_clausulas,
            'tempo_segundos': ranking_time
        })

    def log_tier1_classification(self,
                                  num_classificacoes: int,
                                  model: str,
                                  classification_time: float,
                                  summary: Dict):
        """
        Registra classificações Tier-1

        Args:
            num_classificacoes: Número de cláusulas classificadas
            model: Modelo usado
            classification_time: Tempo gasto
            summary: Resumo das classificações
        """
        self.metadata['tier1'] = {
            'model': model,
            'provider': 'ollama',
            'num_classificacoes': num_classificacoes,
            'tempo_segundos': classification_time,
            'summary': summary
        }

        self.log_event('TIER1_COMPLETED', {
            'model': model,
            'count': num_classificacoes,
            'presente': summary.get('presente', 0),
            'parcial': summary.get('parcial', 0),
            'ausente': summary.get('ausente', 0)
        })

    def log_routing(self, routing_events: List[Dict]):
        """
        Registra decisões de roteamento

        Args:
            routing_events: Eventos de roteamento
        """
        tier1_only = sum(1 for e in routing_events if e['decision'] == 'TIER1_ONLY')
        needs_tier2 = sum(1 for e in routing_events if e['decision'] == 'NEEDS_TIER2')

        self.metadata['roteamento'] = {
            'tier1_only': tier1_only,
            'needs_tier2': needs_tier2,
            'eventos': routing_events
        }

        self.log_event('ROUTING_COMPLETED', {
            'tier1_only': tier1_only,
            'needs_tier2': needs_tier2
        })

    def log_tier2_generation(self,
                            num_sugestoes: int,
                            provider: str,
                            model: str,
                            generation_time: float):
        """
        Registra gerações Tier-2

        Args:
            num_sugestoes: Número de sugestões geradas
            provider: Provider usado
            model: Modelo usado
            generation_time: Tempo gasto
        """
        self.metadata['tier2'] = {
            'provider': provider,
            'model': model,
            'num_sugestoes': num_sugestoes,
            'tempo_segundos': generation_time
        }

        self.log_event('TIER2_COMPLETED', {
            'provider': provider,
            'model': model,
            'count': num_sugestoes
        })

    def log_prompt(self,
                   stage: str,
                   prompt_type: str,
                   prompt: str,
                   max_length: int = 500):
        """
        Registra prompt usado (truncado)

        Args:
            stage: Estágio (tier1, tier2, etc)
            prompt_type: Tipo do prompt
            prompt: Prompt completo
            max_length: Tamanho máximo a salvar
        """
        self.log_event('PROMPT_USED', {
            'stage': stage,
            'type': prompt_type,
            'prompt_preview': prompt[:max_length] + '...' if len(prompt) > max_length else prompt,
            'prompt_length': len(prompt)
        })

    def log_event(self, event_type: str, data: Dict):
        """
        Registra evento genérico

        Args:
            event_type: Tipo do evento
            data: Dados do evento
        """
        self.events.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        })

    def finalize(self):
        """Finaliza auditoria e salva arquivo"""
        self.metadata['timestamp_fim'] = datetime.now().isoformat()

        # Calcula tempo total
        inicio = datetime.fromisoformat(self.metadata['timestamp_inicio'])
        fim = datetime.fromisoformat(self.metadata['timestamp_fim'])
        self.metadata['tempo_total_segundos'] = (fim - inicio).total_seconds()

        # Salva arquivo de auditoria
        audit_file = self.output_dir / f'audit_{self.session_id}.json'

        audit_data = {
            'metadata': self.metadata,
            'events': self.events
        }

        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Auditoria salva em: {audit_file}")

        return audit_file

    def get_summary(self) -> str:
        """
        Gera sumário da auditoria

        Returns:
            String com sumário
        """
        doc = self.metadata.get('documento', {})
        cat = self.metadata.get('catalogo', {})
        t1 = self.metadata.get('tier1', {})
        t2 = self.metadata.get('tier2', {})
        roteamento = self.metadata.get('roteamento', {})

        summary = f"""
SUMÁRIO DE AUDITORIA
{'=' * 60}
Sessão: {self.session_id}
Tempo total: {self.metadata.get('tempo_total_segundos', 0):.2f}s

DOCUMENTO ANALISADO:
- Nome: {doc.get('nome')}
- Hash SHA-256: {doc.get('hash_sha256', '')[:16]}...
- Tamanho: {doc.get('tamanho_bytes', 0):,} bytes

CATÁLOGO USADO:
- Nome: {cat.get('nome')}
- Versão: {cat.get('versao')}
- Hash: {cat.get('hash')}
- Total de cláusulas: {cat.get('total_clausulas')}

TIER-1 (Classificação Local):
- Modelo: {t1.get('model')}
- Classificações: {t1.get('num_classificacoes')}
- PRESENTE: {t1.get('summary', {}).get('presente', 0)}
- PARCIAL: {t1.get('summary', {}).get('parcial', 0)}
- AUSENTE: {t1.get('summary', {}).get('ausente', 0)}

ROTEAMENTO:
- Aprovadas no Tier-1: {roteamento.get('tier1_only', 0)}
- Encaminhadas para Tier-2: {roteamento.get('needs_tier2', 0)}

TIER-2 (Geração de Sugestões):
- Provider: {t2.get('provider', 'N/A')}
- Modelo: {t2.get('model', 'N/A')}
- Sugestões geradas: {t2.get('num_sugestoes', 0)}

Total de eventos registrados: {len(self.events)}
"""

        return summary


def create_audit_trail(output_dir: Path) -> AuditTrail:
    """
    Factory para criar AuditTrail

    Args:
        output_dir: Diretório de saída

    Returns:
        Instância de AuditTrail
    """
    return AuditTrail(output_dir)
