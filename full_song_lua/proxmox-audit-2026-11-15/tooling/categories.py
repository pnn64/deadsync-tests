"""Classify observed failures without matching command-line timeout arguments."""
def failure_category(stage,result,log):
    message=log.lower();journal=result.get('service_tail','').lower()
    if any(term in message+' '+journal for term in ['oom-kill','out of memory','memory allocation','oom killed']):return stage+'_resource_limit'
    if ('timed out' in message or 'did not write a semantic trace within ' in message
        or "result 'timeout'" in journal or 'runtime limit exceeded' in journal):return stage+'_timeout'
    if stage=='capture':
        if 'no stepstype_' in message or 'loaded no charts' in message:return 'no_selectable_chart'
        if 'cannot open' in message or 'no such file' in message:return 'native_missing_input'
        if 'crash' in message:return 'native_crash'
        if 'exited with' in message:return 'native_process_exit'
        return 'native_capture_error'
    return stage+'_error'

def classify_result(result):
    if result['stages'].get('capture',{}).get('exit'):
        result['recorded_worker_status']=result['status']
        result['status']=failure_category('capture',result['stages']['capture'],result.get('reason',''))
        errors=[error for fact in result.get('native_failure',[]) for error in fact.get('errors',[]) if error.get('kind')=='error']
        dropped={key:value for fact in result.get('native_failure',[]) for key,value in fact.get('summary',{}).items()
                 if key.startswith('dropped_') and isinstance(value,(int,float)) and value}
        result['capture_constraints']={'resource_limit':result['status']=='capture_resource_limit','dropped_observations':dropped}
        if errors:result['status']='native_lua_error'
        elif dropped:result['status']='capture_resource_and_observation_limit' if result['capture_constraints']['resource_limit'] else 'capture_observation_limit'
        if result.get('external_native_crash'):result['status']='native_crash'
        debugger=result.get('native_hang_debugger','')
        if 'RunCrashHandler' in debugger and 'malloc_printerr' in debugger and '__libc_fork' in debugger:
            result['status']='native_crash_handler_hang'
        result['classification_version']=3
    return result
