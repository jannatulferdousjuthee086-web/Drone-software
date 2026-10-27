
# ==========================================
# 1. IMPORTS AND SETTINGS
# ==========================================

import heapq
from collections import deque

graph = {
    "Warehouse": [("A", 3, True), ("B", 5, True)],
    "A": [("Warehouse", 3, True), ("B", 2, True), ("C", 4, True)],
    "B": [("Warehouse", 5, True), ("A", 2, True),
          ("C", 1, True), ("D", 4, True)],
    "C": [("A", 4, True), ("B", 1, True),
          ("D", 2, True), ("E", 5, True)],
    "D": [("B", 4, True), ("C", 2, True), ("E", 2, True)],
    "E": [("C", 5, True), ("D", 2, True)]
}

locations = ["Warehouse", "A", "B", "C", "D", "E"]
battery_range = 10


# ==========================================
# 2. LINKED LIST
# ==========================================

class Node:
    def __init__(self, package):
        self.package = package
        self.next = None


class PackageList:
    def __init__(self):
        self.head = None

    # Add a package
    def add(self, package):
        new_node = Node(package)

        if self.head is None:
            self.head = new_node
            return

        current = self.head

        while current.next is not None:
            current = current.next

        current.next = new_node

    # Search a package by ID
    def search(self, package_id):
        current = self.head

        while current is not None:
            if current.package["id"] == package_id:
                return current.package

            current = current.next

        return None

    # Get all packages
    def get_all(self):
        all_packages = []
        current = self.head

        while current is not None:
            all_packages.append(current.package)
            current = current.next

        return all_packages

    # Display all packages
    def display(self):
        all_packages = self.get_all()

        if not all_packages:
            print("No packages found.")
            return

        print("\n========== ALL PACKAGES ==========")

        for package in all_packages:
            print("----------------------------------")
            print("Package ID:", package["id"])
            print("Customer:", package["customer"])
            print("Destination:", package["destination"])
            print("Weight:", package["weight"], "kg")
            print("Priority:", package["priority"])
            print("Status:", package["status"])

        print("----------------------------------")


# Create the package list
packages = PackageList()


# ==========================================
# 3. DELIVERY QUEUES
# ==========================================

normal_queue = deque()
urgent_queue = []
order_number = 0


# ==========================================
# 4. SHORTEST SAFE ROUTE - DIJKSTRA
# ==========================================

def find_shortest_route(destination):
    distance = {place: float("inf") for place in locations}
    parent = {place: None for place in locations}

    distance["Warehouse"] = 0
    route_queue = [(0, "Warehouse")]

    while route_queue:
        current_distance, current = heapq.heappop(route_queue)

        if current_distance > distance[current]:
            continue

        if current == destination:
            break

        for neighbor, road_distance, safe in graph[current]:
            if not safe:
                continue

            new_distance = current_distance + road_distance

            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                parent[neighbor] = current

                heapq.heappush(
                    route_queue, (new_distance, neighbor)
                )

    if distance[destination] == float("inf"):
        return None, float("inf")

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()

    return path, distance[destination]


# ==========================================
# 5. ADD A NEW PACKAGE
# ==========================================

def add_package():
    package_id = input("Enter package ID: ").strip()

    if not package_id:
        print("Package ID cannot be empty.")
        return

    if packages.search(package_id) is not None:
        print("This package ID already exists.")
        return

    customer = input("Enter customer name: ").strip()

    if not customer:
        print("Customer name cannot be empty.")
        return

    print("Available destinations:", locations[1:])
    destination = input("Enter destination: ").strip().upper()

    if destination not in locations[1:]:
        print("Invalid destination.")
        return

    try:
        weight = float(input("Enter package weight (kg): "))
        priority = int(
            input("Priority (1=Normal, 2=Urgent, 3=Emergency): ")
        )

        if weight <= 0:
            print("Weight must be greater than zero.")
            return

        if priority not in [1, 2, 3]:
            print("Priority must be 1, 2 or 3.")
            return

    except ValueError:
        print("Please enter valid numbers.")
        return

    package = {
        "id": package_id,
        "customer": customer,
        "destination": destination,
        "weight": weight,
        "priority": priority,
        "status": "Pending"
    }

    packages.add(package)

    print("Package added successfully.")
    print("Delivery Status: Pending")


# ==========================================
# 6. SEARCH FOR A PACKAGE
# ==========================================

def search_package():
    package_id = input("Enter package ID to search: ").strip()
    package = packages.search(package_id)

    if package is None:
        print("Package not found.")
        return

    print("\nPackage found:")
    print("Package ID:", package["id"])
    print("Customer:", package["customer"])
    print("Destination:", package["destination"])
    print("Weight:", package["weight"], "kg")
    print("Priority:", package["priority"])
    print("Status:", package["status"])


# ==========================================
# 7. SORT PACKAGES
# ==========================================

def sort_packages():
    all_packages = packages.get_all()

    if not all_packages:
        print("No packages available.")
        return

    print("1. Sort by Package ID")
    print("2. Sort by Delivery Distance")

    choice = input("Choose sorting method: ").strip()

    if choice == "1":
        sorted_packages = sorted(
            all_packages,
            key=lambda package: package["id"]
        )

    elif choice == "2":

        def get_distance(package):
            path, distance = find_shortest_route(
                package["destination"]
            )

            if path is None:
                return float("inf")

            return distance

        sorted_packages = sorted(
            all_packages,
            key=get_distance
        )

    else:
        print("Invalid choice.")
        return

    print("\n========== SORTED PACKAGES ==========")

    for package in sorted_packages:
        path, distance = find_shortest_route(
            package["destination"]
        )

        if path is None:
            distance_text = "No safe route"
        else:
            distance_text = str(distance) + " km"

        print(
            "ID:", package["id"],
            "| Destination:", package["destination"],
            "| Distance:", distance_text,
            "| Status:", package["status"]
        )

# ==========================================
# 8. ADD A DELIVERY REQUEST
# ==========================================

def add_delivery_request():
    global order_number

    package_id = input("Enter package ID: ").strip()
    package = packages.search(package_id)

    if package is None:
        print("Package not found. Add the package first.")
        return

    if package["status"] != "Pending":
        print("This package is not pending.")
        return

    if package["priority"] == 1:
        normal_queue.append(package_id)
        print("Added to normal FIFO queue.")

    else:
        order_number += 1

        heapq.heappush(
            urgent_queue,
            (-package["priority"], order_number, package_id)
        )

        print("Added to priority queue.")

    package["status"] = "Queued"
    print("Delivery Status: Queued")


# ==========================================
# 9. PROCESS THE NEXT DELIVERY
# ==========================================

def process_delivery():
    if urgent_queue:
        _, _, package_id = heapq.heappop(urgent_queue)

    elif normal_queue:
        package_id = normal_queue.popleft()

    else:
        print("No delivery requests available.")
        return

    package = packages.search(package_id)

    if package is None:
        print("Package not found.")
        return

    destination = package["destination"]
    path, distance = find_shortest_route(destination)

    print("\n========== DELIVERY REPORT ==========")
    print("Package ID:", package_id)
    print("Customer:", package["customer"])
    print("Destination:", destination)

    if path is None:
        package["status"] = "Pending"
        print("No safe route available.")
        print("Delivery Status: Pending")
        print("Fix the route, then add the request again.")
        return

    print("Selected Route:", " -> ".join(path))
    print("Total Distance:", distance, "km")
    print("Battery Range:", battery_range, "km")

    if path[-1] != destination:
        package["status"] = "Pending"
        print("Destination check failed.")
        print("Delivery Status: Pending")
        return

    print("Destination Check: Correct")

    if distance > battery_range:
        package["status"] = "Pending"
        print("Battery Check: Failed")
        print("Delivery Status: Pending")
        print("Increase battery range, then add the request again.")
        return

    print("Battery Check: Passed")

    package["status"] = "Delivered"
    print("Delivery Status: Delivered")
    print("Delivery Successful (Simulated).")
    print("=====================================")


# ==========================================
# 10. CHANGE WEATHER AND ROAD SAFETY
# ==========================================

def change_weather():
    print("Available locations:", locations)

    source = input("Enter starting location: ").strip().title()
    destination = input("Enter connected location: ").strip().title()

    if source not in graph or destination not in graph:
        print("Invalid location.")
        return

    for index, road in enumerate(graph[source]):
        neighbor, distance, safe = road

        if neighbor == destination:
            print("1. Safe weather")
            print("2. Unsafe weather")

            choice = input("Choose weather condition: ").strip()

            if choice not in ["1", "2"]:
                print("Invalid choice.")
                return

            new_safe = (choice == "1")

            graph[source][index] = (
                neighbor, distance, new_safe
            )

            for reverse_index, reverse_road in enumerate(
                graph[destination]
            ):
                reverse_neighbor, reverse_distance, _ = reverse_road

                if reverse_neighbor == source:
                    graph[destination][reverse_index] = (
                        reverse_neighbor, reverse_distance, new_safe
                    )
                    break

            print("Weather condition updated.")
            print("Connection:", source, "<->", destination)
            print("Route Safety:", "Safe" if new_safe else "Unsafe")
            return

    print("These locations are not directly connected.")


# ==========================================
# 11. CHANGE BATTERY RANGE
# ==========================================

def change_battery():
    global battery_range

    try:
        new_range = float(
            input("Enter drone battery range in km: ")
        )

        if new_range <= 0:
            print("Battery range must be positive.")
            return

        battery_range = new_range
        print("Battery range updated to", battery_range, "km.")

    except ValueError:
        print("Enter a valid number.")


# ==========================================
# 12. FIND A ROUTE AND CHECK BATTERY
# ==========================================

def find_route():
    destination = input("Enter destination: ").strip().upper()

    if destination not in locations[1:]:
        print("Invalid destination.")
        return

    path, distance = find_shortest_route(destination)

    if path is None:
        print("No safe route available.")
        return

    print("Shortest safe route:", " -> ".join(path))
    print(
        "Destination Check:",
        "Correct" if path[-1] == destination else "Incorrect"
    )
    print("Distance:", distance, "km")
    print("Battery Range:", battery_range, "km")

    if distance <= battery_range:
        print("Battery Check: Feasible")
    else:
        print("Battery Check: Not feasible")


# ==========================================
# 13. MAIN MENU
# ==========================================

def main():
    while True:
        print("\n====== DRONE DELIVERY ROUTE OPTIMIZER ======")
        print("1. Add Package")
        print("2. Add Delivery Request")
        print("3. Process Next Delivery")
        print("4. Display All Packages")
        print("5. Search Package")
        print("6. Sort Packages")
        print("7. Change Weather Condition")
        print("8. Change Battery Range")
        print("9. Find Shortest Safe Route")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_package()

        elif choice == "2":
            add_delivery_request()

        elif choice == "3":
            process_delivery()

        elif choice == "4":
            packages.display()

        elif choice == "5":
            search_package()

        elif choice == "6":
            sort_packages()

        elif choice == "7":
            change_weather()

        elif choice == "8":
            change_battery()

        elif choice == "9":
            find_route()

        elif choice == "0":
            print("Thank you for using the system.")
            break

        else:
            print("Invalid choice. Try again.")


# ==========================================
# 14. START THE PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
