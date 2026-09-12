"""
CropMind - Inventory Agent
Manages farm inventory, stock levels, and purchase recommendations

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from ai_engine.agents.base_agent import BaseAgent


class InventoryAgent(BaseAgent):
    """
    Inventory Agent for tracking stock levels and generating purchase recommendations.
    Monitors inventory items and triggers automatic reorder suggestions.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Inventory Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Inventory Agent",
            description="Tracks stock levels and triggers automatic purchase recommendations",
            groq_api_key=groq_api_key
        )
        self.log("✅ Inventory Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive inventory analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - inventory: list of dicts with item_name, quantity, unit, min_threshold, cost_per_unit
                - crop_type: str
                - area: float (area in feddans)
                
        Returns:
            Dict with inventory status and recommendations
        """
        try:
            farm_id = input_data.get("farm_id")
            inventory = input_data.get("inventory", [])
            crop_type = input_data.get("crop_type", "general")
            area = input_data.get("area", 1.0)
            
            self.log(f"📦 Analyzing inventory for farm {farm_id}")
            
            # Step 1: Check stock levels
            stock_status = self.check_stock_levels(inventory)
            
            # Step 2: Identify low stock items
            low_stock_items = [item for item in stock_status if item.get("status") in ["LOW", "CRITICAL"]]
            
            # Step 3: Calculate reorder quantities
            reorder_recommendations = self.calculate_reorder_quantities(
                low_stock_items, crop_type, area
            )
            
            # Step 4: Generate purchase recommendations
            purchase_recommendations = self.generate_purchase_recommendations(
                reorder_recommendations
            )
            
            # Step 5: Calculate total purchase cost
            total_cost = sum(item.get("total_cost", 0) for item in purchase_recommendations)
            
            # Step 6: Generate report
            inventory_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "area": area,
                "inventory": inventory,
                "stock_status": stock_status,
                "low_stock_items": low_stock_items,
                "reorder_recommendations": reorder_recommendations,
                "purchase_recommendations": purchase_recommendations,
                "total_reorder_cost": total_cost
            }
            
            report = self.generate_inventory_report(inventory_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "total_items": len(inventory),
                "low_stock_items": len(low_stock_items),
                "critical_items": len([i for i in low_stock_items if i.get("status") == "CRITICAL"]),
                "reorder_recommendations": reorder_recommendations,
                "purchase_recommendations": purchase_recommendations,
                "total_reorder_cost": round(total_cost, 2),
                "report": report,
                "summary": self._generate_summary(inventory_data)
            })
            
        except Exception as e:
            self.log(f"❌ Error in inventory analysis: {e}")
            return self.format_error(str(e))
    
    def check_stock_levels(self, inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check stock levels and determine status for each item.
        
        Args:
            inventory: List of inventory items
            
        Returns:
            List with updated status for each item
        """
        self.log("🔍 Checking stock levels...")
        
        result = []
        
        for item in inventory:
            quantity = item.get("quantity", 0)
            min_threshold = item.get("min_threshold", 0)
            item_name = item.get("item_name", "Unknown")
            unit = item.get("unit", "unit")
            cost_per_unit = item.get("cost_per_unit", 0)
            
            # Determine stock status
            if quantity <= 0:
                status = "CRITICAL"
                status_message = "Out of stock! Immediate reorder required."
            elif quantity < min_threshold:
                status = "LOW"
                status_message = f"Low stock. Only {quantity} {unit} remaining."
            elif quantity < min_threshold * 1.5:
                status = "WARNING"
                status_message = f"Stock below 150% of minimum. Consider reordering soon."
            else:
                status = "OK"
                status_message = "Stock level is adequate."
            
            # Calculate shortage
            shortage = max(0, min_threshold - quantity)
            
            result.append({
                "item_name": item_name,
                "quantity": quantity,
                "unit": unit,
                "min_threshold": min_threshold,
                "cost_per_unit": cost_per_unit,
                "status": status,
                "status_message": status_message,
                "shortage": round(shortage, 2),
                "stock_ratio": round(quantity / min_threshold * 100, 1) if min_threshold > 0 else 0
            })
        
        return result
    
    def calculate_reorder_quantities(
        self,
        low_stock_items: List[Dict[str, Any]],
        crop_type: str,
        area: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate reorder quantities for low stock items based on crop and area.
        
        Args:
            low_stock_items: List of low stock items
            crop_type: Type of crop
            area: Area in feddans
            
        Returns:
            List with reorder recommendations
        """
        self.log(f"📋 Calculating reorder quantities for {len(low_stock_items)} items")
        
        # Crop-specific consumption rates (per feddan per season)
        consumption_rates = {
            "tomato": {"seeds": 0.5, "fertilizer": 200, "pesticide": 10, "irrigation_supplies": 50},
            "potato": {"seeds": 1.0, "fertilizer": 150, "pesticide": 8, "irrigation_supplies": 40},
            "onion": {"seeds": 0.8, "fertilizer": 120, "pesticide": 6, "irrigation_supplies": 30},
            "wheat": {"seeds": 0.2, "fertilizer": 100, "pesticide": 5, "irrigation_supplies": 25},
            "rice": {"seeds": 0.3, "fertilizer": 120, "pesticide": 8, "irrigation_supplies": 60},
            "maize": {"seeds": 0.4, "fertilizer": 150, "pesticide": 7, "irrigation_supplies": 35},
            "cotton": {"seeds": 0.5, "fertilizer": 180, "pesticide": 12, "irrigation_supplies": 45},
            "sugarcane": {"seeds": 2.0, "fertilizer": 250, "pesticide": 15, "irrigation_supplies": 70},
            "general": {"seeds": 0.5, "fertilizer": 150, "pesticide": 8, "irrigation_supplies": 40}
        }
        
        rates = consumption_rates.get(crop_type.lower(), consumption_rates["general"])
        
        recommendations = []
        
        for item in low_stock_items:
            item_name = item.get("item_name", "").lower()
            quantity = item.get("quantity", 0)
            min_threshold = item.get("min_threshold", 0)
            unit = item.get("unit", "unit")
            cost_per_unit = item.get("cost_per_unit", 0)
            shortage = item.get("shortage", 0)
            
            # Determine reorder quantity based on consumption rate
            if "seed" in item_name:
                reorder_qty = rates.get("seeds", 0.5) * area
            elif "fertilizer" in item_name:
                reorder_qty = rates.get("fertilizer", 150) * area
            elif "pesticide" in item_name or "pest" in item_name:
                reorder_qty = rates.get("pesticide", 8) * area
            elif "irrigation" in item_name or "water" in item_name:
                reorder_qty = rates.get("irrigation_supplies", 40) * area
            else:
                # Use shortage as base and add buffer
                reorder_qty = shortage * 1.5
            
            # Round appropriately
            if unit in ["kg", "g", "tons"]:
                reorder_qty = round(reorder_qty, 2)
            else:
                reorder_qty = round(reorder_qty)
            
            # Ensure at least minimum order
            reorder_qty = max(reorder_qty, shortage + 10)
            
            # Calculate cost
            total_cost = reorder_qty * cost_per_unit
            
            recommendations.append({
                "item_name": item.get("item_name"),
                "current_quantity": quantity,
                "min_threshold": min_threshold,
                "shortage": shortage,
                "recommended_order": reorder_qty,
                "unit": unit,
                "cost_per_unit": cost_per_unit,
                "total_cost": round(total_cost, 2),
                "priority": "HIGH" if item.get("status") == "CRITICAL" else "MEDIUM",
                "based_on": "crop_consumption_rate"
            })
        
        return recommendations
    
    def generate_purchase_recommendations(
        self,
        reorder_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed purchase recommendations from reorder list.
        
        Args:
            reorder_recommendations: List of reorder recommendations
            
        Returns:
            List with purchase recommendations
        """
        self.log("🛒 Generating purchase recommendations...")
        
        recommendations = []
        
        for item in reorder_recommendations:
            recommendations.append({
                "item": item.get("item_name"),
                "quantity": item.get("recommended_order"),
                "unit": item.get("unit"),
                "estimated_cost": item.get("total_cost", 0),
                "priority": item.get("priority", "MEDIUM"),
                "action": "URGENT ORDER" if item.get("priority") == "HIGH" else "SCHEDULE ORDER",
                "reason": "Critical stock" if item.get("priority") == "HIGH" else "Low stock",
                "suggested_supplier": "Local Agricultural Supply"  # This could be enhanced with real suppliers
            })
        
        return recommendations
    
    def generate_inventory_report(self, data: Dict[str, Any]) -> str:
        """
        Generate inventory report in Arabic using LLM.
        
        Args:
            data: Dict with all inventory data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating inventory report...")
        
        prompt = self._build_report_prompt(data)
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build the prompt for inventory report generation.
        """
        total_items = len(data.get("inventory", []))
        low_stock = len(data.get("low_stock_items", []))
        critical = len([i for i in data.get("low_stock_items", []) if i.get("status") == "CRITICAL"])
        total_cost = data.get("total_reorder_cost", 0)
        
        # Get purchase recommendations summary
        recs = data.get("purchase_recommendations", [])
        rec_summary = "\n".join([
            f"- {r.get('item')}: {r.get('quantity')} {r.get('unit')} ({r.get('priority')} priority)"
            for r in recs[:5]
        ]) if recs else "- No urgent reorder needed"
        
        prompt = f"""
أنت خبير إدارة مخزون زراعي في نظام CropMind متخصص في إدارة المخزون الزراعي.

البيانات المتاحة:
- إجمالي العناصر في المخزون: {total_items}
- عناصر منخفضة المخزون: {low_stock}
- عناصر حرجة (تحتاج شراء عاجل): {critical}
- تكلفة إعادة الطلب المقدرة: {total_cost} جنيه
- توصيات الشراء المقترحة:
{rec_summary}

المطلوب:
اكتب تقريراً مفصلاً باللغة العربية عن حالة المخزون في المزرعة يشمل:
1. تحليل حالة المخزون الحالية
2. تحديد العناصر التي تحتاج شراء عاجل
3. خطة شراء مقترحة مع الأولويات
4. توصيات لتحسين إدارة المخزون مستقبلاً

اكتب التقرير بصيغة واضحة ومباشرة مع عناوين فرعية.
"""
        return prompt
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quick summary of inventory analysis.
        """
        inventory = data.get("inventory", [])
        low_stock = data.get("low_stock_items", [])
        recs = data.get("purchase_recommendations", [])
        
        total_value = sum(
            item.get("quantity", 0) * item.get("cost_per_unit", 0)
            for item in inventory
        )
        
        return {
            "total_items": len(inventory),
            "total_inventory_value": round(total_value, 2),
            "low_stock_items": len(low_stock),
            "critical_items": len([i for i in low_stock if i.get("status") == "CRITICAL"]),
            "reorder_recommendations": len(recs),
            "estimated_reorder_cost": data.get("total_reorder_cost", 0),
            "status": "NEEDS ATTENTION" if low_stock else "HEALTHY"
        }
