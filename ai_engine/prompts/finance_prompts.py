"""
CropMind - Finance Prompts
Prompt templates for Finance Agent

Author: CropMind Team
Date: 2026
"""

# Financial report prompt - generates comprehensive financial report
FINANCIAL_REPORT_PROMPT = """
أنت خبير مالي زراعي في نظام CropMind متخصص في التحليل المالي للمزارع.

البيانات المتاحة:
- المحصول: {crop}
- المساحة: {area} فدان
- إجمالي التكاليف: {total_cost} جنيه
- إجمالي الإيرادات: {total_revenue} جنيه
- صافي الربح: {net_profit} جنيه
- العائد على الاستثمار (ROI): {roi}%
- مستوى الربحية: {profitability_level}
- نقطة التعادل (إنتاج): {break_even_yield} طن

المطلوب:
اكتب تقريراً مالياً مفصلاً باللغة العربية للمزرعة يشمل:
1. تحليل التكاليف والإيرادات
2. تحليل الربحية والعائد على الاستثمار
3. تحليل نقطة التعادل
4. توقعات مالية للمواسم القادمة
5. توصيات لتحسين الأداء المالي

اكتب التقرير بصيغة واضحة ومباشرة مع عناوين فرعية.
"""

# Cost breakdown prompt - brief cost analysis in Arabic
COST_BREAKDOWN_PROMPT = """
تحليل التكاليف لمحصول {crop}:

{costs_dict}

قم بتقديم تحليل مختصر للتكاليف باللغة العربية، مع تحديد أكبر بند تكلفة وتوصية لتقليل التكاليف.
"""
