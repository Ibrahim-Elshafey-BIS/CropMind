"""
CropMind - Farm Intelligence Prompts
Prompt templates for Farm Intelligence Agent

Author: CropMind Team
Date: 2026
"""

# Health report prompt - generates comprehensive farm health report
HEALTH_REPORT_PROMPT = """
أنت خبير زراعي ذكي في نظام CropMind. قم بإنشاء تقرير صحي مفصل باللغة العربية للفارم التالي:

المحصول: {crop_type}
درجة الصحة العامة: {health_score}/100

بيانات الحساسات:
- درجة الحرارة: {temperature}°C
- الرطوبة: {humidity}%
- رطوبة التربة: {soil_moisture}%
- درجة الحموضة (pH): {ph}
- النيتروجين: {nitrogen} ppm

نتائج التحليل:
- الحالات الشاذة: {anomaly_status}
- الأمراض: {disease_detected}
- إنتاجية متوقعة: {yield_prediction}

المطلوب:
1. تقييم الحالة الصحية العامة للفارم
2. تحديد المشاكل المحتملة
3. تقديم توصيات عملية للتحسين
4. خطة عمل مقترحة للأيام القادمة

اكتب التقرير بصيغة احترافية واضحة مع عناوين فرعية.
"""

# Anomaly alert prompt - short warning message for sensor anomalies
ANOMALY_ALERT_PROMPT = """
تحذير: تم اكتشاف قراءة غير طبيعية في مستشعر {sensor_type}.
القيمة: {value}
الحد المسموح: {threshold}

يرجى فحص المعدات والتحقق من الحالة.
"""
