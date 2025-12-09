"""
Integrações com APIs Empresariais
Sienge ERP e CVDW CRM
"""

from .base_client import BaseAPIClient
from .sienge.client import SiengeClient
from .cvdw.client import CVDWClient

__all__ = [
    "BaseAPIClient",
    "SiengeClient",
    "CVDWClient"
]
