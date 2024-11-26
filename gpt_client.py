from openai import OpenAI
from config import OPENAI_TOKEN
import asyncio
import json

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_TOKEN)

# Predefined allowed values
ALLOWED_VALUES = {
    "cities": {
        "الرياض", "الدرعية", "الخرج", "الدلم", "المجمعة", "وادي الدواسر",
        "مكة المكرمة", "جدة", "الطائف", "المدينة المنورة", "ينبع", "الدمام",
        "الأحساء", "أبها", "خميس مشيط", "تبوك", "حائل", "جازان", "عرعر",
        "نجران", "الباحة", "سكاكا", "غير محدد"
    },
    "regions": {
        "منطقة الرياض", "منطقة مكة المكرمة", "منطقة المدينة المنورة",
        "المنطقة الشرقية", "منطقة القصيم", "منطقة عسير", "منطقة تبوك",
        "منطقة حائل", "منطقة جازان", "منطقة نجران", "منطقة الباحة",
        "منطقة الجوف", "منطقة الحدود الشمالية", "غير محدد"
    },
    "sectors": {
        "القطاع الصناعي والإنتاجي", "الصناعة الكيميائية والبتروكيماويات",
        "القطاع الهندسي والفني", "قطاع العقارات والمقاولات",
        "التجزئة والمبيعات المباشرة", "الاتصالات وتقنية المعلومات",
        "الأغذية والمشروبات", "التسويق والعلاقات العامة",
        "الخدمات اللوجستية والأمنية", "الخدمات القانونية والاستشارية",
        "القطاع المالي والمحاسبي", "الرعاية الصحية والخدمات الطبية",
        "الإدارة والدعم الإداري", "التعليم والتطوير المهني",
        "التصميم والفنون الإبداعية", "البيئة والاستدامة",
        "السياحة والضيافة", "البحث والتطوير", "قطاع الإعلام والنشر",
        "غير محدد"
    },
    "specializations": {
        "تصنيع المعادن", "تصنيع المواد البلاستيكية", "تصنيع المواد الغذائية",
        "تصنيع الأجهزة الكهربائية", "التصنيع الخفيف والثقيل", "الكيمياء العضوية",
        "الكيمياء غير العضوية", "هندسة البتروكيماويات",
        "إنتاج المواد الكيميائية المتخصصة", "معالجة المياه والنفايات",
        "الهندسة المدنية", "الهندسة الميكانيكية", "الهندسة الكهربائية",
        "الهندسة المعمارية", "التصميم الصناعي", "إدارة المشاريع",
        "تصميم الداخلي", "تسويق العقارات", "تطوير العقارات",
        "مقاولات البناء", "إدارة المبيعات", "خدمة العملاء", "التسويق الرقمي",
        "إدارة المخزون", "التحليل التجاري", "تطوير البرمجيات",
        "أمن المعلومات", "الشبكات والاتصالات", "إدارة البيانات",
        "الذكاء الاصطناعي", "إدارة الجودة", "غير محدد"
    }
}

async def get_response(prompt, client):
    instructions = """
                Extracts and validates structured job advertisement information.

                Instructions:
                The Jobs Data Extractor specializes in parsing job advertisements and extracting structured
                information based on a predefined schema. Fields are validated against predefined allowed values 
                (ALLOWED_VALUES). Missing or ambiguous data defaults to 'غير محدد'. The extractor outputs concise 
                JSON responses with validated job data.
                """
    json_results = []
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2048,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "ad_extractor_func",
                        "description": (
                                        f"{instructions}"
                        ),
                        "parameters": {
                            "type": "object",
                            "required": [
                                "company_name", "job_title", "city", "region", "sectors",
                                "specialization", "experience", "education", "email", "domain", "date"
                            ],
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "enum": list(ALLOWED_VALUES["cities"]),
                                    "description": "City or region of the job."
                                },
                                "region": {
                                    "type": "string",
                                    "enum": list(ALLOWED_VALUES["regions"]),
                                    "default": "غير محدد",
                                    "description": "Region corresponding to the city."
                                },
                                "sectors": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": list(ALLOWED_VALUES["sectors"])
                                    },
                                    "description": "Primary sectors of the job."
                                },
                                "specialization": {
                                    "type": "string",
                                    "enum": list(ALLOWED_VALUES["specializations"]),
                                    "description": "Specialization within the job sector."
                                },
                                "company_name": {"type": "string", "description": "Name of the company."},
                                "job_title": {"type": "string", "description": "Title of the job."},
                                "experience": {"type": "string", "description": "Required experience."},
                                "education": {"type": "string", "description": "Required education level."},
                                "email": {"type": "string", "description": "Email address for job contact."},
                                "domain": {"type": "string", "description": "Domain of the email address."},
                                "date": {"type": "string", "description": "Posting date in YYYY-MM-DD format."}
                            },
                            "additionalProperties": False
                        }
                    }
                }
            ],
            parallel_tool_calls=True,
        )
        # Process and collect tool call results
        if response.choices[0].message.tool_calls:
            for call in response.choices[0].message.tool_calls:
                json_results.append(eval(call.function.arguments))

    except Exception as e:
        print(f"Error: {e}")

    return json_results if json_results else "No valid data extracted"

# Example usage
async def main():
    ad = """إعلان وظيفة: مهندس كهرباء - شركة  فرع المقاولات

الموقع: [جدة]


نحن نبحث عن مهندس  كهرباء للانضمام إلى فريقها في مشاريع المقاولات!

المسؤوليات:

تصميم وتنفيذ الأنظمة الكهربائية لمشاريع المقاولات.
الإشراف على تركيب الأنظمة الكهربائية في المواقع.
إجراء الفحوصات والتقييمات الفنية لضمان مطابقة المواصفات.
التنسيق مع الفرق الفنية الأخرى لضمان سير العمل بكفاءة.
إعداد التقارير الفنية والمشاركة في الاجتماعات الدورية.
المتطلبات:

درجة بكاليوس في الهندسة الكهربائية أو ما يعادلها.
خبرة لا تقل عن [5] سنوات في مجال المقاولات.
معرفة قوية بالبرامج الهندسية مثل AutoCAD وETAP.
مهارات تواصل ممتازة وقدرة على العمل تحت الضغط.
نحن نقدم:

راتب تنافسي.
بيئة عمل محفزة وداعمة.
فرص للتطوير المهني والنمو الوظيفي.
كيفية التقديم:
يرجى إرسال السيرة الذاتية إلى [hr@cellexarabia.com] 
مع ذكر "مهندس كهرباء - فرع المقاولات" في موضوع الرسالة.

الموعد النهائي للتقديم: [25/11/2024]

نحن نتطلع إلى استقبال طلباتكم!"""
    prompt = "Extract job advertisements data from this ad :" + ad
    
    results = await get_response(prompt)
    print(json.dumps(results, ensure_ascii=False, indent=2))

# if __name__ == "__main__":
#     # Run the function
#     asyncio.run(main())
