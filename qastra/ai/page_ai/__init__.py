"""
AI Page Understanding - Intelligent page analysis and action execution.

This module provides AI-powered page understanding capabilities that allow
Qastra to understand web pages and perform intelligent actions based on
natural language instructions.
"""

from .page_analyzer import PageAnalyzer, Product, Form, NavigationItem, extract_products, analyze_page
from .action_planner import ActionPlanner, ActionPlan, Goal, ActionType, GoalType, parse_instruction
from .decision_engine import DecisionEngine, Decision, execute_goal, find_cheapest_product

__all__ = [
    # Page Analyzer
    'PageAnalyzer',
    'Product',
    'Form', 
    'NavigationItem',
    'extract_products',
    'analyze_page',
    
    # Action Planner
    'ActionPlanner',
    'ActionPlan',
    'Goal',
    'ActionType',
    'GoalType',
    'parse_instruction',
    
    # Decision Engine
    'DecisionEngine',
    'Decision',
    'execute_goal',
    'find_cheapest_product'
]
