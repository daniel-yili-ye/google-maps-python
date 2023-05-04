def qs_constructor(destinations, base_url, directories, plan_output):
    solution = [destinations[i] for i in plan_output]
    
    solution_url = directories[:2] + solution # + directories[-2:-1]
    solution_url = [base_url, *solution_url]
    solution_url = "/".join(solution_url)
    return solution_url

# destinations = ["Blue Mountains, Australia", 
#                 "Uluru, Petermann NT 0872 Australia", 
#                 "Canberra Australian Capital Territory, Australia", 
#                 "Kakadu, Northern Territory 0822 Australia"]
# base_url = "https://google.com"
# directories = ["maps", "dir"]
# plan_output = [0, 2, 1, 3]

# print(qs_constructor(destinations, base_url, directories, plan_output))