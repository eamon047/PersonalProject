import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models.user import User
from app.security import get_password_hash


# 创建测试数据库
@pytest.fixture
def test_db():
    """创建测试数据库"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # 创建测试表
    from app.models import user, company, job, application, candidate_profile
    user.SQLModel.metadata.create_all(engine)
    company.SQLModel.metadata.create_all(engine)
    job.SQLModel.metadata.create_all(engine)
    application.SQLModel.metadata.create_all(engine)
    candidate_profile.SQLModel.metadata.create_all(engine)
    
    return engine


@pytest.fixture
def test_session(test_db):
    """创建测试会话"""
    def override_get_session():
        with Session(test_db) as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    return test_db


@pytest.fixture
def client(test_session):
    """创建测试客户端"""
    return TestClient(app)


class TestUserRegistration:
    """测试用户注册功能"""
    
    def test_register_user_success(self, client):
        """测试用户注册成功"""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
    
    def test_register_user_duplicate_email(self, client):
        """测试重复邮箱注册"""
        # 第一次注册
        client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        # 第二次注册相同邮箱
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password456"}
        )
        
        assert response.status_code == 409
        assert "邮箱已被注册" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client):
        """测试无效邮箱格式"""
        response = client.post(
            "/auth/register",
            json={"email": "invalid-email", "password": "password123"}
        )
        
        assert response.status_code == 422  # 验证错误
    
    def test_register_user_short_password(self, client):
        """测试密码太短"""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "123"}
        )
        
        assert response.status_code == 422  # 验证错误


class TestUserLogin:
    """测试用户登录功能"""
    
    def test_login_user_success(self, client):
        """测试用户登录成功"""
        # 先注册用户
        client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        # 然后登录
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_user_wrong_password(self, client):
        """测试密码错误"""
        # 先注册用户
        client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        # 用错误密码登录
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 400
        assert "邮箱或密码错误" in response.json()["detail"]
    
    def test_login_user_not_exists(self, client):
        """测试用户不存在"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"}
        )
        
        assert response.status_code == 400
        assert "邮箱或密码错误" in response.json()["detail"]


class TestAuthentication:
    """测试认证功能"""
    
    def test_protected_endpoint_without_token(self, client):
        """测试无token访问受保护端点"""
        response = client.get("/profile/me")
        assert response.status_code == 401  # 未授权
    
    def test_protected_endpoint_with_valid_token(self, client):
        """测试有效token访问受保护端点"""
        # 注册并登录用户
        client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        login_response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        token = login_response.json()["access_token"]
        
        # 使用token访问受保护端点
        response = client.get(
            "/profile/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404  # 没有个人资料，但认证成功
