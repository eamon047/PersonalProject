# scripts/db_smoke.py
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager

# === 导入你的模型 ===
from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application
from app.models.candidate_profile import CandidateProfile

# 内存 SQLite，引擎带 foreign_keys 打开（SQLite 默认关着）
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

@contextmanager
def session_scope():
    with Session(engine) as s:
        yield s

def init_db():
    # 创建所有表
    SQLModel.metadata.create_all(engine)

def main():
    init_db()
    print("✅ Tables created")

    with session_scope() as s:
        # 1) 创建用户（唯一 email）
        u1 = User(email="a@example.com", password_hash="hash")
        s.add(u1); s.commit(); s.refresh(u1)
        print("✅ user1 id:", u1.id)

        # 1.1) 重复 email 触发唯一约束
        try:
            s.add(User(email="a@example.com", password_hash="hash2"))
            s.commit()
            raise RuntimeError("❌ duplicate email should fail but did not")
        except IntegrityError:
            s.rollback()
            print("✅ duplicate email blocked")

        # 2) 每个用户最多 1 家公司（owner_id 唯一）
        c1 = Company(owner_id=u1.id, name="Acme", website=None)
        s.add(c1); s.commit(); s.refresh(c1)
        print("✅ company id:", c1.id)

        try:
            s.add(Company(owner_id=u1.id, name="DupCo"))
            s.commit()
            raise RuntimeError("❌ duplicate company per owner should fail but did not")
        except IntegrityError:
            s.rollback()
            print("✅ unique company per owner blocked")

        # 3) 创建职位（与当前模型字段一致）
        j1 = Job(
            company_id=c1.id,
            title="Backend Engineer",
            position="backend",       # 你的模型若用 Enum/str，保持一致
            based_in_code=0,           # 0=tokyo, 1=osaka
            description="Build APIs",
            salary=500,
        )
        s.add(j1); s.commit(); s.refresh(j1)
        print("✅ job id:", j1.id)

        # 4) 候选人资料（与当前模型字段一致）
        prof = CandidateProfile(user_id=u1.id, full_name="Alice", age=23, gender="female", phone=None, intro="Hi")
        s.add(prof); s.commit(); s.refresh(prof)
        print("✅ profile user_id:", prof.user_id)

        # 5) Application（与当前模型字段一致）
        app1 = Application(user_id=u1.id, job_id=j1.id, status="applied", application_note=None)
        s.add(app1); s.commit(); s.refresh(app1)
        print("✅ application id:", app1.id)

        try:
            s.add(Application(user_id=u1.id, job_id=j1.id, status="applied", application_note=None))
            s.commit()
            raise RuntimeError("❌ duplicate application should fail but did not")
        except IntegrityError:
            s.rollback()
            print("✅ duplicate application blocked")

        # 6) 外键有效性：删除公司/用户/职位时是否可删？（视你是否设置了级联）
        # 这里不做强删测试，避免和你当前的约束设计冲突。你后续可按需加。

        # 7) 简单查询验证
        jobs_in_tokyo = s.exec(select(Job).where(Job.based_in_code == 0)).all()
        print("✅ jobs in tokyo:", len(jobs_in_tokyo))

    print("🎉 DB smoke test finished without fatal errors")

if __name__ == "__main__":
    main()
