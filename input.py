# 1. example of moving objects on the table and the shelf
def text(scenario_name):
    # 1. example of moving objects on the table and the shelf
    if scenario_name == 'shelf':
        environment = {
            "assets": [
                "<table>",
                "<shelf_bottom>",
                "<shelf_top>",
                "<trash_bin>",
                "<floor>"],
            "asset_states": {
                "<shelf_bottom>": "on_something(<table>)",
                "<trash_bin>": "on_something(<floor>)"},
            "objects": [
                "<spam>",
                "<juice>"],
            "object_states": {
                "<spam>": "on_something(<table>)",
                "<juice>": "on_something(<shelf_bottom>)"}}
        instructions = ['Put the juice on top of the shelf',
                        'Throw away the spam into the trash bin',
                        'Move the juice on top of the table',
                        'Throw away the juice']
    # 2. example of opening and closing the fridge, and putting the juice on
    # the floor
    elif scenario_name == 'fridge':
        environment = {
            "assets": [
                "<fridge>",
                "<floor>"],
            "asset_states": {
                "<fridge>": "on_something(<floor>)"},
            "objects": [
                "<fridge_handle>",
                "<juice>"],
            "object_states": {
                "<fridge_handle>": "closed()",
                "<juice>": "inside_something(<fridge>)"}}
        instructions = ['Open the fridge half way',
                        'Open the fridge wider',
                        'Take the juice in the fridge and put it on the floor',
                        'Close the fridge']
    # 3. example of opening and closing the drawer
    elif scenario_name == 'drawer':
        environment = {"assets": ["<drawer>", "<floor>"],
                       "asset_states": {"<drawer>": "on_something(<floor>)"},
                       "objects": ["<drawer_handle>"],
                       "object_states": {"<drawer_handle>": "closed()"}}
        instructions = ['Open the drawer widely',
                        'Close the drawer half way',
                        'Close the drawer fully']
    # 4. example of wiping the table
    elif scenario_name == 'table':
        environment = {
            "assets": [
                "<table1>",
                "<table2>",
                "<trash_bin>",
                "<floor>"],
            "asset_states": {
                "<table1>": "next_to(<table2>)",
                "<trash_bin>": "on_something(<floor>)"},
            "objects": ["<sponge>"],
            "object_states": {
                "<sponge>": "on_something(<table1>)"}}
        instructions = ['Put the sponge on the table2',
                        'Wipe the table2 with the sponge']
    # 5. example of wiping the window
    elif scenario_name == 'window':
        environment = {
            "assets": [
                "<table>",
                "<window>",
                "<trash_bin>",
                "<floor>"],
            "asset_states": {
                "<table>": "next_to(<window>)",
                "<trash_bin>": "on_something(<floor>)"},
            "objects": ["<sponge>"],
            "object_states": {
                "<sponge>": "on_something(<table>)"}}
        instructions = [
            'Get the sponge from the table and wipe the window with it. After that, put the sponge back on the table',
            'Throw away the sponge on the table']
    return environment, instructions
