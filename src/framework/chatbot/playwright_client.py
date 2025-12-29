import time
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright
from src.framework.core.interfaces import BaseChatbot

class PlaywrightChatbot(BaseChatbot):
    """Interacts with a Streamlit Chatbot using Playwright."""

    def __init__(self, target_url: str = "http://localhost:8503", headless: bool = True, selectors: Dict[str, str] = None):
        self.target_url = target_url
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None
        
        # Default Selectors (Streamlit)
        self.selectors = {
            "input": 'textarea[aria-label="Ask me anything..."]',
            "message": 'div[data-testid="stChatMessage"]',
            "response_container": 'div[data-testid="stMarkdownContainer"]'
        }
        if selectors:
            self.selectors.update(selectors)

    def _ensure_page(self):
        if not self._page:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
            self._page = self._browser.new_page()
            self._page.goto(self.target_url)
            # Wait for app to load
            try:
                self._page.wait_for_selector('textarea[aria-label="Ask me anything..."]', timeout=10000)
            except:
                # Fallback or retry if initial load is slow
                time.sleep(2)

    def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        self._ensure_page()
        page = self._page
        
        # 1. Fill Input
        input_selector = self.selectors["input"]
        try:
           page.wait_for_selector(input_selector, timeout=5000)
        except:
             # If specific fails and we are using default, try generic fallback
             if input_selector == 'textarea[aria-label="Ask me anything..."]':
                input_selector = 'textarea'
                page.wait_for_selector(input_selector, timeout=5000)
             else:
                 raise

        page.fill(input_selector, message)
        page.press(input_selector, "Enter")

        # 2. Wait for Response
        # Initial wait to let the UI update and user message to appear
        time.sleep(1)
        
        last_text = ""
        stable_count = 0
        
        for i in range(30): # 15 seconds max
            # Get all chat messages
            message_elements = page.query_selector_all(self.selectors["message"])
            if not message_elements:
                time.sleep(0.5)
                continue
                
            last_msg_el = message_elements[-1]
            
            # Extract content
            current_text = ""
            if self.selectors.get("response_container"):
                 container = last_msg_el.query_selector(self.selectors["response_container"])
                 if container:
                     current_text = container.inner_text()
            
            if not current_text:
                current_text = last_msg_el.inner_text() # Fallback

            # Debug print
            # print(f"DEBUG: Attempt {i}, Last Msg: '{current_text}'")

            # Heuristic: If text is empty or matches our prompt, we are probably still seeing the user message 
            # or an empty container.
            # RAG bot response should definitely not be the exact user prompt.
            if current_text.strip() == message.strip():
                # Still evaluating or seeing user message
                time.sleep(0.5)
                continue
            
            if not current_text.strip():
                 # Empty response
                time.sleep(0.5)
                last_text = ""
                continue

            # Check stability
            if current_text == last_text:
                stable_count += 1
            else:
                stable_count = 0
            
            last_text = current_text
            
            # If stable for 3 checks (1.5s), assume complete
            if stable_count >= 3:
                return current_text
            
            time.sleep(0.5)

        return last_text or "[TIMEOUT] Failed to scrape response."

    def close(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
