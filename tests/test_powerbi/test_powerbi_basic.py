"""Basic tests for Power BI integration"""
import pytest
from src.powerbi.config import get_powerbi_settings, PowerBISettings
from src.powerbi.models import AccessLevel, DashboardCreate, EmbedTokenRequest


@pytest.mark.unit
class TestPowerBIConfig:
    """Test Power BI configuration"""

    def test_powerbi_settings_creation(self):
        """Test Power BI settings creation"""
        settings = PowerBISettings()
        assert settings.powerbi_api_url == "https://api.powerbi.com/v1.0/myorg"
        assert settings.enable_powerbi_features == False
        assert settings.mock_powerbi == True

    def test_get_powerbi_settings(self):
        """Test getting Power BI settings"""
        settings = get_powerbi_settings()
        assert isinstance(settings, PowerBISettings)


@pytest.mark.unit
class TestPowerBIModels:
    """Test Power BI data models"""

    def test_access_level_enum(self):
        """Test AccessLevel enum values"""
        assert AccessLevel.PUBLIC == "public"
        assert AccessLevel.ROLE_BASED == "role_based"
        assert AccessLevel.PRIVATE == "private"

    def test_dashboard_create_model(self):
        """Test DashboardCreate model"""
        data = {
            "name": "Test Dashboard",
            "description": "A test dashboard",
            "powerbi_report_id": "report-123",
            "powerbi_workspace_id": "workspace-456",
            "embed_url": "https://app.powerbi.com/embed/test",
            "access_level": AccessLevel.PRIVATE
        }

        dashboard = DashboardCreate(**data)
        assert dashboard.name == "Test Dashboard"
        assert dashboard.access_level == AccessLevel.PRIVATE

    def test_embed_token_request_model(self):
        """Test EmbedTokenRequest model"""
        from uuid import uuid4
        data = {
            "dashboard_id": uuid4(),
            "user_id": uuid4(),
            "filters": {"region": "North"}
        }

        request = EmbedTokenRequest(**data)
        assert "dashboard_id" in request.__dict__
        assert "user_id" in request.__dict__
        assert request.filters["region"] == "North"


# Integration tests (require Power BI service)
@pytest.mark.integration
class TestPowerBIService:
    """Integration tests for Power BI service"""

    @pytest.mark.asyncio
    async def test_generate_embed_token_mock(self):
        """Test embed token generation with mock data"""
        from src.powerbi.service import get_powerbi_service
        from uuid import uuid4

        service = get_powerbi_service()
        request = EmbedTokenRequest(
            dashboard_id=uuid4(),
            user_id=uuid4()
        )

        # This should work with mock data
        response = await service.generate_embed_token(request)
        assert "token" in response.__dict__
        assert "embed_url" in response.__dict__