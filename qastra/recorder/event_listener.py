"""
Event Listener - Captures browser events for AI test recording.
"""

import json
import time
from typing import Dict, Any, List, Optional
from playwright.sync_api import Page


class EventListener:
    """Captures user interactions in the browser for test recording."""
    
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.page_url = None
    
    def inject_listener(self, page: Page, actions_list: List[Dict[str, Any]]):
        """
        Inject JavaScript event listener into the page to capture user actions.
        
        Args:
            page: Playwright page object
            actions_list: List to store captured actions
        """
        self.actions = actions_list
        self.start_time = time.time()
        self.page_url = page.url
        
        # Expose a function to Python that JavaScript can call
        page.expose_function("recordAction", self._record_action)
        
        # Inject comprehensive event listener
        listener_script = """
        (() => {
            console.log('Qastra Recorder: Event listener injected');
            
            // Helper function to get element description
            function getElementDescription(element) {
                const tagName = element.tagName.toLowerCase();
                const text = element.innerText?.trim() || '';
                const id = element.id || '';
                const className = element.className || '';
                const name = element.name || '';
                const placeholder = element.placeholder || '';
                const type = element.type || '';
                const value = element.value || '';
                const href = element.href || '';
                const title = element.title || '';
                
                return {
                    tagName,
                    text,
                    id,
                    className,
                    name,
                    placeholder,
                    type,
                    value,
                    href,
                    title
                };
            }
            
            // Helper function to generate intent from element
            function generateIntent(element, actionType) {
                const desc = getElementDescription(element);
                let intent = '';
                
                if (actionType === 'click') {
                    // For clicks, prioritize text content
                    if (desc.text) {
                        intent = desc.text.toLowerCase();
                    } else if (desc.title) {
                        intent = desc.title.toLowerCase();
                    } else if (desc.id) {
                        intent = desc.id.toLowerCase();
                    } else if (desc.className) {
                        intent = desc.className.split(' ')[0].toLowerCase();
                    } else if (desc.tagName === 'a' && desc.href) {
                        intent = 'link';
                    } else {
                        intent = desc.tagName;
                    }
                } else if (actionType === 'fill') {
                    // For inputs, prioritize field name
                    if (desc.name) {
                        intent = desc.name.toLowerCase();
                    } else if (desc.placeholder) {
                        intent = desc.placeholder.toLowerCase();
                    } else if (desc.id) {
                        intent = desc.id.toLowerCase();
                    } else if (desc.type === 'email') {
                        intent = 'email';
                    } else if (desc.type === 'password') {
                        intent = 'password';
                    } else if (desc.type === 'tel') {
                        intent = 'phone';
                    } else if (desc.type === 'search') {
                        intent = 'search';
                    } else {
                        intent = 'input';
                    }
                }
                
                return intent;
            }
            
            // Click event listener
            document.addEventListener('click', (event) => {
                const element = event.target;
                const desc = getElementDescription(element);
                const intent = generateIntent(element, 'click');
                
                // Only record meaningful clicks
                if (desc.tagName === 'button' || 
                    desc.tagName === 'a' || 
                    desc.tagName === 'input' && (desc.type === 'submit' || desc.type === 'button') ||
                    desc.role === 'button' ||
                    desc.onclick ||
                    desc.text) {
                    
                    window.recordAction(JSON.stringify({
                        type: 'click',
                        intent: intent,
                        element: desc,
                        timestamp: Date.now(),
                        url: window.location.href
                    }));
                }
            }, true);
            
            // Input event listener
            document.addEventListener('input', (event) => {
                const element = event.target;
                const desc = getElementDescription(element);
                const intent = generateIntent(element, 'fill');
                
                // Only record meaningful inputs
                if (desc.tagName === 'input' || 
                    desc.tagName === 'textarea') {
                    
                    window.recordAction(JSON.stringify({
                        type: 'fill',
                        intent: intent,
                        value: desc.value,
                        element: desc,
                        timestamp: Date.now(),
                        url: window.location.href
                    }));
                }
            }, true);
            
            // Change event listener for selects
            document.addEventListener('change', (event) => {
                const element = event.target;
                const desc = getElementDescription(element);
                
                if (desc.tagName === 'select') {
                    const intent = desc.name || desc.id || 'select';
                    const selectedOption = element.options[element.selectedIndex]?.text || '';
                    
                    window.recordAction(JSON.stringify({
                        type: 'select',
                        intent: intent.toLowerCase(),
                        value: selectedOption,
                        element: desc,
                        timestamp: Date.now(),
                        url: window.location.href
                    }));
                }
            }, true);
            
            // Navigation event listener
            let lastUrl = window.location.href;
            window.addEventListener('popstate', () => {
                const currentUrl = window.location.href;
                if (currentUrl !== lastUrl) {
                    window.recordAction(JSON.stringify({
                        type: 'navigate',
                        url: currentUrl,
                        timestamp: Date.now()
                    }));
                    lastUrl = currentUrl;
                }
            });
            
            // Form submit event listener
            document.addEventListener('submit', (event) => {
                const element = event.target;
                const desc = getElementDescription(element);
                
                window.recordAction(JSON.stringify({
                    type: 'submit',
                    element: desc,
                    timestamp: Date.now(),
                    url: window.location.href
                }));
            });
            
            // Scroll event listener (throttled)
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    window.recordAction(JSON.stringify({
                        type: 'scroll',
                        scrollY: window.scrollY,
                        scrollX: window.scrollX,
                        timestamp: Date.now(),
                        url: window.location.href
                    }));
                }, 500);
            });
            
            console.log('Qastra Recorder: Event listeners active');
        })();
        """
        
        try:
            page.evaluate(listener_script)
            print("✅ Event listener injected successfully")
        except Exception as e:
            print(f"❌ Failed to inject event listener: {e}")
            raise
    
    def _record_action(self, action_json: str):
        """
        Callback function called from JavaScript when an action occurs.
        
        Args:
            action_json: JSON string containing action data
        """
        try:
            action = json.loads(action_json)
            
            # Add relative timestamp
            if self.start_time:
                action['relative_time'] = action['timestamp'] - (self.start_time * 1000)
            
            # Add sequence number
            action['sequence'] = len(self.actions) + 1
            
            self.actions.append(action)
            
            # Log the action for debugging
            action_type = action['type']
            intent = action.get('intent', '')
            
            if action_type == 'click':
                print(f"🖱️  Click recorded: {intent}")
            elif action_type == 'fill':
                value = action.get('value', '')
                print(f"⌨️  Fill recorded: {intent} = '{value}'")
            elif action_type == 'select':
                value = action.get('value', '')
                print(f"📋 Select recorded: {intent} = '{value}'")
            elif action_type == 'navigate':
                url = action.get('url', '')
                print(f"🌐 Navigate recorded: {url}")
            elif action_type == 'submit':
                print(f"📤 Submit recorded")
            elif action_type == 'scroll':
                print(f"📜 Scroll recorded")
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse action JSON: {e}")
        except Exception as e:
            print(f"❌ Error recording action: {e}")
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get all recorded actions."""
        return self.actions.copy()
    
    def clear_actions(self):
        """Clear all recorded actions."""
        self.actions = []
        self.start_time = time.time()
    
    def get_recording_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the recording session.
        
        Returns:
            Summary dictionary
        """
        if not self.actions:
            return {
                'total_actions': 0,
                'duration': 0,
                'action_types': {},
                'intents': [],
                'start_url': self.page_url
            }
        
        # Count action types
        action_types = {}
        intents = []
        
        for action in self.actions:
            action_type = action['type']
            action_types[action_type] = action_types.get(action_type, 0) + 1
            
            if 'intent' in action:
                intents.append(action['intent'])
        
        # Calculate duration
        duration = 0
        if len(self.actions) > 1:
            first_action = self.actions[0]
            last_action = self.actions[-1]
            duration = (last_action['timestamp'] - first_action['timestamp']) / 1000
        
        return {
            'total_actions': len(self.actions),
            'duration': duration,
            'action_types': action_types,
            'intents': list(set(intents)),
            'start_url': self.page_url,
            'unique_intents': len(set(intents))
        }
    
    def filter_actions(self, action_types: Optional[List[str]] = None, 
                      intents: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Filter recorded actions by type and/or intent.
        
        Args:
            action_types: List of action types to include
            intents: List of intents to include
            
        Returns:
            Filtered list of actions
        """
        filtered = self.actions
        
        if action_types:
            filtered = [a for a in filtered if a['type'] in action_types]
        
        if intents:
            filtered = [a for a in filtered if a.get('intent') in intents]
        
        return filtered
    
    def get_action_flow(self) -> List[str]:
        """
        Get a human-readable flow of actions.
        
        Returns:
            List of action descriptions
        """
        flow = []
        
        for action in self.actions:
            action_type = action['type']
            intent = action.get('intent', '')
            
            if action_type == 'click':
                flow.append(f"Click {intent}")
            elif action_type == 'fill':
                value = action.get('value', '')
                flow.append(f"Fill {intent} with '{value}'")
            elif action_type == 'select':
                value = action.get('value', '')
                flow.append(f"Select '{value}' in {intent}")
            elif action_type == 'navigate':
                url = action.get('url', '')
                flow.append(f"Navigate to {url}")
            elif action_type == 'submit':
                flow.append("Submit form")
            elif action_type == 'scroll':
                flow.append("Scroll page")
        
        return flow


# Convenience function
def inject_listener(page: Page, actions_list: List[Dict[str, Any]]) -> EventListener:
    """Quick function to inject event listener."""
    listener = EventListener()
    listener.inject_listener(page, actions_list)
    return listener
