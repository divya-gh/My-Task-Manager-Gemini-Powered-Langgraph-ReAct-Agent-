### define a functiont o extract information for observability

# extract toolcall information from spy.toolcalls
def extract_tool_info(tool_calls_list , schema_name):
    ''' Extract tool information from apy.tool_Calls for observability
        Args:
            tool_calls: List of tool calls from the model
            schema_name: Name of the schema tool (e.g., "Memory", "ToDo", "Profile") '''
    docs= []
    for tool_call in tool_calls_list:
        for call in tool_call:
            if call['name'] == 'PatchDoc':
                doc = f"""Json patch applied:
                - Memory_document id: {call['args']['json_doc_id']}.. updated
                - Planned_content: {call['args']['planned_edits']} .. created
                - Acutal_content: {call['args']['patches'][0].get('value',None)}..applied\n\n"""
                docs.append(doc+"-"*30)
            elif call['name'] == schema_name:
                doc = f"""New {schema_name} created:
                      - New_memory: {call['args']}\n\n"""
                docs.append(doc+"-"*30)

    return docs 

