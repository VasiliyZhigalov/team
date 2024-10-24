def get_plan(plan):
    result_str = ("**План**\n \n **Oписание**\n") + plan["analysis"] + "\n\n"
    i = 1
    for task in plan['subtasks']:
        result_str += f"\n**{i}. {task["name"]}** \n"
        for step in task['steps']:
            result_str += f"  -{step} \n \n"
        i += 1
    return result_str


def get_subtask_to_worker(worker, subtask, steps):
    result_str = f'**Задача:** \n \n  {subtask} \n\n **Шаги**: \n\n '
    for step in steps:
        result_str += f"  -{step} \n \n"
    return result_str
