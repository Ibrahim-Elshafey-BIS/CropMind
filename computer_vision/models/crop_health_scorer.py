"""
CropMind - Crop Health Scorer
Converts disease detection results into health scores for the Farm DNA Score

Author: CropMind Team
Date: 2026
"""

from typing import Dict, List, Any, Optional
from collections import Counter


class CropHealthScorer:
    """
    Crop Health Scorer that converts disease detection results into health scores.
    Used for calculating the Farm DNA Score component.
    """
    
    def __init__(self):
        """Initialize the CropHealthScorer."""
        print("[CropHealthScorer] ✅ Initialized")
    
    def calculate_health_score(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate health score from a single disease prediction.
        
        Args:
            prediction: Result from predict_disease()
            
        Returns:
            Dict with health_score, status, color, recommendation, needs_attention
        """
        # Extract prediction data
        is_healthy = prediction.get("is_healthy", False)
        severity = prediction.get("severity", "Unknown")
        confidence = prediction.get("confidence", 0.0)
        disease_name = prediction.get("disease_name", "Unknown")
        crop = prediction.get("crop", "Unknown")
        plant_not_recognized = prediction.get("plant_not_recognized", False)
        
        # Calculate health score based on severity
        health_score = 0
        status = "Unknown"
        color = "gray"
        
        if plant_not_recognized:
            health_score = 50
            status = "Fair"
            color = "orange"
        elif is_healthy:
            # Healthy plants score 90-100 based on confidence
            if confidence >= 90:
                health_score = 98
            elif confidence >= 80:
                health_score = 95
            elif confidence >= 70:
                health_score = 90
            else:
                health_score = 85
            status = "Excellent"
            color = "green"
        elif severity == "Low":
            health_score = 80 + (confidence / 100) * 9  # 80-89
            status = "Good"
            color = "yellow"
        elif severity == "Medium":
            health_score = 50 + (confidence / 100) * 19  # 50-69
            status = "Fair"
            color = "orange"
        elif severity == "High":
            health_score = 10 + (confidence / 100) * 29  # 10-39
            status = "Poor"
            color = "red"
        else:
            health_score = 50
            status = "Fair"
            color = "orange"
        
        # Clamp score to 0-100
        health_score = max(0, min(100, health_score))
        
        # Generate recommendation based on health status
        recommendation = self._get_recommendation(
            health_score, is_healthy, disease_name, severity
        )
        
        return {
            "health_score": round(health_score, 2),
            "status": status,
            "color": color,
            "recommendation": recommendation,
            "needs_attention": health_score < 70,
            "disease_name": disease_name,
            "crop": crop,
            "is_healthy": is_healthy,
            "severity": severity
        }
    
    def _get_recommendation(
        self,
        health_score: float,
        is_healthy: bool,
        disease_name: str,
        severity: str
    ) -> str:
        """
        Generate recommendation based on health score.
        """
        if health_score >= 90:
            return "✅ المحصول بصحة ممتازة، استمر في برنامج الرعاية الحالي"
        
        elif health_score >= 80:
            return "✅ المحصول بصحة جيدة، استمر في المراقبة الوقائية"
        
        elif health_score >= 70:
            return "⚠️ المحصول بحالة جيدة، يوصى بالمراقبة الدورية"
        
        elif health_score >= 50:
            if not is_healthy:
                return f"🔶 تم اكتشاف {disease_name} بدرجة {severity}. يوصى بالعلاج الفوري"
            return "🔶 حالة المحصول متوسطة، يوصى بتحسين الرعاية"
        
        elif health_score >= 30:
            if not is_healthy:
                return f"🔴 {disease_name} بدرجة {severity} - يوصى بالتدخل العاجل واستشارة خبير"
            return "🔴 حالة المحصول سيئة، يوصى بالتدخل الفوري"
        
        else:
            return "🚨 حالة المحصول حرجة، يوصى بالتدخل الفوري واستشارة خبير زراعي"
    
    def score_field(self, field_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate health score for an entire field.
        
        Args:
            field_predictions: List of prediction results from multiple plants
            
        Returns:
            Dict with field health summary
        """
        if not field_predictions:
            return {
                "field_health_score": 0,
                "status": "No Data",
                "total_plants": 0,
                "healthy_plants": 0,
                "diseased_plants": 0,
                "diseases_found": [],
                "recommendation": "لا توجد بيانات كافية لتقييم الحقل"
            }
        
        scores = []
        healthy_count = 0
        diseased_count = 0
        diseases_found = []
        
        for pred in field_predictions:
            result = self.calculate_health_score(pred)
            scores.append(result["health_score"])
            
            if result["is_healthy"]:
                healthy_count += 1
            else:
                diseased_count += 1
                if result["disease_name"] != "Unknown":
                    diseases_found.append(result["disease_name"])
        
        # Calculate average health score
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine field status
        status = self._get_status(avg_score)
        
        # Get unique diseases
        disease_counts = Counter(diseases_found)
        top_diseases = [d for d, _ in disease_counts.most_common(3)]
        
        # Generate field recommendation
        recommendation = self._get_field_recommendation(
            avg_score, healthy_count, diseased_count, top_diseases
        )
        
        return {
            "field_health_score": round(avg_score, 2),
            "status": status,
            "total_plants": len(field_predictions),
            "healthy_plants": healthy_count,
            "diseased_plants": diseased_count,
            "diseases_found": top_diseases,
            "recommendation": recommendation
        }
    
    def score_farm(self, fields: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Calculate health score for the entire farm.
        
        Args:
            fields: Dict mapping field_name -> list of predictions
            
        Returns:
            Dict with farm health summary
        """
        if not fields:
            return {
                "farm_health_score": 0,
                "fields": {},
                "overall_status": "No Data",
                "critical_fields": [],
                "recommendation": "لا توجد بيانات كافية لتقييم المزرعة"
            }
        
        field_scores = {}
        critical_fields = []
        
        for field_name, predictions in fields.items():
            field_result = self.score_field(predictions)
            field_scores[field_name] = field_result
            
            if field_result["field_health_score"] < 40:
                critical_fields.append(field_name)
        
        # Calculate average farm health score
        all_scores = [f["field_health_score"] for f in field_scores.values() if f["field_health_score"] > 0]
        farm_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Overall farm status
        overall_status = self._get_status(farm_score)
        
        # Generate farm recommendation
        recommendation = self._get_farm_recommendation(
            farm_score, critical_fields, field_scores
        )
        
        return {
            "farm_health_score": round(farm_score, 2),
            "fields": field_scores,
            "overall_status": overall_status,
            "critical_fields": critical_fields,
            "recommendation": recommendation
        }
    
    def _get_status(self, score: float) -> str:
        """
        Get status label based on score.
        """
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def _get_field_recommendation(
        self,
        score: float,
        healthy_count: int,
        diseased_count: int,
        diseases: List[str]
    ) -> str:
        """
        Generate field-level recommendation.
        """
        if score >= 80:
            return "✅ الحقل بصحة ممتازة، استمر في الممارسات الحالية"
        
        elif score >= 60:
            return "✅ الحقل بصحة جيدة، استمر في المراقبة الوقائية"
        
        elif score >= 40:
            if diseased_count > 0:
                return f"⚠️ تم اكتشاف {len(diseases)} مرض في الحقل. يوصى بالعلاج الفوري للمناطق المصابة"
            return "⚠️ الحقل بحاجة إلى تحسين في الرعاية والتغذية"
        
        elif score >= 20:
            if diseases:
                return f"🔴 الحقل يعاني من أمراض ({', '.join(diseases[:2])}). يوصى بالتدخل العاجل واستشارة خبير"
            return "🔴 الحقل بحالة سيئة، يوصى بمراجعة خطة الرعاية بأكملها"
        
        else:
            return "🚨 الحقل بحالة حرجة، يوصى بالتدخل الفوري"
    
    def _get_farm_recommendation(
        self,
        farm_score: float,
        critical_fields: List[str],
        field_scores: Dict[str, Any]
    ) -> str:
        """
        Generate farm-level recommendation.
        """
        if farm_score >= 80:
            return "✅ المزرعة بصحة ممتازة، استمر في برامج الرعاية الحالية"
        
        elif farm_score >= 60:
            return "✅ المزرعة بصحة جيدة، استمر في المراقبة والتقييم الدوري"
        
        elif farm_score >= 40:
            if critical_fields:
                return f"⚠️ الحقول الحرجة: {', '.join(critical_fields)}. يوصى بالتركيز على تحسين هذه الحقول"
            return "⚠️ المزرعة بحاجة إلى تحسين في الرعاية والتخطيط"
        
        else:
            if critical_fields:
                return f"🔴 الحقول الحرجة: {', '.join(critical_fields)}. يوصى بالتدخل العاجل واستشارة خبير زراعي"
            return "🔴 المزرعة بحالة سيئة، يوصى بمراجعة خطة الإدارة بالكامل"
