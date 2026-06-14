# agent/HTML_patch_viewer.py

import html

def render_patch_html(patches):
    """
    patches: list of tool call dictionaries from TrustCall spy
    Returns: HTML string for Streamlit
    """

    if not patches:
        return "<h3>No patches found.</h3>"

    cards = ""

    for tool_call_list in patches:
        for call in tool_call_list:

            name = call.get("name", "")
            args = call.get("args", {})

            # -------------------------
            # PatchDoc (JSON Patch)
            # -------------------------
            if name == "PatchDoc":
                json_id = args.get("json_doc_id", "unknown")
                planned = html.escape(str(args.get("planned_edits", [])))
                applied = html.escape(str(args.get("patches", [])))

                cards += f"""
                <div class="patch-card">
                    <div class="patch-header">
                        <span class="patch-type">PatchDoc</span>
                        <span class="patch-id">ID: {json_id}</span>
                    </div>

                    <div class="patch-body">
                        <p><b>Planned Edits:</b></p>
                        <pre>{planned}</pre>

                        <p><b>Applied Patches:</b></p>
                        <pre>{applied}</pre>
                    </div>
                </div>
                """

            # -------------------------
            # Schema creation (UserProfile, ToDo, Instructions)
            # -------------------------
            else:
                value = html.escape(str(args))
                cards += f"""
                <div class="patch-card">
                    <div class="patch-header">
                        <span class="patch-type">{name}</span>
                        <span class="patch-id">New Memory</span>
                    </div>

                    <div class="patch-body">
                        <p><b>Value:</b></p>
                        <pre>{value}</pre>
                    </div>
                </div>
                """

    # -------------------------
    # Final HTML Page
    # -------------------------
    html_page = f"""
    <style>
        .patch-container {{
            font-family: system-ui, sans-serif;
            margin: 1rem auto;
            max-width: 900px;
        }}
        .patch-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #fafafa;
        }}
        .patch-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: .5rem;
        }}
        .patch-type {{
            font-weight: 600;
            color: #1f6feb;
        }}
        .patch-id {{
            font-size: .8rem;
            color: #555;
        }}
        pre {{
            background: #fff;
            padding: .5rem;
            border-radius: 6px;
            border: 1px solid #eee;
            overflow-x: auto;
        }}
    </style>

    <div class="patch-container">
        <h2>🔍 Patch Viewer</h2>
        {cards}
    </div>
    """

    return html_page
