from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
import json


@dataclass
class MemoryEntry:
    """A single memory entry representing a task execution."""
    timestamp: str
    task: str
    status: str  
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return asdict(self)


class Memory:
    """Simple memory system for storing and querying task execution history."""
    
    def __init__(self):
        self.entries: list[MemoryEntry] = []
    
    def record(self, task: str, status: str, result: Any = None, 
               error: str = None, **metadata) -> MemoryEntry:
        """
        Record a task execution.
        
        Args:
            task: Description of the task
            status: Execution status ('started', 'completed', 'failed')
            result: Optional result data
            error: Optional error message
            **metadata: Additional key-value pairs to store
            
        Returns:
            The created MemoryEntry
        """
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            task=task,
            status=status,
            result=result,
            error=error,
            metadata=metadata
        )
        self.entries.append(entry)
        return entry
    
    def get_all(self) -> list[MemoryEntry]:
        """Retrieve all memory entries."""
        return self.entries.copy()
    
    def filter_by_status(self, status: str) -> list[MemoryEntry]:
        """Get entries with a specific status."""
        return [e for e in self.entries if e.status == status]
    
    def filter_by_task(self, task_pattern: str) -> list[MemoryEntry]:
        """Get entries where task contains the pattern (case-insensitive)."""
        pattern = task_pattern.lower()
        return [e for e in self.entries if pattern in e.task.lower()]
    
    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """Get the n most recent entries."""
        return self.entries[-n:]
    
    def get_summary(self) -> dict:
        """Get a summary of execution statistics."""
        total = len(self.entries)
        if total == 0:
            return {'total': 0, 'completed': 0, 'failed': 0, 'started': 0}
        
        return {
            'total': total,
            'completed': sum(1 for e in self.entries if e.status == 'completed'),
            'failed': sum(1 for e in self.entries if e.status == 'failed'),
            'started': sum(1 for e in self.entries if e.status == 'started')
        }
    
    def clear(self):
        """Clear all memory entries."""
        self.entries.clear()
    
    def export_json(self, filepath: str):
        """Export memory to JSON file."""
        with open(filepath, 'w') as f:
            json.dump([e.to_dict() for e in self.entries], f, indent=2)
    
    def import_json(self, filepath: str):
        """Import memory from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.entries = [MemoryEntry(**entry) for entry in data]


if __name__ == "__main__":
    memory = Memory()
    
    # Record some task executions
    memory.record("Research AI trends", "started", agent="researcher")
    memory.record("Research AI trends", "completed", 
                  result={"sources": 5, "insights": 12}, agent="researcher")
    
    memory.record("Build web scraper", "started", agent="developer")
    memory.record("Build web scraper", "failed", 
                  error="Connection timeout", agent="developer")
    
    memory.record("Analyze data", "completed", 
                  result={"rows_processed": 1000}, agent="analyst")
    
    
    print("=== All Entries ===")
    for entry in memory.get_all():
        print(f"{entry.timestamp}: {entry.task} - {entry.status}")
    
    print("\n=== Summary ===")
    print(memory.get_summary())
    
    print("\n=== Failed Tasks ===")
    for entry in memory.filter_by_status("failed"):
        print(f"{entry.task}: {entry.error}")
    
    print("\n=== Recent 3 ===")
    for entry in memory.get_recent(3):
        print(f"{entry.task} - {entry.status}")
    
    
    memory.export_json("memory_audit.json")
    print("\n✓ Exported to memory_audit.json")
