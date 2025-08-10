from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用环境
    app_env: str = "dev"
    
    # 数据库配置
    database_url: str = "sqlite:///./app.db"
    
    # JWT配置
    jwt_secret: str = "your-super-secret-jwt-key-change-in-production"
    jwt_expire_minutes: int = 60
    
    # 管理员账号
    admin_email: str = "eamonzhaowork@gmail.com"
    admin_password: str = "zym1010."
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()
