def calculate_sum(numbers):
    """
    Calculates the sum of a list of numerical values.

    Args:
        numbers (list): A list of numerical values (integers or floats).

    Returns:
        (int or float): The sum of the numbers in the list.
    """
    return sum(numbers)

if __name__ == "__main__":
    # Example usage:
    list1 = [1, 2, 3, 4, 5]
    print(f"The sum of {list1} is: {calculate_sum(list1)}")

    list2 = [10.5, 20.5, 30.0]
    print(f"The sum of {list2} is: {calculate_sum(list2)}")

def calculate_difference(numbers):
    """
    Calculates the difference of a list of numerical values (first element minus subsequent ones).

    Args:
        numbers (list): A list of numerical values (integers or floats).

    Returns:
        (int or float): The difference of the numbers in the list.
    """
    if not numbers:
        return 0  # Or raise an error, depending on desired behavior for empty list
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    return result

def calculate_product(numbers):
    """
    Calculates the product of a list of numerical values.

    Args:
        numbers (list): A list of numerical values (integers or floats).

    Returns:
        (int or float): The product of the numbers in the list.
    """
    if not numbers:
        return 1  # Product of an empty set is 1
    result = 1
    for num in numbers:
        result *= num
    return result

def calculate_quotient(numbers):
    """
    Calculates the quotient of a list of numerical values (first element divided by subsequent ones).

    Args:
        numbers (list): A list of numerical values (integers or floats).

    Returns:
        (int or float): The quotient of the numbers in the list.

    Raises:
        ValueError: If division by zero is attempted.
    """
    if not numbers:
        return 0  # Or raise an error
    if len(numbers) == 1:
        return numbers[0]
    result = numbers[0]
    for num in numbers[1:]:
        if num == 0:
            raise ValueError("Cannot divide by zero")
        result /= num
    return result


    list3 = []
    print(f"The sum of {list3} is: {calculate_sum(list3)}")

    list4 = [-1, -2, 5]
    print(f"The sum of {list4} is: {calculate_sum(list4)}")
    # New features demonstration:
    list5 = [10, 2, 3]
    print(f"The difference of {list5} is: {calculate_difference(list5)}")

    list6 = [2, 3, 4]
    print(f"The product of {list6} is: {calculate_product(list6)}")

    list7 = [100, 2, 5]
    print(f"The quotient of {list7} is: {calculate_quotient(list7)}")

    list8 = [10]
    print(f"The difference of {list8} is: {calculate_difference(list8)}")
    print(f"The product of {list8} is: {calculate_product(list8)}")
    print(f"The quotient of {list8} is: {calculate_quotient(list8)}")

    # Test empty lists
    list_empty = []
    print(f"The difference of {list_empty} is: {calculate_difference(list_empty)}")
    print(f"The product of {list_empty} is: {calculate_product(list_empty)}")
    print(f"The quotient of {list_empty} is: {calculate_quotient(list_empty)}")

    # Test division by zero
    try:
        list_div_zero = [10, 0, 2]
        print(f"The quotient of {list_div_zero} is: {calculate_quotient(list_div_zero)}")
    except ValueError as e:
        print(f"Error: {e}")
