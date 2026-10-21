/**
 * CLI event adapters for the standalone Aria avatar.
 * These only translate already-received events. They never launch a CLI,
 * connect to a provider, execute tools, or send credentials.
 */

function eventObject(raw) {
  if (typeof raw === "string") {
    if (!raw.trim()) return null;
    raw = JSON.parse(raw);
  }
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  return raw;
}

function bridge(avatar) {
  if (!avatar || typeof avatar.handle !== "function") {
    throw new TypeError("An avatar with handle(event) is required.");
  }
  return (events, type, text) => {
    const event = text === undefined ? { type } : { type, text };
    events.push(event);
    avatar.handle(event);
  };
}

/**
 * Translate claude stream-json JSONL or matching TypeScript SDK objects.
 * receive returns the normalized events it forwards. reset() starts a new run.
 */
export function createClaudeAdapter(avatar) {
  const send = bridge(avatar);
  let messages = new Map();
  let currentId = null;
  let nextId = 0;
  let turnHasText = false;
  let finished = false;
  const recordFor = id => {
    if (!messages.has(id)) messages.set(id, { streamed: false, snapshots: new Set() });
    return messages.get(id);
  };

  function receive(raw) {
    const message = eventObject(raw);
    const events = [];
    if (!message || message.parent_tool_use_id) return events;

    if (message.type === "system" && message.subtype === "init") {
      messages = new Map();
      currentId = null;
      turnHasText = false;
      finished = false;
      send(events, "thinking");
      return events;
    }
    if (finished) return events;

    if (message.type === "stream_event") {
      const event = message.event || {};
      if (event.type === "message_start") {
        currentId = event.message?.id || `partial-${++nextId}`;
        recordFor(currentId);
        send(events, "thinking");
      } else if (event.type === "content_block_start") {
        const block = event.content_block || {};
        if (block.type === "tool_use") send(events, "working");
        if (block.type === "text" && block.text) {
          recordFor(currentId || "partial").streamed = true;
          turnHasText = true;
          send(events, "delta", block.text);
        }
      } else if (event.type === "content_block_delta") {
        const delta = event.delta || {};
        if (delta.type === "text_delta" && typeof delta.text === "string" && delta.text) {
          recordFor(currentId || "partial").streamed = true;
          turnHasText = true;
          send(events, "delta", delta.text);
        }
        // Thinking text and tool input JSON are deliberately not spoken.
      } else if (event.type === "message_stop") {
        send(events, "done");
      }
    } else if (message.type === "assistant") {
      const body = message.message || {};
      const id = body.id || currentId || `complete-${++nextId}`;
      const record = recordFor(id);
      const blocks = Array.isArray(body.content) ? body.content : [];
      for (const block of blocks) {
        if (block.type === "text" && typeof block.text === "string" && block.text) {
          // With partial messages the assistant snapshot repeats streamed text.
          if (!record.streamed && !record.snapshots.has(block.text)) {
            record.snapshots.add(block.text);
            turnHasText = true;
            send(events, "message", block.text);
          }
        } else if (block.type === "tool_use") {
          send(events, "working");
        }
      }
    } else if (message.type === "user") {
      const blocks = message.message?.content;
      if (Array.isArray(blocks) && blocks.some(block => block.type === "tool_result")) send(events, "thinking");
    } else if (message.type === "tool_progress") {
      send(events, "working");
    } else if (message.type === "result") {
      finished = true;
      if (message.is_error || (message.subtype && message.subtype !== "success")) {
        send(events, "error", "Claude 运行失败，请检查外部进程的错误信息。");
      } else {
        if (!turnHasText && typeof message.result === "string" && message.result) send(events, "message", message.result);
        send(events, "done");
      }
    } else if (message.type === "error") {
      finished = true;
      send(events, "error", "Claude 事件流发生错误。");
    }
    return events;
  }

  receive.reset = () => {
    messages = new Map();
    currentId = null;
    turnHasText = false;
    finished = false;
    avatar.handle({ type: "stop" });
  };
  return receive;
}

/**
 * Translate codex exec --json JSONL. item.completed agent_message is a
 * COMPLETE message, not a token delta. Reasoning and tool results stay silent.
 */
export function createCodexAdapter(avatar) {
  const send = bridge(avatar);
  let spokenIds = new Set();
  let finished = false;
  const workTypes = new Set(["command_execution", "file_change", "mcp_tool_call", "web_search"]);

  function receive(raw) {
    const event = eventObject(raw);
    const events = [];
    if (!event) return events;
    if (event.type === "turn.started") {
      spokenIds = new Set();
      finished = false;
      send(events, "thinking");
      return events;
    }
    if (finished) return events;

    const item = event.item || {};
    if (event.type === "item.started") {
      if (workTypes.has(item.type)) send(events, "working");
      else if (item.type === "reasoning") send(events, "thinking");
    } else if (event.type === "item.completed") {
      if (item.type === "agent_message" && typeof item.text === "string" && item.text) {
        // Without a stable id preserve messages rather than deduplicating text.
        if (!item.id || !spokenIds.has(item.id)) {
          if (item.id) spokenIds.add(item.id);
          send(events, "message", item.text);
        }
      } else if (workTypes.has(item.type)) {
        send(events, "thinking");
      }
    } else if (event.type === "turn.completed") {
      finished = true;
      send(events, "done");
    } else if (event.type === "turn.failed" || event.type === "error") {
      finished = true;
      send(events, "error", "Codex 运行失败，请检查外部进程的错误信息。");
    }
    return events;
  }

  receive.reset = () => {
    spokenIds = new Set();
    finished = false;
    avatar.handle({ type: "stop" });
  };
  return receive;
}
