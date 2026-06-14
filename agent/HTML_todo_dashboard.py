
import datetime

def render_html_dashboard(user_id: str, store_memory):
    namespace = ("ToDo", str(user_id))
    tasks = store_memory.search(namespace)

    if not tasks:
        # Return simple HTML; Streamlit will render it
        return "<h3>No tasks found.</h3>"

    cards_html = ""

    for m in tasks:
        t = m.value

        task = t.get("task", "Untitled Task")
        status = t.get("status", "unknown")
        deadline = t.get("deadline", None)
        instruction = t.get("instruction", "")
        desired_solution = t.get("desired_solution", "")
        time_taken = t.get("time_taken", None)

        status_color = {
            "completed": "#4CAF50",
            "in progress": "#FFC107",
            "not started": "#F44336"
        }.get(status.lower(), "#9E9E9E")

        if deadline:
            try:
                d = datetime.datetime.fromisoformat(deadline)
                deadline_fmt = d.strftime("%b %d, %Y")
            except:
                deadline_fmt = deadline
        else:
            deadline_fmt = "None"

        cards_html += f"""
        <div class="task-card">
            <div class="task-header">
                <span class="task-title">{task}</span>
                <span class="task-status" style="background:{status_color}">{status}</span>
            </div>

            <div class="task-body">
                <p><b>Deadline:</b> {deadline_fmt}</p>
                <p><b>Time Taken:</b> {time_taken}</p>
                <p><b>Instruction:</b> {instruction}</p>
                <p><b>Desired Solution:</b> {desired_solution}</p>
            </div>
        </div>
        """

    html_page = f"""
    <style>
        .task-container {{
            font-family: system-ui, sans-serif;
            margin: 1rem auto;
            max-width: 900px;
        }}
        .task-title {{
            font-size: 1.2rem;
            font-weight: 600;
        }}
        .task-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #fafafa;
        }}
        .task-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: .5rem;
        }}
        .task-status {{
            padding: .3rem .6rem;
            border-radius: 6px;
            color: white;
            font-size: .8rem;
            text-transform: capitalize;
        }}
        .task-body p {{
            margin: .3rem 0;
        }}
    </style>

    <div class="task-container">
        <h2>📝 Task Dashboard</h2>
        {cards_html}
    </div>
    """

    return html_page



