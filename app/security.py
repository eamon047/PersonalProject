from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT相关函数
# data 是要放进 token 里的“声明/信息（claims）”，比如“这个 token 属于谁（sub）”角色是什么
# 例如：{"sub": str(user.id), "role": "candidate"}
# 令牌中包含的内容；Header（算法信息）,Payload（用户信息、过期时间等）, Signature（签名，防篡改）
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """验证JWT令牌，返回用户ID"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        # 过期时间不需要手动读取，decode会自动验证其是否有效，无效时直接抛出异常
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        # 使用try-except也是为了提前截获上面的异常
        return None

# 密码相关函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)
