#!/usr/bin/env python3
import sys, os, json, time
ev=sys.argv[1] if len(sys.argv)>1 else '?'
here=os.path.dirname(os.path.abspath(__file__))
try:
    d=json.loads(sys.stdin.read() or '{}')
except Exception as e:
    d={'_erro':str(e)}
rec={'ev':ev,'t':time.time(),'stdin_keys':sorted(d.keys()),'session_id':d.get('session_id'),'transcript_path':d.get('transcript_path'),'cwd':d.get('cwd'),
     'hook_event_name':d.get('hook_event_name'),'tool_name':d.get('tool_name'),'cmd':(d.get('tool_input') or {}).get('command'),'reason':d.get('reason'),
     'env':{k:os.environ.get(k) for k in ('CLAUDE_CODE_SESSION_ID','CLAUDE_EFFORT','CLAUDE_CONFIG_DIR','MAESTRI_TERMINAL_ID','TG_FRENTE','TG_NOME')}}
fd=os.open(os.path.join(here,'eventos.jsonl'),os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o644); os.write(fd,(json.dumps(rec)+'\n').encode()); os.close(fd)
modo=os.environ.get('SONDA_MODO','normal')
if ev=='prompt':
    if modo=='block':
        print(json.dumps({"decision":"block","reason":"SONDA-TG-BLOCK-7731"})); sys.exit(0)
    print('SONDA-TG-CTX-7731 (contexto injetado pelo hook UserPromptSubmit do --settings)')
elif ev=='pre_bash':
    if 'SONDA_DENY' in (rec['cmd'] or ''):
        print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"SONDA-TG-DENY-7731"}}))
sys.exit(0)
