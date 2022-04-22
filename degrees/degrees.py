import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Breadth first search algorithm
    solution_path = []
    # 1. Create a frontier for our search algorithm
    frontier = QueueFrontier()
    # 2. Create an 'explored' set
    explored_nodes = set()
    # 3. Add the source as a node to the frontier
    frontier.add(Node(source, None, None))
    
    # Start the Search
    while True:
        # 4. Check if frontier is empty; if so, return no solution
        if frontier.empty():
            return None

        # 5. Expand a node from the frontier
        current_node = frontier.remove()

        # 6. Check if current node is the solution
        persons = []
        movies = []
        if current_node.state == target:
            # 6a. If so, build the solution path in reverse
            while current_node.parent is not None:
                persons.append(current_node.state)
                movies.append(current_node.action)
                current_node = current_node.parent
            # Reverse the list of persons and movies
            persons.reverse()
            movies.reverse()

            # 6b. Add the states and actions to the solution path
            for i in range(len(persons)):
                solution_path.append((movies[i], persons[i]))
            
            # 6c. Return the solution path
            return solution_path

        # 7. Add the explored state to the explored set
        explored_nodes.add(current_node.state)    

        # 8. If not solution, check neighbors
        for movie, person in neighbors_for_person(current_node.state):
            # 8a. Check if the neighbor is the target person; if so, return the solution path
            if person == target:
                while current_node.parent is not None:
                    persons.append(current_node.state)
                    movies.append(current_node.action)
                    current_node = current_node.parent
                persons.reverse()
                movies.reverse()

                for i in range(len(persons)):
                    solution_path.append((movies[i], persons[i]))
                
                # Append the current neighbor to the solution_path
                solution_path.append((movie, person))

                return solution_path

            # 8b. Otherwise, create a new node for each neighbor only if not explored yet and not in the frontier
            if person not in explored_nodes and not frontier.contains_state(person):
                frontier.add(Node(person, current_node, movie))

        # 9. Repeat until we find a solution

    # raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
