ORCHESTRATOR_PLAN_PROMPT = """
 You are a ReAct (Reasoning + Acting) planning agent. Your task is to create a detailed plan for the following task:
{task}

And we have assembled the following team:

{team}


Please follow these steps:
1. Analyze the task
2. Break it down into subtasks.
3. For each subtask, provide simple, actionable steps
4. If needed, use external tools or knowledge sources.
5. status: not_started, completed, in_progress
6. Choose an executor from the list:{names}

Please output an answer in pure JSON format according to the following schema. The JSON object must be parsable as-is. DO NOT OUTPUT ANYTHING OTHER THAN JSON, AND DO NOT DEVIATE FROM THIS SCHEMA. РЕЗУЛЬТАТЫ ПИШИ НА РУССКОМ ЯЗЫКЕ:
{{
    "analysis": string,
    "subtasks": [
        {{
            "name": string,
            "steps": [string, string, ...],
            "status": string,
            "executor":string
        }},
        ...
    ],
}}
РЕЗУЛЬТАТЫ ПИШИ НА РУССКОМ ЯЗЫКЕ
"""
ORCHESTRATOR_SUBTASK_EXECUTE_PROMPT = """
We are working to address the following user request:
**{task}**
Task description:
{description}

To solve the task, we follow the plan, here is the next point of the plan. 

{subtask}

Please complete this step by following the following steps:
{steps}
"""

ORCHESTRATOR_SUMMARY_PROMPT = """
View the history of the task and organically organize the answers into a common text, DO NOT SHORTEN.
Let me remind you that we are solving the following task:  {task}

"""
