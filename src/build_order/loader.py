"""
JSON parser for build orders
"""
import json
from pathlib import Path
from typing import List, Optional
from .build_order import BuildOrder, BuildOrderStep, ActionType, ResourceType


class BuildOrderLoader:
    """Loads build orders from JSON files"""
    
    @staticmethod
    def load_from_file(filepath: str) -> BuildOrder:
        """Load a build order from a JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return BuildOrderLoader.parse_json(data)
    
    @staticmethod
    def parse_json(data: dict) -> BuildOrder:
        """Parse JSON data into BuildOrder object"""
        steps = []
        
        for step_data in data.get('steps', []):
            # Parse action type
            action_str = step_data.get('action', '').lower()
            action = ActionType(action_str)
            
            # Parse resource if present
            resource = None
            resource_str = step_data.get('resource')
            if resource_str:
                resource = ResourceType(resource_str.lower())
            
            step = BuildOrderStep(
                villager_count=step_data.get('villager_count', 0),
                action=action,
                description=step_data.get('description', ''),
                resource=resource,
                building=step_data.get('building'),
                unit=step_data.get('unit'),
                tech=step_data.get('tech'),
                count=step_data.get('count', 1),
                notes=step_data.get('notes'),
                important=step_data.get('important', False)
            )
            steps.append(step)
        
        build_order = BuildOrder(
            name=data.get('name', 'Unnamed Build Order'),
            description=data.get('description', ''),
            civilization=data.get('civilization', 'any'),
            steps=steps,
            author=data.get('author'),
            target_age=data.get('target_age', 'Feudal'),
            max_villagers=data.get('max_villagers', 25),
            strategy=data.get('strategy')
        )
        
        return build_order
    
    @staticmethod
    def get_available_build_orders(build_orders_dir: str) -> List[str]:
        """Get list of available build order files"""
        path = Path(build_orders_dir)
        if not path.exists():
            return []
        
        return [str(f) for f in path.glob('*.json')]
    
    @staticmethod
    def save_to_file(build_order: BuildOrder, filepath: str):
        """Save build order to JSON file"""
        data = {
            'name': build_order.name,
            'description': build_order.description,
            'civilization': build_order.civilization,
            'author': build_order.author,
            'target_age': build_order.target_age,
            'max_villagers': build_order.max_villagers,
            'strategy': build_order.strategy,
            'steps': []
        }
        
        for step in build_order.steps:
            step_data = {
                'villager_count': step.villager_count,
                'action': step.action.value,
                'description': step.description,
                'count': step.count
            }
            
            if step.resource:
                step_data['resource'] = step.resource.value
            if step.building:
                step_data['building'] = step.building
            if step.unit:
                step_data['unit'] = step.unit
            if step.tech:
                step_data['tech'] = step.tech
            if step.notes:
                step_data['notes'] = step.notes
            if step.important:
                step_data['important'] = True
            
            data['steps'].append(step_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
