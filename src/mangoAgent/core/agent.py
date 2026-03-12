import json
from anthropic import Anthropic

class Agent:
    def __init__(
        self, 
        client: Anthropic, 
        model: str, 
        system_prompt: str, 
        tools: list, 
        handlers: dict,
        # Optional managers for hooks
        todo_mgr=None,
        context_mgr=None,
        bg_mgr=None,
        bus_mgr=None,
        logger=None,
        tui=None
    ):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.handlers = handlers
        
        self.todo_mgr = todo_mgr
        self.context_mgr = context_mgr
        self.bg_mgr = bg_mgr
        self.bus_mgr = bus_mgr
        self.logger = logger
        self.tui = tui
        
        # Metrics
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def run(self, messages: list):
        rounds_without_todo = 0
        
        while True:
            # === Pre-LLM Hooks ===
            
            # 1. Micro-compacting
            if self.context_mgr:
                self.context_mgr.microcompact(messages)
                if self.context_mgr.estimate_tokens(messages) > 100000:
                    print("\033[33m[auto-compact triggered]\033[0m")
                    messages[:] = self.context_mgr.auto_compact(messages)

            # 2. Drain background tasks
            if self.bg_mgr:
                notifs = self.bg_mgr.drain()
                if notifs:
                    txt = "\n".join(f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs)
                    messages.append({
                        "role": "user", 
                        "content": f"<background-results>\n{txt}\n</background-results>"
                    })
                    messages.append({
                        "role": "assistant", 
                        "content": "Noted background results."
                    })

            # 3. Check inbox
            if self.bus_mgr:
                inbox = self.bus_mgr.read_inbox("lead")
                if inbox:
                    messages.append({
                        "role": "user", 
                        "content": f"<inbox>{json.dumps(inbox, indent=2)}</inbox>"
                    })
                    messages.append({
                        "role": "assistant", 
                        "content": "Noted inbox messages."
                    })

            # === LLM Call ===
            if self.tui:
                self.tui.print_system_message("Thinking...")
            else:
                print("\033[35m[LLM] Calling model...\033[0m")
                
            if self.logger:
                self.logger.debug(f"Messages before LLM call: {json.dumps(messages, default=str)}")
                
            response = self.client.messages.create(
                model=self.model,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools,
                max_tokens=8000,
            )
            
            if hasattr(response, 'usage'):
                in_tokens = response.usage.input_tokens
                out_tokens = response.usage.output_tokens
                
                self.total_input_tokens += in_tokens
                self.total_output_tokens += out_tokens
                
                total_in = self.total_input_tokens
                total_out = self.total_output_tokens
                total_all = total_in + total_out
                
                # Assuming 128k context window
                context_limit = 128000 
                usage_percent = (in_tokens / context_limit) * 100
                
                if self.tui:
                    self.tui.print_usage(in_tokens, out_tokens, total_all, usage_percent)
                else:
                    print(f"\033[30;47m[Usage] Current: {in_tokens}+{out_tokens} | Total: {total_all} (In:{total_in} Out:{total_out}) | Ctx: {usage_percent:.1f}%\033[0m")
            
            if self.logger:
                self.logger.debug(f"LLM Response Content: {response.content}")
                
            messages.append({"role": "assistant", "content": response.content})
            
            # === Print LLM Response (Text Blocks) ===
            for block in response.content:
                if block.type == "text":
                    if self.tui:
                        self.tui.print_assistant_message(block.text)
                    else:
                        print(f"\033[34m[Assistant]:\033[0m {block.text}")

            # Check if there are any tool_use blocks
            has_tool_use = any(block.type == "tool_use" for block in response.content)
            
            if not has_tool_use:
                return

            # === Tool Execution ===
            results = []
            used_todo = False
            manual_compress = False
            
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "compress":
                        manual_compress = True
                        
                    handler = self.handlers.get(block.name)
                    
                    if self.tui:
                        self.tui.print_tool_call(block.name, block.input)
                    else:
                        print(f"\033[33m[Tool Call]: {block.name}\033[0m")
                        print(f"\033[33m[Input]: {json.dumps(block.input, indent=2, ensure_ascii=False)}\033[0m")
                    
                    try:
                        output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    except Exception as e:
                        output = f"Error: {e}"
                    
                    if self.tui:
                        self.tui.print_tool_result(str(output))
                    else:
                        print(f"\033[32m[Result]: {str(output)[:500]}\033[0m")
                        if len(str(output)) > 500:
                            print(f"\033[32m... ({len(str(output)) - 500} more chars)\033[0m")
                        
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(output),
                    })
                    
                    if block.name == "TodoWrite":
                        used_todo = True
            
            if not results:
                # Should not happen given has_tool_use check, but as a safeguard
                # to prevent empty user message which API might reject or handle poorly
                return
            
            # === Post-Tool Hooks ===
            
            # Todo Nag
            if self.todo_mgr:
                rounds_without_todo = 0 if used_todo else rounds_without_todo + 1
                if self.todo_mgr.has_open_items() and rounds_without_todo >= 3:
                    results.insert(0, {
                        "type": "text", 
                        "text": "<reminder>Update your todos.</reminder>"
                    })
            
            messages.append({"role": "user", "content": results})
            
            # Manual Compress Hook
            if manual_compress and self.context_mgr:
                print("\033[33m[manual compact]\033[0m")
                messages[:] = self.context_mgr.auto_compact(messages)
