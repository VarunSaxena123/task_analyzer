from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScoringEngine, get_scoring_strategy

class ScoringAlgorithmTests(TestCase):
    
    def setUp(self):
        self.scorer = TaskScoringEngine()
        self.today = date.today()
    
    def test_urgency_scoring_past_due(self):
        """Test urgency scoring for past due dates"""
        overdue_task = {
            'title': 'Overdue Task',
            'due_date': (self.today - timedelta(days=5)).isoformat(),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': []
        }
        result = self.scorer.calculate_comprehensive_score(overdue_task)
        self.assertGreaterEqual(result['score'], 80)  # Past due should have high score
        self.assertIn('high urgency', result['explanation'].lower())
    
    def test_urgency_scoring_due_today(self):
        """Test urgency scoring for tasks due today"""
        due_today_task = {
            'title': 'Due Today Task',
            'due_date': self.today.isoformat(),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        result = self.scorer.calculate_comprehensive_score(due_today_task)
        self.assertGreaterEqual(result['component_scores']['urgency'], 90)
    
    def test_importance_scoring_high(self):
        """Test importance scoring for high importance tasks"""
        high_importance_task = {
            'title': 'Important Task',
            'due_date': (self.today + timedelta(days=7)).isoformat(),
            'estimated_hours': 3,
            'importance': 9,
            'dependencies': []
        }
        result = self.scorer.calculate_comprehensive_score(high_importance_task)
        self.assertEqual(result['component_scores']['importance'], 90)
        self.assertIn('high importance', result['explanation'].lower())
    
    def test_quick_win_scoring(self):
        """Test quick win bonus for low-effort tasks"""
        quick_task = {
            'title': 'Quick Task',
            'due_date': (self.today + timedelta(days=7)).isoformat(),
            'estimated_hours': 1,
            'importance': 5,
            'dependencies': []
        }
        result = self.scorer.calculate_comprehensive_score(quick_task)
        self.assertEqual(result['component_scores']['effort'], 90)
        self.assertIn('quick win', result['explanation'].lower())
    
    def test_dependency_scoring(self):
        """Test dependency-based scoring"""
        blocking_task = {
            'title': 'Blocking Task',
            'due_date': (self.today + timedelta(days=3)).isoformat(),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': [],
            'id': 1
        }
        dependent_task = {
            'title': 'Dependent Task', 
            'due_date': (self.today + timedelta(days=3)).isoformat(),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': [1]
        }
        
        tasks = [blocking_task, dependent_task]
        result = self.scorer.calculate_comprehensive_score(blocking_task, tasks)
        self.assertGreaterEqual(result['component_scores']['dependencies'], 70)
        self.assertIn('blocks other tasks', result['explanation'].lower())
    
    def test_missing_data_handling(self):
        """Test handling of missing task data"""
        incomplete_task = {
            'title': 'Incomplete Task'
            # Missing other fields
        }
        result = self.scorer.calculate_comprehensive_score(incomplete_task)
        self.assertIsInstance(result['score'], float)
        self.assertIsInstance(result['explanation'], str)
        # Should use defaults without crashing
        self.assertIn('due_date', str(result))
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        task_a = {
            'title': 'Task A',
            'due_date': self.today.isoformat(),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': [2],
            'id': 1
        }
        task_b = {
            'title': 'Task B',
            'due_date': self.today.isoformat(),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': [1],
            'id': 2
        }
        
        tasks = [task_a, task_b]
        cycles = self.scorer.detect_circular_dependencies(tasks)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 2)
    
    def test_different_strategies(self):
        """Test different scoring strategies"""
        task = {
            'title': 'Test Task',
            'due_date': (self.today + timedelta(days=1)).isoformat(),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        # Test different strategies
        smart_balance = get_scoring_strategy('smart_balance')
        fastest_wins = get_scoring_strategy('fastest_wins')
        high_impact = get_scoring_strategy('high_impact')
        deadline_driven = get_scoring_strategy('deadline_driven')
        
        smart_result = smart_balance.calculate_scores([task])[0]
        fast_result = fastest_wins.calculate_scores([task])[0]
        high_result = high_impact.calculate_scores([task])[0]
        deadline_result = deadline_driven.calculate_scores([task])[0]
        
        # Each strategy should produce different scoring patterns
        self.assertNotEqual(smart_result.get('priority_score', smart_result.get('score')), 
                           fast_result.get('priority_score', fast_result.get('score')))
        
        # High impact should reflect importance directly
        self.assertIn('high impact', high_result['explanation'].lower())
        
        # Fastest wins should emphasize low effort
        self.assertIn('quick win', fast_result['explanation'].lower())