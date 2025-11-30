from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user
from ..models.candidate_profile import CandidateProfile
from ..models.user import User
from ..schemas.profile import ProfileResponse, ProfileUpdateRequest
from ..services.pdf_analyzer import PDFAnalyzer

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="personal profile not found")
    return ProfileResponse(
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        phone=profile.phone,
        intro=profile.intro,
    )


@router.put("/", response_model=ProfileResponse)
def upsert_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()

    if profile is None:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=payload.full_name,
            age=payload.age,
            gender=payload.gender,
            phone=payload.phone,
            intro=payload.intro,
        )
        session.add(profile)
    else:
        profile.full_name = payload.full_name
        profile.age = payload.age
        profile.gender = payload.gender
        profile.phone = payload.phone
        profile.intro = payload.intro

    session.commit()
    session.refresh(profile)

    return ProfileResponse(
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        phone=profile.phone,
        intro=profile.intro,
    )


@router.post("/upload-pdf")
async def upload_pdf_and_analyze(
    file: UploadFile = File(..., description="pdf file"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # """
    # 上传PDF简历并自动分析，提取CandidateProfile需要的字段
    
    # - 支持PDF格式文件
    # - 使用OpenAI GPT自动分析简历内容
    # - 提取姓名、年龄、性别、电话、个人介绍等信息
    # - 验证信息完整性，不完整时返回错误提示
    
    # 成功时直接返回提取的数据，可直接用于PUT /profile端点
    # """
    
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="only PDF files are supported"
        )
    
    # 验证文件大小（限制为10MB）
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="file size exceeds the 10MB limit"
        )
    
    try:
        # 创建PDF分析器实例
        analyzer = PDFAnalyzer()
        
        # 分析PDF文件
        result = analyzer.analyze_pdf(file.file)
        
        # 成功时直接返回提取的数据，符合PUT /profile的格式
        return result["extracted_data"]
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他未知错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error occurred during PDF processing: {str(e)}"
        )
