class TaskPlanner:
    """A simple framework for breaking down goals into tasks."""
    
    def __init__(self):
        self.task_templates = {
            'research': ['Gather information', 'Review sources', 'Summarize findings'],
            'project': ['Define requirements', 'Plan approach', 'Execute', 'Review'],
            'learning': ['Identify topics', 'Study materials', 'Practice', 'Test knowledge'],
            'default': ['Analyze goal', 'Break into steps', 'Prioritize', 'Execute']
        }
    
    def plan(self, goal: str) -> list[str]:
        """
        Generate a list of tasks for a given goal.
        
        Args:
            goal: A string describing the goal
            
        Returns:
            A list of task strings
        """
        goal_lower = goal.lower()
        
        # Simple keyword matching to select template
        if any(word in goal_lower for word in ['research', 'investigate', 'study']):
            template = self.task_templates['research']
        elif any(word in goal_lower for word in ['build', 'create', 'develop', 'project']):
            template = self.task_templates['project']
        elif any(word in goal_lower for word in ['learn', 'understand', 'master']):
            template = self.task_templates['learning']
        else:
            template = self.task_templates['default']
        
        # Contextualize tasks with the goal
        return [f"{task}: {goal}" for task in template]
    
    def add_template(self, name: str, tasks: list[str]):
        """Add a custom task template."""
        self.task_templates[name] = tasks


# Example usage
if __name__ == "__main__":
    planner = TaskPlanner()
    
    # Test with different goals
    goals = [
        "Research market trends for AI startups",
        "Build a web scraper",
        "Learn Python decorators"
    ]
    
    for goal in goals:
        print(f"\nGoal: {goal}")
        tasks = planner.plan(goal)
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task}")
    
    # Add custom template
    planner.add_template('writing', ['Outline', 'Draft', 'Edit', 'Publish'])
    print(f"\n\nCustom template test:")
    print(planner.plan("Write a blog post"))
