"""Analysis Service - Business Logic"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from .models import AnalysisCreate, AnalysisUpdate, AnalysisResponse
from ..supabase_client import supabase_client


class AnalysisService:
    """Service for managing analyses (dashboards and reports)"""

    def __init__(self):
        self.client = supabase_client

    async def get_user_permissions(self, user_id: UUID) -> Dict[str, Any]:
        """Get user permissions based on their role and division"""
        try:
            # Get user details with role and division
            user_response = self.client.table("usuarios").select("""
                id, nome, email, ativo,
                cargos!inner(nome, nivel_acesso),
                divisoes!inner(id, nome, codigo)
            """).eq("id", str(user_id)).single().execute()

            if not user_response.data:
                return {"can_access_all": False, "user_division_id": None, "user_role_level": 0}

            user_data = user_response.data
            cargo_data = user_data.get("cargos", {})
            divisao_data = user_data.get("divisoes", {})

            return {
                "can_access_all": cargo_data.get("nivel_acesso", 0) >= 4,  # Master/Diretor/Gerente
                "user_division_id": divisao_data.get("id"),
                "user_role_level": cargo_data.get("nivel_acesso", 0)
            }

        except Exception as e:
            print(f"Error getting user permissions: {e}")
            return {"can_access_all": False, "user_division_id": None, "user_role_level": 0}

    def user_can_access_analysis(self, user_permissions: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Check if user can access a specific analysis"""
        # Master/Diretor/Gerente can access everything
        if user_permissions["can_access_all"]:
            return True

        # Analysis is public
        if analysis.get("publico", False):
            return True

        # Analysis is restricted to user's division
        if analysis.get("divisao_restrita_id"):
            return str(analysis["divisao_restrita_id"]) == str(user_permissions["user_division_id"])

        # Default: no access
        return False

    async def get_analyses_for_user(self, user_id: UUID) -> List[AnalysisResponse]:
        """Get all analyses that a user can access"""
        try:
            user_permissions = await self.get_user_permissions(user_id)

            # Get all analyses
            response = self.client.table("analyses").select("*").execute()

            if not response.data:
                return []

            # Filter analyses based on user permissions
            accessible_analyses = []
            for analysis in response.data:
                if self.user_can_access_analysis(user_permissions, analysis):
                    accessible_analyses.append(AnalysisResponse(**analysis))

            return accessible_analyses

        except Exception as e:
            print(f"Error getting analyses for user: {e}")
            return []

    async def get_analysis_by_id(self, analysis_id: UUID, user_id: UUID) -> Optional[AnalysisResponse]:
        """Get a specific analysis if user has access"""
        try:
            # Get analysis
            response = self.client.table("analyses").select("*").eq("id", str(analysis_id)).single().execute()

            if not response.data:
                return None

            analysis = response.data

            # Check permissions
            user_permissions = await self.get_user_permissions(user_id)
            if not self.user_can_access_analysis(user_permissions, analysis):
                return None

            return AnalysisResponse(**analysis)

        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None

    async def create_analysis(self, analysis_data: AnalysisCreate, user_id: UUID) -> Optional[AnalysisResponse]:
        """Create a new analysis (admin only)"""
        try:
            # Check if user is admin
            user_permissions = await self.get_user_permissions(user_id)
            if not user_permissions["can_access_all"]:
                return None

            # Create analysis
            data = analysis_data.dict()
            data["created_at"] = "now()"
            data["updated_at"] = "now()"

            response = self.client.table("analyses").insert(data).execute()

            if response.data:
                return AnalysisResponse(**response.data[0])

        except Exception as e:
            print(f"Error creating analysis: {e}")

        return None

    async def update_analysis(self, analysis_id: UUID, update_data: AnalysisUpdate, user_id: UUID) -> Optional[AnalysisResponse]:
        """Update an analysis (admin only)"""
        try:
            # Check if user is admin
            user_permissions = await self.get_user_permissions(user_id)
            if not user_permissions["can_access_all"]:
                return None

            # Update analysis
            data = update_data.dict(exclude_unset=True)
            data["updated_at"] = "now()"

            response = self.client.table("analyses").update(data).eq("id", str(analysis_id)).execute()

            if response.data:
                return AnalysisResponse(**response.data[0])

        except Exception as e:
            print(f"Error updating analysis: {e}")

        return None

    async def delete_analysis(self, analysis_id: UUID, user_id: UUID) -> bool:
        """Delete an analysis (admin only)"""
        try:
            # Check if user is admin
            user_permissions = await self.get_user_permissions(user_id)
            if not user_permissions["can_access_all"]:
                return False

            # Delete analysis
            response = self.client.table("analyses").delete().eq("id", str(analysis_id)).execute()

            return len(response.data) > 0 if response.data else False

        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False


# Global service instance
analysis_service = AnalysisService()

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance"""
    return analysis_service