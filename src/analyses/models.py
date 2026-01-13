"""
Pydantic models for analyses (dashboards/reports).
"""
from typing import Optional
from pydantic import BaseModel


class AnalysisBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str
    embed_url: Optional[str] = None
    divisao_restrita_id: Optional[str] = None
    publico: bool = True
    ativo: bool = True


class AnalysisCreate(AnalysisBase):
    pass


class AnalysisUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    embed_url: Optional[str] = None
    divisao_restrita_id: Optional[str] = None
    publico: Optional[bool] = None
    ativo: Optional[bool] = None


class AnalysisResponse(AnalysisBase):
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
