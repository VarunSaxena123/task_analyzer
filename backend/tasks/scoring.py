from datetime import datetime, date

class ScoringStrategy:
    def calculate_scores(self, tasks):
        raise NotImplementedError

class SmartBalanceStrategy(ScoringStrategy):
    def calculate_scores(self, tasks):
        scored_tasks = []
        
        for task in tasks:
            task_copy = task.copy()
            
            urgency = self._calculate_urgency(task)
            importance = self._calculate_importance(task)
            effort = self._calculate_effort(task)
            dependencies = self._calculate_dependencies(task, tasks)
            
            score = (urgency * 0.4 + importance * 0.3 + effort * 0.2 + dependencies * 0.1)
            
            task_copy['priority_score'] = round(score, 2)
            task_copy['explanation'] = self._get_explanation(urgency, importance, effort, dependencies)
            
            scored_tasks.append(task_copy)
        
        return scored_tasks
    
    def _calculate_urgency(self, task):
        try:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            today = date.today()
            days_until = (due_date - today).days
            
            if days_until < 0:
                return 100
            elif days_until == 0:
                return 95
            elif days_until <= 1:
                return 85
            elif days_until <= 3:
                return 70
            elif days_until <= 7:
                return 50
            else:
                return 20
        except:
            return 10
    
    def _calculate_importance(self, task):
        importance = task.get('importance', 5)
        return importance * 10
    
    def _calculate_effort(self, task):
        hours = task.get('estimated_hours', 1)
        if hours <= 1:
            return 90
        elif hours <= 3:
            return 70
        elif hours <= 8:
            return 40
        else:
            return 20
    
    def _calculate_dependencies(self, task, all_tasks):
        task_id = task.get('id')
        if not task_id:
            return 10
        
        dependent_count = 0
        for other_task in all_tasks:
            if task_id in other_task.get('dependencies', []):
                dependent_count += 1
        
        if dependent_count == 0:
            return 10
        elif dependent_count == 1:
            return 50
        elif dependent_count <= 3:
            return 75
        else:
            return 95
    
    def _get_explanation(self, urgency, importance, effort, dependencies):
        reasons = []
        
        if urgency >= 80:
            reasons.append("urgent deadline")
        elif urgency >= 50:
            reasons.append("approaching deadline")
        
        if importance >= 80:
            reasons.append("high importance")
        
        if effort >= 70:
            reasons.append("quick win")
        
        if dependencies >= 70:
            reasons.append("blocks other tasks")
        
        return f"Prioritized because: {', '.join(reasons)}" if reasons else "Moderate priority"

class FastestWinsStrategy(ScoringStrategy):
    def calculate_scores(self, tasks):
        scored_tasks = []
        for task in tasks:
            task_copy = task.copy()
            hours = task.get('estimated_hours', 1)
            score = max(10, 100 - (hours * 15))
            task_copy['priority_score'] = round(score, 2)
            task_copy['explanation'] = "Quick win strategy"
            scored_tasks.append(task_copy)
        return scored_tasks

class HighImpactStrategy(ScoringStrategy):
    def calculate_scores(self, tasks):
        scored_tasks = []
        for task in tasks:
            task_copy = task.copy()
            importance = task.get('importance', 5)
            score = importance * 10
            task_copy['priority_score'] = round(score, 2)
            task_copy['explanation'] = "High impact strategy"
            scored_tasks.append(task_copy)
        return scored_tasks

class DeadlineDrivenStrategy(ScoringStrategy):
    def calculate_scores(self, tasks):
        scored_tasks = []
        for task in tasks:
            task_copy = task.copy()
            score = self._calculate_urgency(task)
            task_copy['priority_score'] = round(score, 2)
            task_copy['explanation'] = "Deadline focused"
            scored_tasks.append(task_copy)
        return scored_tasks
    
    def _calculate_urgency(self, task):
        try:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            today = date.today()
            days_until = (due_date - today).days
            
            if days_until < 0:
                return 100
            elif days_until == 0:
                return 95
            elif days_until <= 1:
                return 90
            elif days_until <= 3:
                return 80
            elif days_until <= 7:
                return 60
            else:
                return 30
        except:
            return 10

def get_scoring_strategy(name):
    strategies = {
        'smart_balance': SmartBalanceStrategy,
        'fastest_wins': FastestWinsStrategy,
        'high_impact': HighImpactStrategy,
        'deadline_driven': DeadlineDrivenStrategy,
    }
    return strategies.get(name, SmartBalanceStrategy)()