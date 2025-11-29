import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .scoring import get_scoring_strategy

# Simple in-memory storage
TASKS_STORAGE = []

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    global TASKS_STORAGE
    
    print("=== ANALYZE TASKS ENDPOINT CALLED ===")
    print(f"Method: {request.method}")
    
    try:
        # Parse JSON data
        body = request.body.decode('utf-8')
        print(f"Raw body: {body}")
        
        if not body:
            return JsonResponse({'error': 'Empty request body'}, status=400)
        
        data = json.loads(body)
        print(f"Received data: {data}")
        
        # Extract tasks
        if isinstance(data, list):
            tasks = data
        elif isinstance(data, dict) and 'tasks' in data:
            tasks = data['tasks']
        else:
            tasks = data.get('tasks', [])
        
        if not isinstance(tasks, list):
            return JsonResponse({'error': 'Tasks should be a list'}, status=400)
        
        print(f"Processing {len(tasks)} tasks")
        
        # Validate and prepare tasks
        validated_tasks = []
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
                
            validated_task = {
                'id': task.get('id', i + 1),
                'title': task.get('title', f'Task {i + 1}').strip(),
                'due_date': task.get('due_date', '2024-12-01'),
                'estimated_hours': int(task.get('estimated_hours', 1)),
                'importance': int(task.get('importance', 5)),
                'dependencies': task.get('dependencies', [])
            }
            validated_tasks.append(validated_task)
        
        # Store tasks
        TASKS_STORAGE = validated_tasks.copy()
        print(f"Stored {len(TASKS_STORAGE)} tasks")
        
        # Get strategy
        strategy_name = 'smart_balance'
        if isinstance(data, dict):
            strategy_name = data.get('strategy', 'smart_balance')
        
        # Calculate scores
        strategy = get_scoring_strategy(strategy_name)
        scored_tasks = strategy.calculate_scores(validated_tasks)
        sorted_tasks = sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)
        
        response_data = {
            'tasks': sorted_tasks,
            'strategy_used': strategy_name,
            'total_tasks': len(sorted_tasks),
            'message': 'Analysis successful'
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def suggest_tasks(request):
    global TASKS_STORAGE
    
    print("=== SUGGEST TASKS ENDPOINT CALLED ===")
    print(f"Method: {request.method}")
    print(f"Stored tasks: {len(TASKS_STORAGE)}")
    
    if not TASKS_STORAGE:
        return JsonResponse({
            'error': 'No tasks available for suggestions',
            'message': 'Please analyze tasks first by sending a POST request to /api/tasks/analyze/'
        }, status=400)
    
    try:
        # Calculate suggestions
        strategy = get_scoring_strategy('smart_balance')
        scored_tasks = strategy.calculate_scores(TASKS_STORAGE)
        top_tasks = sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)[:3]
        
        # Format suggestions
        suggestions = []
        for i, task in enumerate(top_tasks, 1):
            suggestions.append({
                'rank': i,
                'title': task['title'],
                'priority_score': round(task['priority_score'], 2),
                'explanation': task.get('explanation', 'High priority task'),
                'due_date': task['due_date'],
                'estimated_hours': task['estimated_hours'],
                'importance': task['importance'],
                'reason': f"Priority score: {task['priority_score']}"
            })
        
        response_data = {
            'suggestions': suggestions,
            'total_tasks_analyzed': len(TASKS_STORAGE)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return JsonResponse({'error': f'Suggestion generation failed: {str(e)}'}, status=500)