# Smart Task Analyzer

An intelligent task management system that prioritizes tasks based on multiple factors using sophisticated scoring algorithms. This application helps users identify which tasks to work on first by balancing urgency, importance, effort, and dependencies.

## 🎯 Project Overview

This project demonstrates advanced problem-solving skills, clean code architecture, and algorithmic thinking. The system intelligently scores and prioritizes tasks using multiple configurable strategies, providing users with actionable insights for better task management.

## 🚀 Features

### Core Functionality
- **Intelligent Priority Scoring**: Advanced algorithm balancing four key factors
- **Multiple Sorting Strategies**: Four distinct prioritization approaches
- **Real-time Analysis**: Instant task prioritization with detailed explanations
- **Smart Suggestions**: AI-driven top 3 task recommendations
- **Circular Dependency Detection**: Automatic detection of dependency cycles
- **Responsive Design**: Seamless experience across all devices

### Scoring Strategies
1. **Smart Balance** 🧠 - Balanced approach considering all factors
2. **Fastest Wins** ⚡ - Prioritizes low-effort "quick win" tasks
3. **High Impact** 🎯 - Focuses on high-importance tasks
4. **Deadline Driven** 📅 - Emphasizes urgent deadlines

## 🛠️ Technical Stack

- **Backend**: Python 3.8+, Django 4.2.7
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: SQLite (Django default)
- **Architecture**: RESTful API with monolithic frontend

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## ⚡ Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd task-analyzer/backend

# Install dependencies
pip install django==4.2.7

# Setup database
python manage.py migrate

# Run the Aplication
python manage.py runserver 8000

# Access the Aplication
http://localhost:8000

Algorithm Explanation
Core Scoring Mechanism
The priority scoring algorithm employs a sophisticated weighted approach that balances four critical factors to determine task priority:

Urgency Scoring (40% weight): Tasks are evaluated based on their due dates using a tiered system. Overdue tasks receive the maximum score of 100, emphasizing their critical nature. Tasks due today score 95, while those due tomorrow score 85. The scoring gradually decreases for less urgent tasks, with deadlines beyond two weeks receiving only 10 points. This ensures time-sensitive tasks receive appropriate attention while maintaining balance with other factors.

Importance Evaluation (30% weight): User-provided importance ratings (1-10 scale) are linearly scaled to a 10-100 point system. This direct mapping preserves user intent while integrating seamlessly with the overall scoring framework. High-importance tasks (8-10) receive 80-100 points, medium importance (4-7) get 40-70 points, and low importance tasks (1-3) receive 10-30 points.

Effort Assessment (20% weight): The system rewards "quick wins" by assigning higher scores to lower-effort tasks. Tasks estimated at 1 hour or less receive 90 points, while those taking 3 hours score 70 points. The scoring decreases progressively, with tasks requiring 8+ hours receiving only 20 points. This encourages productivity by prioritizing achievable tasks.

Dependency Analysis (10% weight): Tasks that block other work receive priority boosts. Independent tasks start with 10 points, while tasks blocking one other task score 50 points. Those blocking 2-3 tasks earn 75 points, and tasks with extensive dependencies (4+) receive 95 points. This ensures critical path items are addressed promptly.

The algorithm intelligently combines these factors using the weighted sum: Total Score = (Urgency × 0.4) + (Importance × 0.3) + (Effort × 0.2) + (Dependencies × 0.1). This balanced approach prevents any single factor from dominating while ensuring comprehensive task evaluation.

🚀 Future Improvements

Given additional time, I would implement:

Immediate Enhancements (1-2 hours)

Database Integration: Replace in-memory storage with proper database models

Unit Test Suite: Comprehensive testing for scoring algorithms and API endpoints

Input Validation: Enhanced client-side and server-side validation


Advanced Features (3-4 hours)

User Authentication: Individual task lists and preferences

Task Categories: Organize tasks by project or context

Export Functionality: CSV/PDF reports of prioritized tasks

Mobile App: React Native companion application


Enterprise Features (5+ hours)

Team Collaboration: Shared task lists and assignments

Analytics Dashboard: Productivity metrics and trends

Integration APIs: Connect with calendar and project management tools

Machine Learning: Adaptive scoring based on user behavior
