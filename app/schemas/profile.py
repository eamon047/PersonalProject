from pydantic import BaseModel, Field
from typing import Optional

from ..models.candidate_profile import Gender

# 用在前端-后端的情况，表示请求体的结构
# 用户在提交数据时不应该有权限修改他们不该修改的字段(比如id)
class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=18, le=80)
    gender: Gender
    phone: Optional[str] = None
    intro: Optional[str] = Field(default=None, max_length=1000)

# 用在后端-前端的情况，表示响应体的结构
# 一般会比请求体多一些字段
# 保证了更强的灵活性，请求体可能做更严格的现实，而相应体可能做更宽松的展示
class ProfileResponse(BaseModel):
    user_id: int
    full_name: str
    age: int
    gender: Gender
    phone: Optional[str] = None
    intro: Optional[str] = None
