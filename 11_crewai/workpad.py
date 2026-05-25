from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find latest AI app trends",
    backstory="Expert tech researcher"
)

writer = Agent(
    role="Writer",
    goal="Write engaging blog posts",
    backstory="Senior content writer"
)

task1 = Task(
    description="Research React Native AI apps",
    agent=researcher
)

task2 = Task(
    description="Write blog using research",
    agent=writer
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2]
)

result = crew.kickoff()
print(result)