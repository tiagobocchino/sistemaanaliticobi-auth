"""
Authentication service using Supabase Auth
"""
from typing import Optional
from gotrue.errors import AuthApiError
from src.supabase_client import supabase_client, supabase_admin_client
from src.auth.models import (
    UserSignUp,
    UserSignIn,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordUpdateRequest,
    SignUpResponse
)


class AuthService:
    """Handle all authentication operations"""

    def __init__(self):
        self.client = supabase_client
        self.admin_client = supabase_admin_client

    async def sign_up(self, user_data: UserSignUp) -> SignUpResponse:
        """
        Register a new user

        Args:
            user_data: User registration data

        Returns:
            SignUpResponse: Authentication tokens/message depending on email confirmation requirement

        Raises:
            AuthApiError: If registration fails
        """
        try:
            response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "cargo_id": user_data.cargo_id,
                        "divisao_id": user_data.divisao_id
                    }
                }
            })

            if not response.user:
                raise AuthApiError("Failed to create user")

            # Verificar se email precisa confirmação
            if not response.session:
                # Email confirmation é necessária
                return SignUpResponse(
                    message="Cadastro realizado com sucesso! Por favor, verifique seu email para confirmar sua conta antes de fazer login.",
                    requires_email_confirmation=True,
                    user=UserResponse(
                        id=response.user.id,
                        email=response.user.email,
                        full_name=user_data.full_name,
                        cargo_id=user_data.cargo_id,
                        divisao_id=user_data.divisao_id,
                        created_at=response.user.created_at,
                        email_confirmed_at=response.user.email_confirmed_at
                    )
                )

            # Se chegou aqui, usuário foi criado e já está logado
            # Criar perfil na tabela usuarios se cargo_id e divisao_id foram fornecidos
            if user_data.cargo_id and user_data.divisao_id:
                await self._create_user_profile(
                    user_id=response.user.id,
                    email=response.user.email,
                    nome=user_data.full_name or response.user.email,
                    cargo_id=user_data.cargo_id,
                    divisao_id=user_data.divisao_id
                )

            return SignUpResponse(
                message="Cadastro realizado com sucesso!",
                requires_email_confirmation=False,
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                refresh_token=response.session.refresh_token,
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_data.full_name,
                    cargo_id=user_data.cargo_id,
                    divisao_id=user_data.divisao_id,
                    created_at=response.user.created_at,
                    email_confirmed_at=response.user.email_confirmed_at
                )
            )
        except AuthApiError as e:
            raise AuthApiError(f"Sign up failed: {str(e)}")

    async def _create_user_profile(self, user_id: str, email: str, nome: str, cargo_id: str, divisao_id: str):
        """
        Criar perfil do usuário na tabela usuarios

        Args:
            user_id: ID do usuário no auth.users
            email: Email do usuário
            nome: Nome completo
            cargo_id: UUID do cargo
            divisao_id: UUID da divisão
        """
        try:
            self.admin_client.table("usuarios").insert({
                "id": user_id,
                "email": email,
                "nome": nome,
                "cargo_id": cargo_id,
                "divisao_id": divisao_id,
                "ativo": True
            }).execute()
        except Exception as e:
            # Não falhar o signup se não conseguir criar o perfil
            print(f"Erro ao criar perfil do usuário: {str(e)}")

    async def sign_in(self, credentials: UserSignIn) -> TokenResponse:
        """
        Authenticate user with email and password

        Args:
            credentials: User login credentials

        Returns:
            TokenResponse: Authentication tokens and user data

        Raises:
            AuthApiError: If authentication fails
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })

            if not response.user:
                raise AuthApiError("Invalid credentials")

            user_metadata = response.user.user_metadata or {}

            return TokenResponse(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                refresh_token=response.session.refresh_token,
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_metadata.get("full_name"),
                    created_at=response.user.created_at,
                    email_confirmed_at=response.user.email_confirmed_at
                )
            )
        except AuthApiError as e:
            error_msg = str(e)
            print(f"AuthApiError during sign_in: {error_msg}")
            raise AuthApiError(f"Falha no login: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            print(f"Unexpected error during sign_in: {error_msg}")
            raise AuthApiError(f"Erro inesperado: {error_msg}")

    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out user and invalidate token

        Args:
            access_token: User's access token

        Returns:
            bool: True if successful
        """
        try:
            self.client.auth.sign_out()
            return True
        except AuthApiError:
            return False

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: User's refresh token

        Returns:
            TokenResponse: New authentication tokens

        Raises:
            AuthApiError: If refresh fails
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)

            if not response.user:
                raise AuthApiError("Failed to refresh token")

            user_metadata = response.user.user_metadata or {}

            return TokenResponse(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                refresh_token=response.session.refresh_token,
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_metadata.get("full_name"),
                    created_at=response.user.created_at,
                    email_confirmed_at=response.user.email_confirmed_at
                )
            )
        except AuthApiError as e:
            raise AuthApiError(f"Token refresh failed: {str(e)}")

    async def get_user(self, access_token: str) -> Optional[UserResponse]:
        """
        Get user data from access token

        Args:
            access_token: User's access token

        Returns:
            Optional[UserResponse]: User data if valid token
        """
        try:
            response = self.client.auth.get_user(access_token)

            if not response.user:
                return None

            user_metadata = response.user.user_metadata or {}

            return UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_metadata.get("full_name"),
                created_at=response.user.created_at,
                email_confirmed_at=response.user.email_confirmed_at
            )
        except AuthApiError:
            return None

    async def reset_password(self, request: PasswordResetRequest) -> bool:
        """
        Send password reset email

        Args:
            request: Password reset request with email

        Returns:
            bool: True if email sent
        """
        try:
            self.client.auth.reset_password_email(request.email)
            return True
        except AuthApiError:
            return False

    async def update_password(self, access_token: str, request: PasswordUpdateRequest) -> bool:
        """
        Update user password

        Args:
            access_token: User's access token
            request: New password

        Returns:
            bool: True if successful
        """
        try:
            self.client.auth.update_user({
                "password": request.new_password
            })
            return True
        except AuthApiError:
            return False


# Singleton instance
auth_service = AuthService()
