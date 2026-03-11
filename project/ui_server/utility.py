def set_fall_back(task):
    if not task:
        return False
    task['status'] = 'failed'
    task['category'] = 'error'
    task['title'] = 'Time Limit Exceeded'
    task['save'] = '0'
