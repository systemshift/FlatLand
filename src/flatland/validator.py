"""
Schema validation module for FlatLand environments.
"""

from typing import Dict, Any, Tuple, List, Optional
import jsonschema

from .schemas import ENVIRONMENT_SCHEMA
from .models import Rule


class ValidationError(Exception):
    """Exception raised for schema validation errors."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []


class SchemaValidator:
    """Validates environment definitions against JSON schema."""
    
    @staticmethod
    def validate_environment(env_data: Dict[str, Any]) -> Tuple[bool, Optional[List[str]]]:
        """
        Validate an environment definition against the schema.
        
        Args:
            env_data: The environment data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            jsonschema.validate(instance=env_data, schema=ENVIRONMENT_SCHEMA)
            return True, None
        except jsonschema.exceptions.ValidationError as e:
            # Extract the validation error path and message
            path = ".".join(str(p) for p in e.path) if e.path else "root"
            error_msg = f"Validation error at {path}: {e.message}"
            return False, [error_msg]
    
    @staticmethod
    def validate_rule(rule: Rule) -> Tuple[bool, Optional[List[str]]]:
        """
        Validate a rule against the schema.
        
        Args:
            rule: The rule to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate rule type
        if rule.type not in {"conditional", "transformation", "constraint"}:
            errors.append(f"Invalid rule type: {rule.type}")
        
        # Validate condition
        if "condition" not in rule.when:
            errors.append("Rule condition missing 'condition' field")
        elif not isinstance(rule.when["condition"], str):
            errors.append("Rule condition must be a string")
        
        # Validate entities if present
        if "entities" in rule.when and not isinstance(rule.when["entities"], list):
            errors.append("Rule entities must be a list")
        
        # Validate action
        if "action" not in rule.then:
            errors.append("Rule action missing 'action' field")
        elif rule.then["action"] not in {"transform", "move", "validate"}:
            errors.append(f"Invalid action type: {rule.then['action']}")
        
        # Validate parameters
        if "parameters" not in rule.then:
            errors.append("Rule action missing 'parameters' field")
        elif not isinstance(rule.then["parameters"], dict):
            errors.append("Rule parameters must be a dictionary")
        
        return len(errors) == 0, errors if errors else None


class RuleConflictDetector:
    """Detects conflicts between rules."""
    
    @staticmethod
    def detect_conflicts(rules: List[Rule]) -> List[Tuple[Rule, Rule, str]]:
        """
        Detect potential conflicts between rules.
        
        Args:
            rules: List of rules to check
            
        Returns:
            List of (rule1, rule2, conflict_reason) tuples
        """
        conflicts = []
        
        # Build a map of entity types affected by each rule
        rule_entities = {}
        for rule in rules:
            entities = rule.when.get("entities", [])
            rule_entities[rule.name] = set(entities)
        
        # Check for rules that affect the same entities but have different priorities
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                # Skip rules with the same priority
                if rule1.priority == rule2.priority:
                    continue
                
                # Check if rules affect the same entities
                entities1 = rule_entities[rule1.name]
                entities2 = rule_entities[rule2.name]
                
                if entities1 and entities2 and entities1.intersection(entities2):
                    # Rules affect the same entities but have different priorities
                    conflicts.append((
                        rule1, 
                        rule2, 
                        f"Rules affect the same entities ({entities1.intersection(entities2)}) but have different priorities"
                    ))
        
        return conflicts


class DependencyResolver:
    """Resolves dependencies between rules."""
    
    @staticmethod
    def build_dependency_graph(rules: List[Rule]) -> Dict[str, List[str]]:
        """
        Build a directed graph of rule dependencies.
        
        Args:
            rules: List of rules to analyze
            
        Returns:
            Dictionary mapping rule names to lists of dependent rule names
        """
        graph = {}
        rule_map = {rule.name: rule for rule in rules}
        
        for rule in rules:
            dependencies = []
            
            # Extract entity types affected by this rule
            affected_entities = rule.when.get("entities", [])
            
            # Find rules that might affect these entities
            for other_rule in rules:
                if other_rule.name == rule.name:
                    continue
                
                # Check if other rule affects entities that this rule depends on
                other_entities = other_rule.when.get("entities", [])
                if any(entity in affected_entities for entity in other_entities):
                    dependencies.append(other_rule.name)
            
            graph[rule.name] = dependencies
        
        return graph
    
    @staticmethod
    def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect cycles in the dependency graph.
        
        Args:
            graph: Dependency graph
            
        Returns:
            List of cycles, where each cycle is a list of rule names
        """
        cycles = []
        visited = set()
        path = []
        
        def dfs(node):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            
            path.pop()
        
        for node in graph:
            dfs(node)
        
        return cycles
