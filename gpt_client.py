from openai import OpenAI
from config import OPENAI_TOKEN
import time
import asyncio

client = OpenAI(api_key=OPENAI_TOKEN)

async def get_response(prompt, client=client):
    retry_delay = 15
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            },
            {
            "role": "assistant",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_calls": [
                {
                "id": "call_xAB64ZmpNNO1hhRQ5C9YzVjk",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"recruitment@two.sa\", \"domain\": \"two.sa\", \"region\": \"منطقة الرياض\", \"sectors\": [\"التجزئة والمبيعات المباشرة\"], \"education\": \"بكالوريوس\", \"job_title\": \"مدير عمليات\", \"experience\": \"خبرة لا تقل عن 7 سنوات\", \"company_name\": \"شركة متخصصة في مجال التجزئة\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_FC42L0D3w7gjDeczL8GaJy7T",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"المجمعة\", \"date\": \"2024-07-13\", \"email\": \"recruitment@two.sa\", \"domain\": \"two.sa\", \"region\": \"منطقة الرياض\", \"sectors\": [\"التجزئة والمبيعات المباشرة\"], \"education\": \"ثانوي\", \"job_title\": \"مديرة معرض\", \"experience\": \"سنة واكثر\", \"company_name\": \"شركة متخصصة في مجال التجزئة\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_2zSHWkEOehWbae5G7eaK4DzH",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"careers@glt.co\", \"domain\": \"glt.co\", \"region\": \"منطقة الرياض\", \"sectors\": [\"القطاع المالي والمحاسبي\"], \"education\": \"بكالوريوس\", \"job_title\": \"اخصائي مكافحة غسل اموال\", \"experience\": \"2-3 سنوات\", \"company_name\": \"شركة بمجال التقني المالي\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_u3E2UwwJCHzMuGJ2BTV3U9av",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"Jobc.2200@gmail.com\", \"domain\": \"gmail.com\", \"region\": \"منطقة الرياض\", \"sectors\": [\"القطاع المالي والمحاسبي\"], \"education\": \"دبلوم وأعلى\", \"job_title\": \"اخصائي موارد بشرية\", \"experience\": \"يفضل من سنة وأكثر\", \"company_name\": \"شركة عقارية\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_oLU9i5YtmPEs0c9ltlkxyq0E",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"Careers@cashin.sa\", \"domain\": \"cashin.sa\", \"region\": \"منطقة الرياض\", \"sectors\": [\"التجزئة والمبيعات المباشرة\"], \"education\": \"بكالوريوس\", \"job_title\": \"اخصائي مشتريات وتحصيل\", \"experience\": \"من سنتين واكثر\", \"company_name\": \"شركة تعمل في المجال اللوجستي\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_i7PtBEGIjnpil2aEDCUFtkZu",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"info@gfsxpress.com\", \"domain\": \"gfsxpress.com\", \"region\": \"منطقة الرياض\", \"sectors\": [\"الخدمات اللوجستية والأمنية\"], \"education\": \"غير محدد\", \"job_title\": \"اخصائية خدمة عملاء\", \"experience\": \"غير محدد\", \"company_name\": \"شركة تعمل في المجال اللوجستي\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_ZQU2K3pOZyexcQWK1B2lF2zc",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الرياض\", \"date\": \"2024-07-13\", \"email\": \"info@gfsxpress.com\", \"domain\": \"gfsxpress.com\", \"region\": \"منطقة الرياض\", \"sectors\": [\"الخدمات اللوجستية والأمنية\"], \"education\": \"غير محدد\", \"job_title\": \"محصل مالي\", \"experience\": \"يفضل من لدية خبرة كاشير او محصل مالي\", \"company_name\": \"شركة تعمل في المجال اللوجستي\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_vZSUuzdAnBsaL1v8M0oD0eyd",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"جدة\", \"date\": \"2024-07-13\", \"email\": \"nadia.alotaibi@bravoint.com\", \"domain\": \"bravoint.com\", \"region\": \"منطقة مكة المكرمة\", \"sectors\": [\"القطاع المالي والمحاسبي\"], \"education\": \"غير محدد\", \"job_title\": \"أخصائية موارد بشرية\", \"experience\": \"غير محدد\", \"company_name\": \"شركة -قطاع تجزئة\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_OWwtWOj9hCB5kCgM2eL1Rpo0",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"الدمام\", \"date\": \"2024-07-13\", \"email\": \"hr@eastgas.com.sa\", \"domain\": \"eastgas.com.sa\", \"region\": \"منطقة الشرقية\", \"sectors\": [\"القطاع المالي والمحاسبي\"], \"education\": \"بكالوريوس محاسبة أو مالية\", \"job_title\": \"مدير مالي\", \"experience\": \"لا تقل عن 5-10 سنوات\", \"company_name\": \"شركة في المدينة الصناعية الثانية\", \"specialization\": \"اخرى\"}"
                }
                },
                {
                "id": "call_4Uv72Sc02Q99OcXVkv0DbbHS",
                "type": "function",
                "function": {
                    "name": "ad_extractor_func",
                    "arguments": "{\"city\": \"المدينة المنورة\", \"date\": \"2024-07-13\", \"email\": \"hr@mcd.org.sa\", \"domain\": \"mcd.org.sa\", \"region\": \"منطقة المدينة المنورة\", \"sectors\": [\"التعليم والتطوير المهني\"], \"education\": \"بكالوريوس\", \"job_title\": \"منسق برامج و مشاريع\", \"experience\": \"خبرة لا تقل عن عام\", \"company_name\": \"جمعية المدينة المنورة الاهلية لتنمية المجتمع\", \"specialization\": \"اخرى\"}"
                }
                }
            ]
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_xAB64ZmpNNO1hhRQ5C9YzVjk"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_FC42L0D3w7gjDeczL8GaJy7T"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_2zSHWkEOehWbae5G7eaK4DzH"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_u3E2UwwJCHzMuGJ2BTV3U9av"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_oLU9i5YtmPEs0c9ltlkxyq0E"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_i7PtBEGIjnpil2aEDCUFtkZu"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_ZQU2K3pOZyexcQWK1B2lF2zc"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_vZSUuzdAnBsaL1v8M0oD0eyd"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_OWwtWOj9hCB5kCgM2eL1Rpo0"
            },
            {
            "role": "tool",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ],
            "tool_call_id": "call_4Uv72Sc02Q99OcXVkv0DbbHS"
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            }
        ],
        temperature=0.2,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        tools=[
            {
            "type": "function",
            "function": {
                "name": "ad_extractor_func",
                "description": "Extracts specific information from advertisements in JSON format with fixed lists for cities, regions, main sectors, subcategories, and other fields. If a field does not match a list item, it defaults to 'غير محدد'.",
                "parameters": {
                "type": "object",
                "required": [
                    "company_name",
                    "job_title",
                    "city",
                    "region",
                    "sectors",
                    "specialization",
                    "experience",
                    "education",
                    "email",
                    "domain",
                    "date"
                ],
                "properties": {
                    "city": {
                    "enum": [
                        "الرياض",
                        "الدرعية",
                        "الخرج",
                        "الدلم",
                        "المجمعة",
                        "وادي الدواسر",
                        "مكة المكرمة",
                        "جدة",
                        "الطائف",
                        "المدينة المنورة",
                        "ينبع",
                        "الدمام",
                        "الأحساء",
                        "أبها",
                        "خميس مشيط",
                        "تبوك",
                        "حائل",
                        "جازان",
                        "عرعر",
                        "نجران",
                        "الباحة",
                        "سكاكا",
                        "غير محدد"
                    ],
                    "type": "string",
                    "description": "City or region of the advertisement, selected from a predefined list."
                    },
                    "date": {
                    "type": "string",
                    "description": "Date of the advertisement in YYYY-MM-DD format."
                    },
                    "email": {
                    "type": "string",
                    "description": "Email address of the advertiser or contact."
                    },
                    "domain": {
                    "type": "string",
                    "description": "Email domain where the ad was posted."
                    },
                    "region": {
                    "enum": [
                        "منطقة الرياض",
                        "منطقة مكة المكرمة",
                        "منطقة المدينة المنورة",
                        "المنطقة الشرقية",
                        "منطقة القصيم",
                        "منطقة عسير",
                        "منطقة تبوك",
                        "منطقة حائل",
                        "منطقة جازان",
                        "منطقة نجران",
                        "منطقة الباحة",
                        "منطقة الجوف",
                        "منطقة الحدود الشمالية",
                        "غير محدد"
                    ],
                    "type": "string",
                    "default": "غير محدد",
                    "description": "Region of the city, matched to a predefined list or set to 'غير محدد' if unmatched."
                    },
                    "sectors": {
                    "type": "array",
                    "items": {
                        "enum": [
                        "القطاع الصناعي والإنتاجي",
                        "الصناعة الكيميائية والبتروكيماويات",
                        "القطاع الهندسي والفني",
                        "قطاع العقارات والمقاولات",
                        "التجزئة والمبيعات المباشرة",
                        "الاتصالات وتقنية المعلومات",
                        "الأغذية والمشروبات",
                        "التسويق والعلاقات العامة",
                        "الخدمات اللوجستية والأمنية",
                        "الخدمات القانونية والاستشارية",
                        "القطاع المالي والمحاسبي",
                        "الرعاية الصحية والخدمات الطبية",
                        "الإدارة والدعم الإداري",
                        "التعليم والتطوير المهني",
                        "التصميم والفنون الإبداعية",
                        "البيئة والاستدامة",
                        "السياحة والضيافة",
                        "البحث والتطوير",
                        "قطاع الإعلام والنشر",
                        "أخرى"
                        ],
                        "type": "string"
                    },
                    "description": "Primary sectors of the job, selected from a predefined list."
                    },
                    "education": {
                    "type": "string",
                    "description": "Required education level for the job."
                    },
                    "job_title": {
                    "type": "string",
                    "description": "Job title as advertised."
                    },
                    "experience": {
                    "type": "string",
                    "description": "Experience required for the job, if specified."
                    },
                    "company_name": {
                    "type": "string",
                    "description": "The name of the company or organization posting the job."
                    },
                    "specialization": {
                    "enum": [
                        "تصنيع المعادن",
                        "تصنيع المواد البلاستيكية",
                        "تصنيع المواد الغذائية",
                        "تصنيع الأجهزة الكهربائية",
                        "التصنيع الخفيف والثقيل",
                        "الكيمياء العضوية",
                        "الكيمياء غير العضوية",
                        "هندسة البتروكيماويات",
                        "إنتاج المواد الكيميائية المتخصصة",
                        "معالجة المياه والنفايات",
                        "الهندسة المدنية",
                        "الهندسة الميكانيكية",
                        "الهندسة الكهربائية",
                        "الهندسة المعمارية",
                        "التصميم الصناعي",
                        "إدارة المشاريع",
                        "تصميم الداخلي",
                        "تسويق العقارات",
                        "تطوير العقارات",
                        "مقاولات البناء",
                        "إدارة المبيعات",
                        "خدمة العملاء",
                        "التسويق الرقمي",
                        "إدارة المخزون",
                        "التحليل التجاري",
                        "تطوير البرمجيات",
                        "أمن المعلومات",
                        "الشبكات والاتصالات",
                        "إدارة البيانات",
                        "الذكاء الاصطناعي",
                        "تطوير المنتجات الغذائية",
                        "إدارة الجودة",
                        "تسويق الأغذية",
                        "التغذية",
                        "سلامة الأغذية",
                        "التسويق الرقمي",
                        "إدارة العلامة التجارية",
                        "العلاقات العامة",
                        "الحملات الإعلانية",
                        "تحليل السوق",
                        "إدارة سلسلة الإمداد",
                        "التخزين والنقل",
                        "الأمن والسلامة",
                        "إدارة المخاطر",
                        "التخطيط اللوجستي",
                        "الاستشارات القانونية",
                        "التحكيم والوساطة",
                        "الاستشارات المالية",
                        "حقوق الملكية الفكرية",
                        "التراخيص والتراخيص التجارية",
                        "المحاسبة المالية",
                        "التدقيق الداخلي",
                        "التخطيط المالي",
                        "تحليل البيانات المالية",
                        "الإدارة المالية",
                        "التمريض",
                        "الإدارة الصحية",
                        "الصيدلة",
                        "الطب النفسي",
                        "العلاج الطبيعي",
                        "إدارة المشاريع",
                        "إدارة الموارد البشرية",
                        "الدعم الإداري",
                        "إدارة المكاتب",
                        "إدارة العمليات",
                        "التدريب والتطوير",
                        "التعليم الإلكتروني",
                        "تصميم المناهج",
                        "استراتيجيات التعلم",
                        "التعليم المستمر",
                        "التصميم الجرافيكي",
                        "تصميم الأزياء",
                        "الفنون التشكيلية",
                        "التصوير الفوتوغرافي",
                        "الإنتاج الإعلامي",
                        "إدارة الموارد البيئية",
                        "الطاقة المتجددة",
                        "تحليل التأثير البيئي",
                        "الاستدامة المؤسسية",
                        "علم الأحياء البيئي",
                        "إدارة الفنادق",
                        "إدارة المطاعم",
                        "تسويق السياحة",
                        "إدارة الفعاليات",
                        "توجيه السياح",
                        "البحث العلمي",
                        "تطوير المنتجات",
                        "الابتكار التكنولوجي",
                        "دراسات السوق",
                        "تحليل البيانات",
                        "الصحافة",
                        "التحرير والنشر",
                        "الإنتاج التلفزيوني",
                        "الإعلام الرقمي",
                        "إدارة المحتوى",
                        "خدمات الاستشارات العامة",
                        "الأعمال التطوعية",
                        "الفنون القتالية",
                        "تكنولوجيا المعلومات",
                        "تخصصات جديدة تظهر في السوق",
                        "اخرى"
                    ],
                    "type": "string",
                    "description": "Specific specialization or subcategory within the main sector."
                    }
                },
                "additionalProperties": False
                },
                "strict": True
            }
            }
        ],
        parallel_tool_calls=True,
        response_format={
            "type": "json_schema",
            "json_schema": {
            "name": "ad_extractor_schema",
            "strict": True,
            "schema": {
                "type": "object",
                "required": [
                "company_name",
                "job_title",
                "city",
                "region",
                "sectors",
                "specialization",
                "experience",
                "education",
                "email",
                "domain",
                "date"
                ],
                "properties": {
                "city": {
                    "enum": [
                    "الرياض",
                    "الدرعية",
                    "الخرج",
                    "الدلم",
                    "المجمعة",
                    "وادي الدواسر",
                    "مكة المكرمة",
                    "جدة",
                    "الطائف",
                    "المدينة المنورة",
                    "ينبع",
                    "الدمام",
                    "الأحساء",
                    "أبها",
                    "خميس مشيط",
                    "تبوك",
                    "حائل",
                    "جازان",
                    "عرعر",
                    "نجران",
                    "الباحة",
                    "سكاكا",
                    "غير محدد"
                    ],
                    "type": "string",
                    "description": "City or region of the advertisement, selected from a predefined list."
                },
                "date": {
                    "type": "string",
                    "description": "Date of the advertisement in YYYY-MM-DD format."
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the advertiser or contact."
                },
                "domain": {
                    "type": "string",
                    "description": "Email domain where the ad was posted."
                },
                "region": {
                    "enum": [
                    "منطقة الرياض",
                    "منطقة مكة المكرمة",
                    "منطقة المدينة المنورة",
                    "المنطقة الشرقية",
                    "منطقة القصيم",
                    "منطقة عسير",
                    "منطقة تبوك",
                    "منطقة حائل",
                    "منطقة جازان",
                    "منطقة نجران",
                    "منطقة الباحة",
                    "منطقة الجوف",
                    "منطقة الحدود الشمالية",
                    "غير محدد"
                    ],
                    "type": "string",
                    "default": "غير محدد",
                    "description": "Region of the city, matched to a predefined list or set to 'غير محدد' if unmatched."
                },
                "sectors": {
                    "type": "array",
                    "items": {
                    "enum": [
                        "القطاع الصناعي والإنتاجي",
                        "الصناعة الكيميائية والبتروكيماويات",
                        "القطاع الهندسي والفني",
                        "قطاع العقارات والمقاولات",
                        "التجزئة والمبيعات المباشرة",
                        "الاتصالات وتقنية المعلومات",
                        "الأغذية والمشروبات",
                        "التسويق والعلاقات العامة",
                        "الخدمات اللوجستية والأمنية",
                        "الخدمات القانونية والاستشارية",
                        "القطاع المالي والمحاسبي",
                        "الرعاية الصحية والخدمات الطبية",
                        "الإدارة والدعم الإداري",
                        "التعليم والتطوير المهني",
                        "التصميم والفنون الإبداعية",
                        "البيئة والاستدامة",
                        "السياحة والضيافة",
                        "البحث والتطوير",
                        "قطاع الإعلام والنشر",
                        "أخرى"
                    ],
                    "type": "string"
                    },
                    "description": "Primary sectors of the job, selected from a predefined list."
                },
                "education": {
                    "type": "string",
                    "description": "Required education level for the job."
                },
                "job_title": {
                    "type": "string",
                    "description": "Job title as advertised."
                },
                "experience": {
                    "type": "string",
                    "description": "Experience required for the job, if specified."
                },
                "company_name": {
                    "type": "string",
                    "description": "The name of the company or organization posting the job."
                },
                "specialization": {
                    "enum": [
                    "تصنيع المعادن",
                    "تصنيع المواد البلاستيكية",
                    "تصنيع المواد الغذائية",
                    "تصنيع الأجهزة الكهربائية",
                    "التصنيع الخفيف والثقيل",
                    "الكيمياء العضوية",
                    "الكيمياء غير العضوية",
                    "هندسة البتروكيماويات",
                    "إنتاج المواد الكيميائية المتخصصة",
                    "معالجة المياه والنفايات",
                    "الهندسة المدنية",
                    "الهندسة الميكانيكية",
                    "الهندسة الكهربائية",
                    "الهندسة المعمارية",
                    "التصميم الصناعي",
                    "إدارة المشاريع",
                    "تصميم الداخلي",
                    "تسويق العقارات",
                    "تطوير العقارات",
                    "مقاولات البناء",
                    "إدارة المبيعات",
                    "خدمة العملاء",
                    "التسويق الرقمي",
                    "إدارة المخزون",
                    "التحليل التجاري",
                    "تطوير البرمجيات",
                    "أمن المعلومات",
                    "الشبكات والاتصالات",
                    "إدارة البيانات",
                    "الذكاء الاصطناعي",
                    "تطوير المنتجات الغذائية",
                    "إدارة الجودة",
                    "تسويق الأغذية",
                    "التغذية",
                    "سلامة الأغذية",
                    "التسويق الرقمي",
                    "إدارة العلامة التجارية",
                    "العلاقات العامة",
                    "الحملات الإعلانية",
                    "تحليل السوق",
                    "إدارة سلسلة الإمداد",
                    "التخزين والنقل",
                    "الأمن والسلامة",
                    "إدارة المخاطر",
                    "التخطيط اللوجستي",
                    "الاستشارات القانونية",
                    "التحكيم والوساطة",
                    "الاستشارات المالية",
                    "حقوق الملكية الفكرية",
                    "التراخيص والتراخيص التجارية",
                    "المحاسبة المالية",
                    "التدقيق الداخلي",
                    "التخطيط المالي",
                    "تحليل البيانات المالية",
                    "الإدارة المالية",
                    "التمريض",
                    "الإدارة الصحية",
                    "الصيدلة",
                    "الطب النفسي",
                    "العلاج الطبيعي",
                    "إدارة المشاريع",
                    "إدارة الموارد البشرية",
                    "الدعم الإداري",
                    "إدارة المكاتب",
                    "إدارة العمليات",
                    "التدريب والتطوير",
                    "التعليم الإلكتروني",
                    "تصميم المناهج",
                    "استراتيجيات التعلم",
                    "التعليم المستمر",
                    "التصميم الجرافيكي",
                    "تصميم الأزياء",
                    "الفنون التشكيلية",
                    "التصوير الفوتوغرافي",
                    "الإنتاج الإعلامي",
                    "إدارة الموارد البيئية",
                    "الطاقة المتجددة",
                    "تحليل التأثير البيئي",
                    "الاستدامة المؤسسية",
                    "علم الأحياء البيئي",
                    "إدارة الفنادق",
                    "إدارة المطاعم",
                    "تسويق السياحة",
                    "إدارة الفعاليات",
                    "توجيه السياح",
                    "البحث العلمي",
                    "تطوير المنتجات",
                    "الابتكار التكنولوجي",
                    "دراسات السوق",
                    "تحليل البيانات",
                    "الصحافة",
                    "التحرير والنشر",
                    "الإنتاج التلفزيوني",
                    "الإعلام الرقمي",
                    "إدارة المحتوى",
                    "خدمات الاستشارات العامة",
                    "الأعمال التطوعية",
                    "الفنون القتالية",
                    "تكنولوجيا المعلومات",
                    "تخصصات جديدة تظهر في السوق",
                    "اخرى"
                    ],
                    "type": "string",
                    "description": "Specific specialization or subcategory within the main sector."
                }
                },
                "additionalProperties": False
            }
            }
        }
        )
                    
        json_results = []
        
        if response.choices[0].message.tool_calls is not None:
            for call in response.choices[0].message.tool_calls:
                json_results.append(eval(call.function.arguments))
    
    except Exception as e:
        print(f"Error fetching response for prompt '{prompt[:30]}': {e}")
        
    await asyncio.sleep(3)
    
    if json_results is not None:
        return json_results 
    else:
        print(f"Warning: No valid tool_calls in response for prompt: {prompt[:30]}")


