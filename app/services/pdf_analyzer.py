import openai
import json
from PyPDF2 import PdfReader
from fastapi import HTTPException
from app.config import settings


class PDFAnalyzer:
    """PDF分析服务，使用OpenAI GPT分析简历内容"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        从PDF文件中提取文本内容
        
        Args:
            pdf_file: 上传的PDF文件对象
            
        Returns:
            str: 提取的文本内容
        """
        try:
            # 创建PDF读取器
            reader = PdfReader(pdf_file)
            text = ""
            
            # 遍历所有页面，提取文本
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # 检查是否成功提取到文本
            if not text.strip():
                raise ValueError("PDF文件中没有找到可提取的文本")
            
            return text.strip()
            
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"PDF文件读取失败: {str(e)}"
            )
    
    def analyze_with_gpt(self, text: str) -> dict:
        """
        使用GPT分析文本并提取CandidateProfile需要的字段
        
        Args:
            text: 从PDF提取的文本内容
            
        Returns:
            dict: 提取的字段信息
        """
        try:
            # 构建提示词，告诉GPT需要提取什么信息
            prompt = f"""
            请分析以下简历文本，提取以下信息：
            
            重要：如果无法从文本中确定某个字段的信息，请明确返回"无法确定"或null，不要猜测或编造信息。
            
            必需字段：
            - full_name: 姓名（字符串，不超过80字符，如果无法确定则返回"无法确定"）
            - age: 年龄（整数，18-80之间，如果无法确定则返回null）
            - gender: 性别（必须是以下之一：male, female，如果无法确定则返回"无法确定"）
            
            可选字段：
            - phone: 电话号码（字符串，必须符合 xxx-xxx-xxxx 格式。如果简历中存在其他格式的电话，请尽量转换为 xxx-xxx-xxxx 格式，如果没有则设为null）
            - intro: 候选人的个人介绍（字符串，不超过1000个字符，如果不存在则返回null）
            
            个人介绍可以包含但不限于以下内容：
            - 学习或教育经历（如专业、学历）
            - 工作或实习经历
            - 技能与强项
            - 研究方向或兴趣领域
            
            intro字段应当是简洁的总结，而不是全文复制。
            
            简历文本：
            {text}
            
            请以JSON格式返回，只返回JSON数据，不要其他文字：
            {{
                "full_name": "姓名或无法确定",
                "age": 年龄数字或null,
                "gender": "性别值或无法确定",
                "phone": "电话号码或null",
                "intro": "第一人称视角、自我介绍形式的个人介绍或null"
            }}
            """
            
            # 调用OpenAI API（新版本格式）
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 低温度，确保输出一致性
                max_tokens=500
            )
            
            # 获取GPT的回复
            gpt_response = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                extracted_data = json.loads(gpt_response)
                return extracted_data
            except json.JSONDecodeError:
                raise ValueError("GPT返回的内容不是有效的JSON格式")
                
        except Exception as e:
            if "api_key" in str(e).lower():
                raise HTTPException(
                    status_code=500, 
                    detail="OpenAI API配置错误，请检查API密钥"
                )
            elif "quota" in str(e).lower() or "billing" in str(e).lower():
                raise HTTPException(
                    status_code=500, 
                    detail="OpenAI API配额不足或账单问题"
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"GPT分析失败: {str(e)}"
                )
    
    def validate_extracted_data(self, data: dict) -> tuple[bool, list]:
        """
        验证提取的数据是否符合CandidateProfile的要求
        
        Args:
            data: 从GPT提取的数据
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['full_name', 'age', 'gender']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"缺少必需字段: {field}")
            elif field == 'full_name' and data[field] == "无法确定":
                errors.append("无法从PDF中确定姓名信息")
            elif field == 'gender' and data[field] == "无法确定":
                errors.append("无法从PDF中确定性别信息")
        
        # 验证字段类型和值
        if 'full_name' in data and data['full_name'] and data['full_name'] != "无法确定":
            if not isinstance(data['full_name'], str):
                errors.append("full_name必须是字符串")
            elif len(data['full_name']) > 80:
                errors.append("full_name长度不能超过80字符")
        
        if 'age' in data and data['age'] is not None:
            if not isinstance(data['age'], int):
                errors.append("age必须是整数")
            elif data['age'] < 18 or data['age'] > 80:
                errors.append("age必须在18-80之间")
        
        if 'gender' in data and data['gender'] and data['gender'] != "无法确定":
            valid_genders = ['male', 'female']
            if data['gender'] not in valid_genders:
                errors.append(f"gender必须是以下值之一: {', '.join(valid_genders)}")
        
        if 'intro' in data and data['intro']:
            if not isinstance(data['intro'], str):
                errors.append("intro必须是字符串")
            elif len(data['intro']) > 1000:
                errors.append("intro长度不能超过1000字符")
        
        return len(errors) == 0, errors
    
    def analyze_pdf(self, pdf_file) -> dict:
        """
        完整的PDF分析流程
        
        Args:
            pdf_file: 上传的PDF文件对象
            
        Returns:
            dict: 分析结果
        """
        # 1. 提取PDF文本
        text = self.extract_text_from_pdf(pdf_file)
        
        # 2. 使用GPT分析文本
        extracted_data = self.analyze_with_gpt(text)
        
        # 3. 验证提取的数据
        is_valid, errors = self.validate_extracted_data(extracted_data)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"PDF分析不完整，请补全以下信息后重新上传: {'; '.join(errors)}"
            )
        
        return {
            "message": "PDF分析成功",
            "extracted_data": extracted_data,
            "suggestion": "请检查提取的信息是否正确，然后使用PUT /profile端点保存"
        }
