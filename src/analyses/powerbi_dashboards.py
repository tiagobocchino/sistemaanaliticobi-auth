"""
Power BI Dashboards Configuration
Centralized configuration for all Power BI dashboards with access control rules
"""
from typing import Dict, List, Any


class PowerBIDashboards:
    """Configuration and access control for Power BI dashboards"""

    # Dashboard configurations with embed URLs and access rules
    DASHBOARDS = {
        "compras": {
            "nome": "Dashboard - Compras - DW",
            "descricao": "Dashboard de compras do Data Warehouse",
            "tipo": "powerbi",
            "embed_url": "https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea",
            "iframe_html": '<iframe title="Dashboard - Compras - DW (1)" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea" frameborder="0" allowFullScreen="true"></iframe>',
            "publico": False,  # Restrito por divisão/cargo
            "divisoes_permitidas": ["FIN"],  # Financeiro (compras e planejamento)
            "nivel_acesso_minimo": 4  # Master/Diretor/Gerente ou superior
        },
        "sdrs": {
            "nome": "Dashboard - SDRs (TV) v2.0",
            "descricao": "Dashboard de acompanhamento dos SDRs de TV",
            "tipo": "powerbi",
            "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9",
            "iframe_html": '<iframe title="Dashboard - SDRs (TV) v2.0" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9" frameborder="0" allowFullScreen="true"></iframe>',
            "publico": False,  # Restrito por divisão/cargo
            "divisoes_permitidas": ["COM"],  # Comercial (Marketing e comercial)
            "nivel_acesso_minimo": 4  # Master/Diretor/Gerente ou superior
        },
        "pastas": {
            "nome": "Dashboard - Pastas",
            "descricao": "Dashboard de contratos e pastas",
            "tipo": "powerbi",
            "embed_url": "https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea",
            "iframe_html": '<iframe title="Dashboard Contratos - 2.0v-19nov" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea" frameborder="0" allowFullScreen="true"></iframe>',
            "publico": False,  # Restrito por divisão/cargo
            "divisoes_permitidas": ["COM"],  # Comercial (Marketing e comercial)
            "nivel_acesso_minimo": 4  # Master/Diretor/Gerente ou superior
        }
    }

    # Mapeamento de códigos de divisão para nomes
    DIVISOES = {
        "TI": "Tecnologia da Informação",
        "RH": "Recursos Humanos",
        "FIN": "Financeiro",
        "COM": "Comercial",
        "OPS": "Operações"
    }

    @classmethod
    def get_dashboard(cls, dashboard_key: str) -> Dict[str, Any]:
        """Get dashboard configuration by key"""
        return cls.DASHBOARDS.get(dashboard_key)

    @classmethod
    def get_all_dashboards(cls) -> Dict[str, Dict[str, Any]]:
        """Get all dashboard configurations"""
        return cls.DASHBOARDS

    @classmethod
    def get_dashboard_keys(cls) -> List[str]:
        """Get list of all dashboard keys"""
        return list(cls.DASHBOARDS.keys())

    @classmethod
    def user_can_access_dashboard(cls, user_permissions: Dict[str, Any], dashboard_key: str) -> bool:
        """
        Check if user can access a specific dashboard based on their permissions

        Args:
            user_permissions: Dict with 'can_access_all', 'user_division_code', 'user_role_level'
            dashboard_key: Key of the dashboard to check

        Returns:
            bool: True if user has access
        """
        if dashboard_key not in cls.DASHBOARDS:
            return False

        dashboard = cls.DASHBOARDS[dashboard_key]

        # Admin/Master/Diretor can access everything
        if user_permissions.get("can_access_all", False):
            return True

        # Check minimum access level
        user_level = user_permissions.get("user_role_level", 0)
        min_level = dashboard.get("nivel_acesso_minimo", 5)
        if user_level < min_level:
            return False

        # Check if user's division is allowed
        user_division_code = user_permissions.get("user_division_code")
        allowed_divisions = dashboard.get("divisoes_permitidas", [])

        if user_division_code in allowed_divisions:
            return True

        return False

    @classmethod
    def get_accessible_dashboards_for_user(cls, user_permissions: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Get all dashboards that a user can access

        Args:
            user_permissions: User permissions dict

        Returns:
            Dict of accessible dashboards
        """
        accessible = {}
        for key, dashboard in cls.DASHBOARDS.items():
            if cls.user_can_access_dashboard(user_permissions, key):
                accessible[key] = dashboard
        return accessible


# Convenience functions
def get_dashboard_config(dashboard_key: str) -> Dict[str, Any]:
    """Get dashboard configuration by key"""
    return PowerBIDashboards.get_dashboard(dashboard_key)


def get_all_dashboard_configs() -> Dict[str, Dict[str, Any]]:
    """Get all dashboard configurations"""
    return PowerBIDashboards.get_all_dashboards()


def user_can_access_dashboard(user_permissions: Dict[str, Any], dashboard_key: str) -> bool:
    """Check if user can access a dashboard"""
    return PowerBIDashboards.user_can_access_dashboard(user_permissions, dashboard_key)
