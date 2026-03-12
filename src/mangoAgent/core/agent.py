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
        
        try:
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
                if self.logger:
                    self.logger.debug(f"Messages before LLM call: {json.dumps(messages, default=str)}")
                    
                full_content = []
                thinking_content = ""
                text_content = ""
                tool_calls = []
                
                # Track current tool being parsed if any
                current_tool_id = None
                current_tool_name = None
                current_tool_input = ""

                # Use stream for real-time output
                with self.client.messages.stream(
                    model=self.model,
                    system=self.system_prompt,
                    messages=messages,
                    tools=self.tools,
                    max_tokens=8000,
                ) as stream:
                    # Handle all events in one unified loop
                    thinking_active = False
                    
                    # Start thinking status if TUI is available
                    if self.tui:
                        self.tui.start_thinking()
                        thinking_active = True

                    for event in stream:
                        if event.type == "content_block_start":
                            if event.content_block.type == "thinking":
                                 pass # Thinking block started
                            elif event.content_block.type == "text":
                                # If we were thinking, stop before printing text
                                if thinking_active:
                                    if self.tui:
                                        self.tui.stop_thinking()
                                    thinking_active = False
                                
                                # Start responding panel
                                if self.tui:
                                    self.tui.start_responding()
                            elif event.content_block.type == "tool_use":
                                # Stop any active streaming panels
                                if thinking_active:
                                    if self.tui:
                                        self.tui.stop_thinking()
                                    thinking_active = False
                                
                                if self.tui:
                                    # If we were responding, stop it
                                    self.tui.stop_responding()
                                
                                current_tool_id = event.content_block.id
                                current_tool_name = event.content_block.name
                                current_tool_input = ""
                        
                        elif event.type == "content_block_delta":
                            if event.delta.type == "thinking_delta":
                                 chunk = event.delta.thinking
                                 thinking_content += chunk
                                 if self.tui:
                                     self.tui.print_thinking_chunk(chunk)
                                 else:
                                     print(f"\033[2m\033[3m{chunk}\033[0m", end="", flush=True)
                            elif event.delta.type == "text_delta":
                                text_chunk = event.delta.text
                                text_content += text_chunk
                                if self.tui:
                                    self.tui.print_stream_chunk(text_chunk)
                                else:
                                    print(text_chunk, end="", flush=True)
                            elif event.delta.type == "input_json_delta":
                                current_tool_input += event.delta.partial_json
                        
                        elif event.type == "content_block_stop":
                            if current_tool_name:
                                tool_calls.append({
                                    "type": "tool_use",
                                    "id": current_tool_id,
                                    "name": current_tool_name,
                                    "input": json.loads(current_tool_input) if current_tool_input else {}
                                })
                                current_tool_id = None
                                current_tool_name = None
                                current_tool_input = ""
                    
                    # Cleanup active status if still active
                    if thinking_active:
                        if self.tui:
                            self.tui.stop_thinking()
                        else:
                            print()
                    
                    # If we were responding, stop it
                    if self.tui:
                        self.tui.stop_responding()

                    # Newline after stream
                    if not self.tui:
                        print()

                    # Construct final content for history
                    if thinking_content:
                        full_content.append({"type": "thinking", "thinking": thinking_content})
                    if text_content:
                        full_content.append({"type": "text", "text": text_content})
                    for tc in tool_calls:
                        full_content.append(tc)

                    final_msg = stream.get_final_message()
                    in_tokens = final_msg.usage.input_tokens
                    out_tokens = final_msg.usage.output_tokens
                    
                    self.total_input_tokens += in_tokens
                    self.total_output_tokens += out_tokens
                    total_all = self.total_input_tokens + self.total_output_tokens
                    usage_percent = (in_tokens / 128000) * 100
                    
                    if self.tui:
                        # Newline after stream
                        print()
                        self.tui.print_usage(in_tokens, out_tokens, total_all, usage_percent)
                    else:
                        print(f"\033[30;47m[Usage] Current: {in_tokens}+{out_tokens} | Total: {total_all} | Ctx: {usage_percent:.1f}%\033[0m")

                messages.append({"role": "assistant", "content": full_content})
                
                # Check if there are any tool_use blocks
                has_tool_use = len(tool_calls) > 0
                
                if not has_tool_use:
                    return

                # === Tool Execution ===
                results = []
                used_todo = False
                manual_compress = False
                
                for block in tool_calls:
                    if block["name"] == "compress":
                        manual_compress = True
                        
                    handler = self.handlers.get(block["name"])
                        
                    if self.tui:
                        self.tui.print_tool_call(block["name"], block["input"])
                    else:
                        print(f"\033[33m[Tool Call]: {block['name']}\033[0m")
                        print(f"\033[33m[Input]: {json.dumps(block['input'], indent=2, ensure_ascii=False)}\033[0m")
                    
                    try:
                        output = handler(**block["input"]) if handler else f"Unknown tool: {block['name']}"
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
                        "tool_use_id": block["id"],
                        "content": str(output),
                    })
                    
                    if block["name"] == "TodoWrite":
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
        except KeyboardInterrupt:
            # Cleanup TUI if needed
            if self.tui:
                try:
                    self.tui.stop_thinking()
                except: pass
                try:
                    self.tui.stop_responding()
                except: pass
                self.tui.print_system_message("Current task loop interrupted by user.")
            else:
                print("\n\033[33m[Interrupted] Task loop stopped by user.\033[0m")
            return
