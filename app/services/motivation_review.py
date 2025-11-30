import openai
from typing import Optional

from fastapi import HTTPException, status

from app.config import settings
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job, Position


class MotivationReviewService:
    """基于候选人Profile和Job信息，对志望動機草稿给出反馈的服务"""

    def __init__(self) -> None:
        # 复用与 PDFAnalyzer 相同的 OpenAI 初始化方式
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def _build_profile_context(self, profile: Optional[CandidateProfile]) -> str:
        if profile is None:
            return "候选人尚未填写完整的Profile，只能基于志望動機本身给出部分反馈。\n"

        lines = [
            "[Candidate Profile]",
            f"姓名: {profile.full_name}",
            f"年龄: {profile.age}",
            f"性别: {profile.gender}",
        ]
        if profile.phone:
            lines.append(f"电话: {profile.phone}")
        if profile.intro:
            lines.append("简介:")
            lines.append(profile.intro)
        return "\n".join(lines)

    def _build_job_context(self, job: Job) -> str:
        lines = [
            "[Job Information]",
            f"职位标题: {job.title}",
            f"职位类型: {job.position}",
            f"工作地点代码: {job.based_in_code}",
            "职位描述:",
            job.description,
        ]
        return "\n".join(lines)

    def _load_guideline_for_position(self, position: Position) -> str:
        """针对不同职位类型的写作指导提示，作为RAG中的领域知识片段"""
        common = (
            "请从企业视角来评价志望動機，尤其关注:\n"
            "- 是否体现出对该职位具体工作的理解（而不是笼统地说‘喜欢编程’）\n"
            "- 是否举了和职位相关的具体经历或项目\n"
            "- 是否说明了候选人能为团队带来什么价值\n"
        )
        if position == Position.backend:
            specific = (
                "针对后端职位，以下元素通常会被重视:\n"
                "- 对API设计、数据库、性能优化等的兴趣或经验\n"
                "- 处理数据、业务逻辑、可维护性等方面的意识\n"
            )
        elif position == Position.frontend:
            specific = (
                "针对前端职位，以下元素通常会被重视:\n"
                "- 对用户体验、界面交互的关注\n"
                "- 与设计协作、实现响应式页面等的经验或兴趣\n"
            )
        else:
            # fullstack 或其他
            specific = (
                "针对全栈职位，以下元素通常会被重视:\n"
                "- 同时理解前端体验和后端设计的平衡\n"
                "- 愿意根据团队需要在不同层之间切换的灵活性\n"
            )
        return "[Motivation Guideline]\n" + common + "\n" + specific

    def review_motivation(
        self,
        *,
        raw_motivation: str,
        job: Job,
        profile: Optional[CandidateProfile],
    ) -> dict:
        """调用 OpenAI，对志望動機草稿给出分析与建议，不代写。"""
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API密钥未配置，无法进行动机分析",
            )

        profile_ctx = self._build_profile_context(profile)
        job_ctx = self._build_job_context(job)
        guideline_ctx = self._load_guideline_for_position(job.position)

        prompt = f"""You are a career advisor who understands entry-level and junior hiring in the Japanese IT industry.
A candidate is considering applying for the following job. Please review their motivation statement.

Your MAIN priorities, in order, are:
1. How well the motivation matches the job description and the company (alignment and misalignment).
2. Whether the motivation shows an understanding of the actual work of this position.
3. Whether the motivation makes good use of the candidate’s own experiences and strengths.

You can refer to the guideline text below, but it is only a general reference, not a strict rulebook.
If the candidate’s writing style is different from the examples, it can still be good as long as it matches the job and the company.

Very important:
- Speak directly to the candidate in the second person ("you"), not in the third person ("the candidate", "he/she").
- Do NOT ghost-write a completely new motivation statement.
- Do NOT output a full sample that can be copy-pasted as-is into an application form.
- Your role is a coach and an editor, not a ghostwriter.

Please respond in English and follow this structure:

1. Overall impression:
   In 1–3 sentences, describe your overall impression of the motivation statement,
   including whether it feels aligned with the job and company.

2. Match analysis:
   In bullet points, describe:
   - Which parts of the motivation match the job description or company (try to refer to specific phrases the candidate used).
   - Which parts might be misaligned or could be misunderstood by the company.

3. Areas for improvement:
   In bullet points, list concrete improvement points.
   Try to base this on how the candidate is currently writing, rather than on an ideal textbook answer.

4. Suggestions for additional or deeper content:
   In bullet points, suggest what the candidate could add or elaborate on, for example:
   - Specific experiences, achievements, or project details.
   - Skills or perspectives that are relevant to this particular role.
   - Clearer explanations of the value they can bring to the team.

Here is the context you can refer to:

{profile_ctx}

{job_ctx}

{guideline_ctx}

[Candidate Motivation Draft]
{raw_motivation}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800,
            )
            feedback = response.choices[0].message.content.strip()
            return {"feedback": feedback}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"动机分析失败: {str(e)}",
            )
