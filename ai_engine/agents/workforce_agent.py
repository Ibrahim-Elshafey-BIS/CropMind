"""
CropMind - Workforce Agent
Manages farm workers, tasks, attendance, and daily field assignments

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ai_engine.agents.base_agent import BaseAgent


class WorkforceAgent(BaseAgent):
    """
    Workforce Agent for managing workers, tasks, and daily assignments.
    Analyzes attendance, reviews tasks, and assigns daily field work.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Workforce Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Workforce Agent",
            description="Manages worker tasks, attendance, and daily field assignments",
            groq_api_key=groq_api_key
        )
        self.log("✅ Workforce Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive workforce analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - workers: list of dicts with worker_id, name, role, attendance, tasks_completed, daily_wage
                - tasks: list of dicts with task_id, task_name, priority, assigned_to, status, due_date
                - crop_type: str
                - area: float (area in feddans)
                
        Returns:
            Dict with workforce status and recommendations
        """
        try:
            farm_id = input_data.get("farm_id")
            workers = input_data.get("workers", [])
            tasks = input_data.get("tasks", [])
            crop_type = input_data.get("crop_type", "general")
            area = input_data.get("area", 1.0)
            
            self.log(f"👥 Analyzing workforce for farm {farm_id}")
            
            # Step 1: Analyze attendance
            attendance_analysis = self.analyze_attendance(workers)
            
            # Step 2: Review tasks
            task_review = self.review_tasks(tasks)
            
            # Step 3: Calculate labor costs
            labor_costs = self.calculate_labor_costs(workers)
            
            # Step 4: Assign daily tasks
            task_assignments = self.assign_daily_tasks(workers, tasks)
            
            # Step 5: Calculate workforce efficiency
            efficiency = self._calculate_efficiency(workers, tasks)
            
            # Step 6: Generate report
            workforce_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "area": area,
                "workers": workers,
                "tasks": tasks,
                "attendance_analysis": attendance_analysis,
                "task_review": task_review,
                "labor_costs": labor_costs,
                "task_assignments": task_assignments,
                "efficiency": efficiency
            }
            
            report = self.generate_workforce_report(workforce_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "total_workers": len(workers),
                "active_workers": attendance_analysis.get("active_workers", 0),
                "attendance_rate": attendance_analysis.get("attendance_rate", 0),
                "tasks_completed": task_review.get("completed", 0),
                "tasks_overdue": task_review.get("overdue", 0),
                "daily_labor_cost": labor_costs.get("daily_total", 0),
                "task_assignments": task_assignments,
                "efficiency_score": efficiency.get("overall_efficiency", 0),
                "report": report,
                "summary": self._generate_summary(workforce_data)
            })
            
        except Exception as e:
            self.log(f"❌ Error in workforce analysis: {e}")
            return self.format_error(str(e))
    
    def analyze_attendance(self, workers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze worker attendance patterns.
        
        Args:
            workers: List of worker records
            
        Returns:
            Dict with attendance analysis
        """
        self.log("📊 Analyzing attendance...")
        
        total_workers = len(workers)
        present_today = 0
        absent_today = 0
        attendance_history = []
        
        for worker in workers:
            attendance = worker.get("attendance", {})
            
            # Check today's attendance
            if attendance.get("today", False):
                present_today += 1
            else:
                absent_today += 1
            
            # Get attendance history (last 7 days)
            history = attendance.get("history", [])
            if history:
                attendance_history.extend(history)
        
        # Calculate attendance rate
        present_rate = (present_today / total_workers * 100) if total_workers > 0 else 0
        
        # Calculate weekly attendance
        weekly_attendance = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_workers = [w for w in workers if w.get("attendance", {}).get("history", []) and 
                          any(d.get("date") == date and d.get("present") for d in w.get("attendance", {}).get("history", []))]
            weekly_attendance.append({
                "date": date,
                "present": len(day_workers),
                "total": total_workers
            })
        
        return {
            "total_workers": total_workers,
            "present_today": present_today,
            "absent_today": absent_today,
            "attendance_rate": round(present_rate, 1),
            "weekly_attendance": weekly_attendance,
            "status": "Good" if present_rate >= 80 else "Needs Improvement" if present_rate >= 60 else "Critical"
        }
    
    def review_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Review task status and identify overdue tasks.
        
        Args:
            tasks: List of task records
            
        Returns:
            Dict with task analysis
        """
        self.log("📋 Reviewing tasks...")
        
        total_tasks = len(tasks)
        completed = 0
        in_progress = 0
        pending = 0
        overdue = 0
        
        for task in tasks:
            status = task.get("status", "pending")
            due_date = task.get("due_date")
            
            if status == "completed":
                completed += 1
            elif status == "in_progress":
                in_progress += 1
            else:
                pending += 1
            
            # Check if overdue - with robust date parsing
            if status != "completed" and due_date:
                try:
                    # Try ISO format first (more flexible)
                    if isinstance(due_date, str):
                        try:
                            # Try ISO format (handles both date and datetime strings)
                            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        except ValueError:
                            # Fallback to date format
                            due = datetime.strptime(due_date, "%Y-%m-%d")
                    else:
                        due = due_date
                    
                    # Compare with current time
                    if due < datetime.now():
                        overdue += 1
                except Exception as e:
                    # Log warning and skip this task for overdue calculation
                    task_name = task.get("task_name", "Unknown task")
                    self.log(f"⚠️ Could not parse due_date '{due_date}' for task '{task_name}': {e}")
                    # Continue with next task - don't count as overdue
                    continue
        
        # Calculate completion rate
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Task distribution by priority
        priority_distribution = {}
        for task in tasks:
            priority = task.get("priority", "medium")
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1),
            "priority_distribution": priority_distribution,
            "status": "On Track" if overdue == 0 else f"{overdue} tasks overdue"
        }
    
    def calculate_labor_costs(self, workers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate daily and weekly labor costs.
        
        Args:
            workers: List of worker records
            
        Returns:
            Dict with labor cost analysis
        """
        self.log("💰 Calculating labor costs...")
        
        daily_total = 0
        role_breakdown = {}
        
        for worker in workers:
            daily_wage = worker.get("daily_wage", 0)
            role = worker.get("role", "laborer")
            attendance = worker.get("attendance", {})
            
            # Only count present workers
            if attendance.get("today", False):
                daily_total += daily_wage
            
            # Role breakdown
            if role not in role_breakdown:
                role_breakdown[role] = {"count": 0, "total_wage": 0}
            role_breakdown[role]["count"] += 1
            role_breakdown[role]["total_wage"] += daily_wage
        
        # Calculate weekly estimate
        weekly_estimate = daily_total * 6  # Assuming 6 working days
        
        return {
            "daily_total": round(daily_total, 2),
            "weekly_estimate": round(weekly_estimate, 2),
            "role_breakdown": role_breakdown,
            "average_wage_per_worker": round(daily_total / len(workers), 2) if workers else 0
        }
    
    def assign_daily_tasks(
        self,
        workers: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Assign daily tasks to available workers.
        
        Args:
            workers: List of worker records
            tasks: List of task records
            
        Returns:
            List of task assignments
        """
        self.log("📋 Assigning daily tasks...")
        
        # Get available workers
        available_workers = [
            w for w in workers
            if w.get("attendance", {}).get("today", False)
        ]
        
        if not available_workers:
            return [{"status": "No workers available"}]
        
        # Get pending tasks (not completed)
        pending_tasks = [
            t for t in tasks
            if t.get("status") != "completed"
        ]
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 3))
        
        assignments = []
        
        # Assign tasks to workers in round-robin
        worker_idx = 0
        for task in pending_tasks:
            if not available_workers:
                break
            
            worker = available_workers[worker_idx % len(available_workers)]
            worker_name = worker.get("name", "Unknown")
            worker_role = worker.get("role", "laborer")
            
            # Check if worker is suitable for the task
            if worker_role == "supervisor" and task.get("requires_supervision", False):
                is_qualified = True
            elif worker_role == "laborer" and task.get("requires_specialist", False):
                is_qualified = False
            else:
                is_qualified = True
            
            if is_qualified:
                assignments.append({
                    "task_id": task.get("task_id"),
                    "task_name": task.get("task_name"),
                    "assigned_to": worker_name,
                    "worker_id": worker.get("worker_id"),
                    "priority": task.get("priority", "medium"),
                    "status": "assigned",
                    "estimated_hours": task.get("estimated_hours", 4),
                    "due_date": task.get("due_date")
                })
                worker_idx += 1
        
        return assignments
    
    def _calculate_efficiency(
        self,
        workers: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate workforce efficiency score.
        
        Args:
            workers: List of worker records
            tasks: List of task records
            
        Returns:
            Dict with efficiency metrics
        """
        self.log("📊 Calculating efficiency...")
        
        # Task completion rate
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Attendance rate
        present = len([w for w in workers if w.get("attendance", {}).get("today", False)])
        attendance_rate = (present / len(workers) * 100) if workers else 0
        
        # Average tasks per worker
        tasks_per_worker = completed_tasks / len(workers) if workers else 0
        
        # Combined efficiency score
        overall_efficiency = (completion_rate * 0.5 + attendance_rate * 0.3 + min(tasks_per_worker * 20, 100) * 0.2)
        
        return {
            "task_completion_rate": round(completion_rate, 1),
            "attendance_rate": round(attendance_rate, 1),
            "tasks_per_worker": round(tasks_per_worker, 1),
            "overall_efficiency": round(overall_efficiency, 1),
            "rating": "Excellent" if overall_efficiency >= 80 else "Good" if overall_efficiency >= 60 else "Needs Improvement"
        }
    
    def generate_workforce_report(self, data: Dict[str, Any]) -> str:
        """
        Generate workforce report in Arabic using LLM.
        
        Args:
            data: Dict with all workforce data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating workforce report...")
        
        prompt = self._build_report_prompt(data)
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build the prompt for workforce report generation.
        """
        attendance = data.get("attendance_analysis", {})
        tasks = data.get("task_review", {})
        costs = data.get("labor_costs", {})
        efficiency = data.get("efficiency", {})
        assignments = data.get("task_assignments", [])
        
        prompt = f"""
أنت خبير إدارة موارد بشرية زراعية في نظام CropMind متخصص في إدارة العمال والمهام الزراعية.

البيانات المتاحة:
- إجمالي العمال: {attendance.get('total_workers', 0)}
- الحضور اليومي: {attendance.get('present_today', 0)} عامل
- نسبة الحضور: {attendance.get('attendance_rate', 0)}%
- المهام المكتملة: {tasks.get('completed', 0)} من {tasks.get('total_tasks', 0)}
- المهام المتأخرة: {tasks.get('overdue', 0)}
- تكلفة العمالة اليومية: {costs.get('daily_total', 0)} جنيه
- كفاءة القوى العاملة: {efficiency.get('overall_efficiency', 0)}%

المهام المقترحة اليوم:
{self._format_assignments(assignments)}

المطلوب:
اكتب تقريراً مفصلاً باللغة العربية عن القوى العاملة في المزرعة يشمل:
1. تحليل الحضور والغياب
2. حالة المهام وإنجازها
3. تكاليف العمالة
4. كفاءة العمال
5. خطة عمل مقترحة لتحسين الإنتاجية

اكتب التقرير بصيغة واضحة ومباشرة مع عناوين فرعية.
"""
        return prompt
    
    def _format_assignments(self, assignments: List[Dict[str, Any]]) -> str:
        """
        Format task assignments for the prompt.
        """
        if not assignments:
            return "- No tasks assigned"
        
        lines = []
        for a in assignments[:10]:
            lines.append(f"- {a.get('task_name')} → {a.get('assigned_to')} ({a.get('priority')} priority)")
        
        return "\n".join(lines)
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quick summary of workforce analysis.
        """
        attendance = data.get("attendance_analysis", {})
        tasks = data.get("task_review", {})
        costs = data.get("labor_costs", {})
        efficiency = data.get("efficiency", {})
        
        return {
            "active_workers": attendance.get("present_today", 0),
            "attendance_rate": attendance.get("attendance_rate", 0),
            "tasks_completed": tasks.get("completed", 0),
            "tasks_overdue": tasks.get("overdue", 0),
            "daily_labor_cost": costs.get("daily_total", 0),
            "efficiency_score": efficiency.get("overall_efficiency", 0),
            "status": "Good" if efficiency.get("overall_efficiency", 0) >= 70 else "Needs Improvement"
        }
