from api import User
if __name__ == "__main__":
    cookie = ""
    me = User(cookie=cookie)
    me.print_courses()
    # find the best course configuration
    configs = me.find_best_configurations()
    for (i, config) in enumerate(configs):
        names = []
        for course in config:
            names.append(course.code)
        print(f"Config {i} :", names)
    # try to select
    config_id = int(input('Which configuration to select (default 0): ').strip() or 0)
    for course in configs[config_id]:
        response = me.select(course)
        if response.status_code == 200:
            print(course.code, response.status_code, "✓")

    

